#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
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

    if options.server:
        from tourbillon.server.app import TourBillonServer
        app = TourBillonServer(cfg)
    else:
        try:
            import wx
        except ImportError:
            logger.critical("wxPython est requis pour lancer ce programme en mode graphique")

        from tourbillon.gui.app import TourBillonGUI
        app = TourBillonGUI(cfg)

    if options.filename:
        app.load(options.filename)

    app.run()


if __name__ == '__main__':
    run()
