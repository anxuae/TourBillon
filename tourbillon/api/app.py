# -*- coding: UTF-8 -*-

"""FastAPI application factory."""

import os.path as osp
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import tourbillon
from .routers import ROUTERS
from ..settings import Settings
from .state import init_state

# Location of the built web frontend (served in production if present).
# The Vue SPA lives in the sibling ``tourbillon-ui`` folder at the repo root.
WEB_DIR = osp.join(
    osp.dirname(osp.dirname(osp.dirname(__file__))), "tourbillon-ui", "dist"
)


def create_app(settings=None):
    """Create and configure the TourBillon FastAPI application.

    Settings are loaded once here (at startup) and saved once on shutdown, so
    the settings module is the only place that persists configuration.

    :param settings: optional :class:`Settings` instance
    """
    if settings is None:
        settings = Settings.load()

    init_state(settings)

    @asynccontextmanager
    async def lifespan(_app):
        # Startup: settings are already loaded above.
        yield
        # Shutdown: persist the settings (including draw options).
        settings.save()

    app = FastAPI(
        title="TourBillon",
        description="Swiss-system tournament manager for the Billon game.",
        version=tourbillon.__version__,
        lifespan=lifespan,
    )

    for router in ROUTERS:
        app.include_router(router)

    @app.get("/api/health", tags=["health"])
    def health():
        """Simple health check."""
        return {"status": "ok"}

    @app.get("/api/version", tags=["about"])
    def version():
        """Return the application name and version (for the About window)."""
        return {"name": tourbillon.__long_name__, "version": tourbillon.__version__}

    # Serve the built Vue SPA if it exists. The client router handles the
    # /admin, /display and /history routes (history mode).
    if osp.isdir(WEB_DIR):
        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="ui")

    return app
