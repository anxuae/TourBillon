# -*- coding: UTF-8 -*-

"""Application state shared across API requests.

Holds the current tournament, an :class:`asyncio.Lock` guarding writes, and a
simple pub/sub hub used to broadcast draw progress and live score updates over
WebSocket.
"""

import asyncio


class ProgressHub:
    """Fan-out of progress/update events to connected WebSocket clients."""

    def __init__(self):
        self._subscribers = set()

    def subscribe(self):
        """Register a new subscriber and return its queue."""
        queue = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue):
        """Remove a subscriber queue."""
        self._subscribers.discard(queue)

    async def publish(self, event):
        """Push an event (dict) to every subscriber."""
        for queue in list(self._subscribers):
            await queue.put(event)


class AppState:
    """Container for the current tournament and its concurrency primitives."""

    def __init__(self, settings):
        self.settings = settings
        self.tournament = None
        self.filename = None
        self.lock = asyncio.Lock()
        self.progress = ProgressHub()

    def require_tournament(self):
        """Return the current tournament or raise if none is loaded."""
        if self.tournament is None:
            raise LookupError("No tournament loaded")
        return self.tournament


# Singleton state, initialised by the application factory.
_state = None


def init_state(settings):
    """Initialise and return the global application state."""
    global _state
    _state = AppState(settings)
    return _state


def get_state():
    """Return the global application state (FastAPI dependency)."""
    if _state is None:
        raise RuntimeError("Application state is not initialised")
    return _state
