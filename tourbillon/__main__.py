#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import os.path as osp

from . import config, logger
from .core import player


def run():
    """
    Entry point.
    """
    # Parse command line options
    options = config.parse_options()

    # Initialize configuration file
    cfg = config.TypedConfigParser(osp.join(os.environ.get('APPDATA', osp.expanduser("~")), '.trb', 'cfg'))

    # Initialize players history
    if cfg.get_path('TOURNOI', 'HISTORIQUE'):
        player.PlayerHistory(cfg.get_path('TOURNOI', 'HISTORIQUE'))
    else:
        player.PlayerHistory(cfg.join_path('hist_jrs'))

    # Configure logging
    if options.logging_level is None:
        if cfg.get_typed('INTERFACE', 'BAVARDE') is True:
            logger.init_logger(logger.DEBUG)
        else:
            logger.init_logger(logger.WARNING)
    else:
        logger.init_logger(options.logging_level)

    if sys.version_info[:3] < (3, 8, 0):
        logger.critical("Python 3.8 (ou supérieure) est requis pour ce programme")

    if options.backend:
        from tourbillon.server.app import TourBillonServer
        app = TourBillonServer(cfg)
    else:
        try:
            import wx
            version = tuple([int(n) for n in wx.__version__.split('.')[:3]])
        except ImportError:
            logger.critical("wxPython est requis pour lancer ce programme en mode graphique")

        if version < (4, 0, 0):
            logger.critical(f"wxPython >= 4.0 est requis (version actuelle: {version})")

        from tourbillon.gui.app import TourBillonGUI
        app = TourBillonGUI(cfg)

    if options.filename:
        app.load(options.filename)

    app.run()


if __name__ == '__main__':
    run()
