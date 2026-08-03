#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""TourBillon entry point.

Launches the FastAPI backend with uvicorn. The legacy wxPython GUI has been
removed; the interface is now fully web based (see ``tourbillon/api`` and the
``web/`` frontends).
"""

import argparse
import copy
import logging
import os

import uvicorn

import tourbillon
from . import logger
from .api.app import create_app
from .settings import Settings, SETTINGS_PATH_ENV


def parse_options():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]",
        description=tourbillon.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=tourbillon.__version__
    )
    parser.add_argument(
        "-c", "--config", dest="config", default=None,
        help="path to a YAML settings file",
    )
    parser.add_argument("--host", dest="host", default=None, help="server host")
    parser.add_argument("--port", dest="port", type=int, default=None, help="server port")
    parser.add_argument(
        "--reload", action="store_true", default=False,
        help="enable auto-reload (development)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbose", dest="logging_level",
        action="store_const", const=logging.DEBUG, default=logging.INFO,
        help="report more information about operations",
    )
    group.add_argument(
        "-q", "--quiet", dest="logging_level",
        action="store_const", const=logging.WARNING,
        help="report only errors and warnings",
    )

    return parser.parse_args()


def run():
    """Entry point: start the TourBillon web server."""
    options = parse_options()

    logger.init_logger(options.logging_level)

    settings = Settings.load(options.config)
    if options.host:
        settings.host = options.host
    if options.port:
        settings.port = options.port

    logger.info("Settings file: %s", settings.path)

    # Let uvicorn keep displaying its own logs, but re-enable propagation so its
    # records also bubble up to the root logger where the execution-summary
    # counter tallies them (see tourbillon.logger).
    log_config = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)
    for cfg in log_config.get("loggers", {}).values():
        cfg["propagate"] = True

    if options.reload:
        # ``--reload`` needs an import string: uvicorn re-imports the app in a
        # child process. Pass the settings file path through the environment so
        # the application factory can rebuild identical settings.
        if options.config:
            os.environ[SETTINGS_PATH_ENV] = options.config
        uvicorn.run(
            "tourbillon.api.app:create_app_from_env",
            factory=True,
            host=settings.host, port=settings.port,
            reload=True, log_config=log_config,
        )
    else:
        app = create_app(settings)
        uvicorn.run(
            app, host=settings.host, port=settings.port,
            log_config=log_config,
        )


if __name__ == "__main__":
    run()
