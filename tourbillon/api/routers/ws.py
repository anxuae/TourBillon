# -*- coding: UTF-8 -*-

"""WebSocket endpoints for real-time draw progress and score updates."""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..state import get_state

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/events")
async def ws_events(websocket: WebSocket):
    """Stream draw progress and live update events to a client."""
    await websocket.accept()
    state = get_state()
    queue = state.progress.subscribe()
    try:
        while True:
            # Race the internal event queue against the raw ASGI receive
            # channel. The server sends a "websocket.disconnect" message on
            # that channel when it closes the connection (client disconnect,
            # or server shutdown e.g. Ctrl+C): without listening for it, this
            # endpoint never notices the closed socket and blocks uvicorn's
            # graceful shutdown until it force-cancels the task.
            get_task = asyncio.ensure_future(queue.get())
            receive_task = asyncio.ensure_future(websocket.receive())
            done, pending = await asyncio.wait(
                {get_task, receive_task}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()

            if receive_task in done:
                message = receive_task.result()
                if message.get("type") == "websocket.disconnect":
                    break
                # This endpoint is push-only: ignore any other client message.
                continue

            await websocket.send_json(get_task.result())
    except (WebSocketDisconnect, asyncio.CancelledError):
        # CancelledError is raised if the server force-cancels the task (e.g.
        # graceful shutdown timeout exceeded): let it propagate after cleanup.
        raise
    finally:
        state.progress.unsubscribe(queue)


