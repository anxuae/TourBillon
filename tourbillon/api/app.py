# -*- coding: UTF-8 -*-

"""FastAPI application factory."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import tourbillon
from .. import logger
from .routers import ROUTERS
from ..settings import Settings, SETTINGS_PATH_ENV
from .state import init_state

# Location of the built web frontend. Prefer the bundled package assets so the
# wheel/sdist works when installed from PyPI; keep a local repo fallback for dev.
# Assets are copied into ``tourbillon/static/dist`` by ``scripts/build-ui.py``
# (the Poetry build hook), so this must match ``pyproject.toml``'s ``include``.
PACKAGE_WEB_DIR = Path(__file__).resolve().parents[1] / "static" / "dist"
DEV_WEB_DIR = Path(__file__).resolve().parents[2] / "tourbillon-ui" / "dist"
WEB_DIR = PACKAGE_WEB_DIR if PACKAGE_WEB_DIR.is_dir() else DEV_WEB_DIR


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
    if WEB_DIR.is_dir():
        if WEB_DIR == PACKAGE_WEB_DIR:
            logger.info("Serving frontend from bundled package assets: %s", WEB_DIR)
        else:
            logger.info("Serving frontend from local dev build: %s", WEB_DIR)
        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="ui")
    else:
        logger.warning("No built frontend found (looked in %s and %s)", PACKAGE_WEB_DIR, DEV_WEB_DIR)

    return app


def create_app_from_env():
    """Application factory used by uvicorn when reloading from an import string.

    ``uvicorn.run(..., reload=True)`` re-imports the app in a child process, so
    it cannot be given the pre-built ``settings`` instance. The settings file
    path is passed through the :data:`SETTINGS_PATH_ENV` environment variable
    instead.
    """
    config = os.environ.get(SETTINGS_PATH_ENV) or None
    return create_app(Settings.load(config))

