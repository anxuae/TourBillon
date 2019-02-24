#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des équipes."""

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

def tirage(type_tirage, equipes_par_manche, statistiques, chapeaux=[], rapport=None):
    if type_tirage not in TIRAGES:
        raise TirageError, u"Categorie de tirage '%s' inconnue." % type_tirage

    # Création thread tirage
    t = TIRAGES[type_tirage].ThreadTirage(equipes_par_manche, statistiques, chapeaux, rapport)

    return t
