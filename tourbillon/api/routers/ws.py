# -*- coding: UTF-8 -*-

"""WebSocket endpoints for real-time draw progress and score updates."""

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
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        state.progress.unsubscribe(queue)
