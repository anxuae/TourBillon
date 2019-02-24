#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """TourBillon est le logiciel officiel de la billonnière utilisé pour
le tournoi de Billon qui a lieu chaque année à Floyon, le premier dimanche d'août."""

import sys, os

__nom__ = u"TourBillon"
__version__ = (5, 0, 2)

if sys.version_info[:3] < (2, 6, 0):
    sys.exit("Python 2.6 (ou supérieure) est requis pour ce programme.")


del sys, os
