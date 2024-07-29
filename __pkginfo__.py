# -*- coding: UTF-8 -*-

import tourbillon

auteur = "La Billonnière"

email = "labillonniere@gmail.fr"

site = "https://www.facebook.com/labillonniere"

licence = "GNU GPL"

nom_python_module = "tourbillon"

nom_dist_package = "TourBillon"

desc_courte = u"TourBillon - by La Billionnière"

desc_longue = \
    u"""TourBillon, est le programme officiel de la Billonnière, utilisé
lors des tournois de billon de printemps (Mai) et d'été (Août).

Ce programme permet de gerer un nombre variable d'équipes lors d'
un tournoi de billon. Deux interfaces sont incluses dans le
package, une interface en ligne de commande et une interface
graphique"""

version = '.'.join([str(num) for num in tourbillon.__version__])

scripts = [
    # (script après install, chemin, fonction à appeler)
    ("tourbillon", "tourbillon/trb.py", "run"), ]

dependences = [  # dist_name + contrainte version
    "pyyaml>=3.0",
    "wxpython>=3.0.0",
    "flask>=1.0.2",
    "flask-restful>=0.3.6"]

ressources = [  # (source, cible, pattern)
    ('', '', ["LICENSE.rst", "LISEZMOI.rst"]),
    ('tourbillon/images', 'images', ["*.png", "*.txt", "*.jpg", "fond/*.png", "fond/*.jpg"])]
