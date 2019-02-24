#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des équipes."""

#--- Import --------------------------------------------------------------------

import sys, os
from tourbillon.trb_core.exceptions import TirageError
from tourbillon.trb_core.tirages import *

#--- Functions -----------------------------------------------------------------

_IGNORE = ['__init__', 'utile']
__dir__ = os.path.abspath(os.path.dirname(__file__))
__modules__ = {}

for root, dirs, fics in os.walk(__dir__):
    for module in fics:
        if module.endswith('.py'):
            module = module.split('.')[0]
            if module not in __modules__ and module not in _IGNORE:
                nom = __package__ + "." + module
                __import__(nom)
                __modules__[module] = sys.modules[nom]

def tirage(module, equipes_par_manche, statistiques, chapeaux = [], rapport = []):
    if module not in __modules__:
        raise TirageError, u"Categorie de tirage '%s' inconnue." % categorie

    # Création thread tirage
    t = __modules__[module].ThreadTirage(equipes_par_manche, statistiques, chapeaux, rapport)

    return t
