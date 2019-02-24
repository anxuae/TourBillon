#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Définitions des équipes."""

#--- Import --------------------------------------------------------------------

import sys, os
import imp
import re
from tourbillon.trb_core.exceptions import TirageError
from tourbillon.trb_core.tirages import aleatoire_ag, niveau_ag, niveau2008_dt

#--- Functions -----------------------------------------------------------------

TIRAGES = {'aleatoire_ag'   :aleatoire_ag,
           'niveau_ag'      :niveau_ag,
           'niveau2008_dt'  :niveau2008_dt}


def tirage(algorithme, equipes_par_manche, statistiques, chapeaux=[], callback=None):
    if algorithme not in TIRAGES:
        raise TirageError(u"Categorie de tirage '%s' inconnue." % algorithme)

    # Création thread tirage
    t = TIRAGES[algorithme].ThreadTirage(equipes_par_manche, statistiques, chapeaux, callback)

    return t
