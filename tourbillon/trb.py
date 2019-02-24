#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Module principale de TourBillon"""

#--- Import --------------------------------------------------------------------

import sys, os

try:
    import tourbillon
except ImportError:
    # Ajouter le package dans sys.path (ici l'utilisation du module inspect
    # et plus robuste que la variable __file__ qui n'est pas toujours définie:
    # par exemple lorqu'on execute le programme avec 'execfile(...)' )
    import inspect
    ce_fichier = inspect.currentframe().f_code.co_filename
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(ce_fichier)), '..'))

from tourbillon.configuration import charger_config, parse_options

try:
# Cela prendra 1 minute ; si psyco n’est pas installé, ça ne changera rien; et si
# psyco est installé, on peut obtenir des gains de performance très considérable
# (probablement de l’ordre de 3-4 fois plus vite – voire 10 ou même plus !)
    import psyco
    psyco.full()
except ImportError:
    pass

#--- Charger la configuration --------------------------------------------------


CONFIG = charger_config()


def run():
    OPTIONS, ARGS = parse_options()

    if not OPTIONS.gui_active:
        from tourbillon.trb_cli.interface import TourBillonCLI
        app = TourBillonCLI(CONFIG)
    else:
        try:
            import wx
            version = tuple(map(int, wx.__version__.split('.')[:3]))
            if  version < (2, 8, 0):
                raise RuntimeError
        except RuntimeError, e:
            sys.exit("wxPython 2.8 (ou supérieur) est requis pour lancer ce programme en mode graphique.")

        from tourbillon.trb_gui.interface import TourBillonGUI
        app = TourBillonGUI(CONFIG)

    if len(ARGS) > 0:
        app.ouvrir(ARGS[0])

    app.MainLoop()

#--- Lancer l'interface utilisateur --------------------------------------------

if __name__ == '__main__':
    run()
