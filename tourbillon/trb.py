#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Module principale de TourBillon"""

#--- Import --------------------------------------------------------------------

import sys, os
# Ajouter le package dans sys.path
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from tourbillon.configuration import (creer_config, charger_config,
                                        parse_options, USERPATH)
from tourbillon.trb_core.exceptions import ConfigError

try :
# Cela prendra 1 minute ; si psyco n’est pas installé, ça ne changera rien; et si
# psyco est installé, on peut obtenir des gains de performance très considérable
# (probablement de l’ordre de 3-4 fois plus vite – voire 10 ou même plus !)
    import psyco
    psyco.full()
except ImportError:
    pass

#--- Charger la configuration --------------------------------------------------

try:
    CONFIG = charger_config()
except ConfigError, e:
    creer_config()
    CONFIG = charger_config()

#--- Lancer l'interface utilisateur --------------------------------------------

if __name__ == '__main__':

    OPTIONS = parse_options()

    if not OPTIONS.gui_active:
        from tourbillon.trb_cli.interface import run
    else:
        try:
            import wx
            version = tuple(map(int, wx.__version__.split('.')[:3]))
            if  version < (2, 8, 0):
                raise RuntimeError
        except:
            sys.exit("wxPython 2.8 (ou supérieur) est requis pour lancer ce programme en mode graphique.")

        from tourbillon.trb_gui.interface import run

    run(CONFIG)
