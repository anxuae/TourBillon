#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Module principal de TourBillon"""

import sys

from tourbillon.config import charger_config, parse_options
from tourbillon import logger


def run():
    """
    Entry point.
    """
    config = charger_config()
    options, args = parse_options()

    # Niveau de log
    verbose = options.verbose
    if verbose is None:
        verbose = config.get_typed('INTERFACE', 'BAVARDE')
    if verbose is True:
        logger.creer_logger(logger.DEBUG)
    elif verbose is False:
        logger.creer_logger(logger.WARNING)
    else:
        logger.creer_logger(logger.INFO)

    if sys.version_info[:3] < (2, 7, 0):
        logger.critical("Python 2.7 (ou supérieure) est requis pour ce programme")

    if options.backend:
        from tourbillon.server.app import TourBillonServer
        app = TourBillonServer(config)
    else:
        try:
            import wx
            version = tuple([int(n) for n in wx.__version__.split('.')[:3]])
        except ImportError:
            logger.critical("wxPython est requis pour lancer ce programme en mode graphique")

        if version < (2, 8, 0):
            logger.critical("wxPython >= 2.8 est requis (version actuelle: %s)" % version)

        from tourbillon.gui.app import TourBillonGUI
        app = TourBillonGUI(config)

    if len(args) > 0:
        app.ouvrir(args[0])

    app.run()


if __name__ == '__main__':
    run()
