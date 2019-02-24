#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """TourBillon est le logiciel officiel de La Billonnière utilisé pour
le tournoi de Billon qui a lieu chaque année à Floyon, le premier dimanche d'août."""

import sys
import os

__version__ = (5, 0, 0)

f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "gpl-3.0.txt"))
__licence__ = f.read()
f.close()

if sys.version_info[:3] < (2, 6, 0):
    sys.exit("Python 2.6 (ou supérieure) est requis pour ce programme.")


del sys, os, f
