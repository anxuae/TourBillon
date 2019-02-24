#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from datetime import datetime, timedelta
from tourbillon.core.constantes import (CHAPEAU, GAGNE, PERDU, FORFAIT)
from tourbillon.core.tournoi import charger_tournoi

#--- Tournoi pour extraction de donnée ----------------------------------------

REF_TOURNOI = charger_tournoi(os.path.join(os.path.dirname(__file__), 'data.yml'))


EQUIPES_PAR_MANCHE = 2
POINTS_PAR_MANCHE = 12
JOUEURS_PAR_EQUIPE = 2

#--- Equipe 1-------------------------------------------------------------------

PARTIES_1 = [{'points': 12, 'etat': GAGNE, 'debut': datetime(2010, 6, 20, 12), 'duree': timedelta(0, 1750), 'adversaires': [4]},
             {'points': 0, 'etat': FORFAIT, 'debut': datetime(2010, 6, 20, 13), 'duree': None, 'adversaires': []},
             {'points': 9, 'etat': PERDU, 'debut': datetime(
                 2010, 6, 20, 14), 'duree': timedelta(0, 1300), 'adversaires': [8]},
             {'points': 12, 'etat': CHAPEAU, 'debut': datetime(2010, 6, 20, 15), 'duree': None, 'adversaires': []},
             {'points': 10, 'etat': PERDU, 'debut': datetime(2010, 6, 20, 16), 'duree': timedelta(0, 2500), 'adversaires': [5]}]


JOUEURS_1 = [("Guillaume", "Cuicui", "27"), ("Thomas", "Rourou", "28")]

# Statistiques après chaque fin de partie
STATISTIQUES_1 = [{'adversaires': [4], 'points': 12, 'chapeaux': 0, 'victoires': 1, 'parties': 1, 'forfaits': 0,
                   'moy_billon': 12.0, 'max_billon': 12, 'min_billon': 12,
                   'moy_duree': timedelta(0, 1750), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1750)},

                  {'adversaires': [4], 'points': 12, 'chapeaux': 0, 'victoires': 1, 'parties': 1, 'forfaits': 1,
                      'moy_billon': 12.0, 'max_billon': 12, 'min_billon': 12,
                      'moy_duree': timedelta(0, 1750), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1750)},

                  {'adversaires': [4, 8], 'points': 21, 'chapeaux': 0, 'victoires': 1, 'parties': 2, 'forfaits': 1,
                      'moy_billon': 10.5, 'max_billon': 12, 'min_billon': 9,
                      'moy_duree': timedelta(0, 1525), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1300)},

                  {'adversaires': [4, 8], 'points': 33, 'chapeaux': 1, 'victoires': 1, 'parties': 3, 'forfaits': 1,
                      'moy_billon': 11.0, 'max_billon': 12, 'min_billon': 9,
                      'moy_duree': timedelta(0, 1525), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1300)},

                  {'adversaires': [4, 8, 5], 'points': 43, 'chapeaux': 1, 'victoires': 1, 'parties': 4, 'forfaits': 1,
                      'moy_billon': 10.75, 'max_billon': 12, 'min_billon': 9,
                      'moy_duree': timedelta(0, 1850), 'max_duree': timedelta(0, 2500), 'min_duree': timedelta(0, 1300)}]

#--- Equipe 2-------------------------------------------------------------------

PARTIES_2 = [{'points': 9, 'etat': PERDU, 'debut': datetime(2010, 6, 20, 12), 'duree': timedelta(0, 1650), 'adversaires': [8]},
             {'points': 12, 'etat': CHAPEAU, 'debut': datetime(2010, 6, 20, 13), 'duree': None, 'adversaires': []},
             {'points': 10, 'etat': PERDU, 'debut': datetime(
                 2010, 6, 20, 14), 'duree': timedelta(0, 1900), 'adversaires': [5]},
             {'points': 9, 'etat': PERDU, 'debut': datetime(
                 2010, 6, 20, 15), 'duree': timedelta(0, 1550), 'adversaires': [4]},
             {'points': 5, 'etat': PERDU, 'debut': datetime(2010, 6, 20, 16), 'duree': timedelta(0, 1050), 'adversaires': [9]}]


JOUEURS_2 = [("Christophe", "Dudu", "35"), ("Christophe", "Rourou", "31")]

# Statistiques après chaque fin de partie
STATISTIQUES_2 = [{'adversaires': [8], 'points': 9, 'chapeaux': 0, 'victoires': 0, 'parties': 1, 'forfaits': 0,
                   'moy_billon': 9.0, 'max_billon': 9, 'min_billon': 9,
                   'moy_duree': timedelta(0, 1650), 'max_duree': timedelta(0, 1650), 'min_duree': timedelta(0, 1650)},

                  {'adversaires': [8], 'points': 21, 'chapeaux': 1, 'victoires': 0, 'parties': 2, 'forfaits': 0,
                      'moy_billon': 10.5, 'max_billon': 12, 'min_billon': 9,
                      'moy_duree': timedelta(0, 1650), 'max_duree': timedelta(0, 1650), 'min_duree': timedelta(0, 1650)},

                  {'adversaires': [8, 5], 'points': 31, 'chapeaux': 1, 'victoires': 0, 'parties': 3, 'forfaits': 0,
                      'moy_billon': 10.33, 'max_billon': 12, 'min_billon': 9,
                      'moy_duree': timedelta(0, 1775), 'max_duree': timedelta(0, 1900), 'min_duree': timedelta(0, 1650)},

                  {'adversaires': [8, 5, 4], 'points': 40, 'chapeaux': 1, 'victoires': 0, 'parties': 4, 'forfaits': 0,
                      'moy_billon': 10.0, 'max_billon': 12, 'min_billon': 9,
                      'moy_duree': timedelta(0, 1700), 'max_duree': timedelta(0, 1900), 'min_duree': timedelta(0, 1550)},

                  {'adversaires': [8, 5, 4, 9], 'points': 45, 'chapeaux': 1, 'victoires': 0, 'parties': 5, 'forfaits': 0,
                      'moy_billon': 9.0, 'max_billon': 12, 'min_billon': 5,
                      'moy_duree': timedelta(0, 1537, 500000), 'max_duree': timedelta(0, 1900), 'min_duree': timedelta(0, 1050)}]

#--- Equipe 4-------------------------------------------------------------------

PARTIES_4 = [{'points': 7, 'etat': PERDU, 'debut': datetime(2010, 6, 20, 12), 'duree': timedelta(0, 1750), 'adversaires': [1]},
             {'points': 13, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 13), 'duree': timedelta(0, 1600), 'adversaires': [5]},
             {'points': 13, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 14), 'duree': timedelta(0, 1450), 'adversaires': [9]},
             {'points': 12, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 15), 'duree': timedelta(0, 1550), 'adversaires': [2]},
             {'points': 8, 'etat': PERDU, 'debut': datetime(2010, 6, 20, 16), 'duree': timedelta(0, 1800), 'adversaires': [8]}]


JOUEURS_4 = [("Jean-Philipe", "Rourou", "22"), ("Erwan", "Rourou", "20")]

# Statistiques après chaque fin de partie
STATISTIQUES_4 = [{'adversaires': [1], 'points': 7, 'chapeaux': 0, 'victoires': 0, 'parties': 1, 'forfaits': 0,
                   'moy_billon': 7.0, 'max_billon': 7, 'min_billon': 7,
                   'moy_duree': timedelta(0, 1750), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1750)},

                  {'adversaires': [1, 5], 'points': 20, 'chapeaux': 0, 'victoires': 1, 'parties': 2, 'forfaits': 0,
                      'moy_billon': 10.0, 'max_billon': 13, 'min_billon': 7,
                      'moy_duree': timedelta(0, 1675), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1600)},

                  {'adversaires': [1, 5, 9], 'points': 33, 'chapeaux': 0, 'victoires': 2, 'parties': 3, 'forfaits': 0,
                      'moy_billon': 11.0, 'max_billon': 13, 'min_billon': 7,
                      'moy_duree': timedelta(0, 1600), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1450)},

                  {'adversaires': [1, 5, 9, 2], 'points': 45, 'chapeaux': 0, 'victoires': 3, 'parties': 4, 'forfaits': 0,
                      'moy_billon': 11.25, 'max_billon': 13, 'min_billon': 7,
                      'moy_duree': timedelta(0, 1587, 500000), 'max_duree': timedelta(0, 1750), 'min_duree': timedelta(0, 1450)},

                  {'adversaires': [1, 5, 9, 2, 8], 'points': 53, 'chapeaux': 0, 'victoires': 3, 'parties': 5, 'forfaits': 0,
                      'moy_billon': 10.6, 'max_billon': 13, 'min_billon': 7,
                      'moy_duree': timedelta(0, 1630), 'max_duree': timedelta(0, 1800), 'min_duree': timedelta(0, 1450)}]

#--- Equipe 5-------------------------------------------------------------------

PARTIES_5 = [{'points': 12, 'etat': GAGNE, 'debut': datetime(2010, 6, 20, 12), 'duree': timedelta(0, 1450), 'adversaires': [9]},
             {'points': 12, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 13), 'duree': timedelta(0, 1600), 'adversaires': [4]},
             {'points': 13, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 14), 'duree': timedelta(0, 1900), 'adversaires': [2]},
             {'points': 11, 'etat': PERDU, 'debut': datetime(
                 2010, 6, 20, 15), 'duree': timedelta(0, 1500), 'adversaires': [8]},
             {'points': 13, 'etat': GAGNE, 'debut': datetime(2010, 6, 20, 16), 'duree': timedelta(0, 2500), 'adversaires': [1]}]


JOUEURS_5 = [("Marie", "Rourou", "25"), ("Anaïs", "Gaga", "24")]

# Statistiques après chaque fin de partie
STATISTIQUES_5 = [{'adversaires': [9], 'points': 12, 'chapeaux': 0, 'victoires': 1, 'parties': 1, 'forfaits': 0,
                   'moy_billon': 12.0, 'max_billon': 12, 'min_billon': 12,
                   'moy_duree': timedelta(0, 1450), 'max_duree': timedelta(0, 1450), 'min_duree': timedelta(0, 1450)},

                  {'adversaires': [9, 4], 'points': 24, 'chapeaux': 0, 'victoires': 2, 'parties': 2, 'forfaits': 0,
                      'moy_billon': 12.0, 'max_billon': 12, 'min_billon': 12,
                      'moy_duree': timedelta(0, 1525), 'max_duree': timedelta(0, 1600), 'min_duree': timedelta(0, 1450)},

                  {'adversaires': [9, 4, 2], 'points': 37, 'chapeaux': 0, 'victoires': 3, 'parties': 3, 'forfaits': 0,
                      'moy_billon': 12.33, 'max_billon': 13, 'min_billon': 12,
                      'moy_duree': timedelta(0, 1650), 'max_duree': timedelta(0, 1900), 'min_duree': timedelta(0, 1450)},

                  {'adversaires': [9, 4, 2, 8], 'points': 48, 'chapeaux': 0, 'victoires': 3, 'parties': 4, 'forfaits': 0,
                      'moy_billon': 12.0, 'max_billon': 13, 'min_billon': 11,
                      'moy_duree': timedelta(0, 1612, 500000), 'max_duree': timedelta(0, 1900), 'min_duree': timedelta(0, 1450)},

                  {'adversaires': [9, 4, 2, 8, 1], 'points': 61, 'chapeaux': 0, 'victoires': 4, 'parties': 5, 'forfaits': 0,
                      'moy_billon': 12.20, 'max_billon': 13, 'min_billon': 11,
                      'moy_duree': timedelta(0, 1790), 'max_duree': timedelta(0, 2500), 'min_duree': timedelta(0, 1450)}]

#--- Equipe 8-------------------------------------------------------------------

PARTIES_8 = [{'points': 12, 'etat': GAGNE, 'debut': datetime(2010, 6, 20, 12), 'duree': timedelta(0, 1650), 'adversaires': [2]},
             {'points': 8, 'etat': PERDU, 'debut': datetime(
                 2010, 6, 20, 13), 'duree': timedelta(0, 1250), 'adversaires': [9]},
             {'points': 12, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 14), 'duree': timedelta(0, 1300), 'adversaires': [1]},
             {'points': 12, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 15), 'duree': timedelta(0, 1500), 'adversaires': [5]},
             {'points': 12, 'etat': GAGNE, 'debut': datetime(2010, 6, 20, 16), 'duree': timedelta(0, 1800), 'adversaires': [4]}]


JOUEURS_8 = [("Thibaut", "Cuicui", "24"), ("Antoine", "Rourou", "26")]

# Statistiques après chaque fin de partie
STATISTIQUES_8 = [{'adversaires': [2], 'points': 12, 'chapeaux': 0, 'victoires': 1, 'parties': 1, 'forfaits': 0,
                   'moy_billon': 12.0, 'max_billon': 12, 'min_billon': 12,
                   'moy_duree': timedelta(0, 1650), 'max_duree': timedelta(0, 1650), 'min_duree': timedelta(0, 1650)},

                  {'adversaires': [2, 9], 'points': 20, 'chapeaux': 0, 'victoires': 1, 'parties':2, 'forfaits': 0,
                      'moy_billon': 10.0, 'max_billon': 12, 'min_billon': 8,
                      'moy_duree': timedelta(0, 1450), 'max_duree': timedelta(0, 1650), 'min_duree': timedelta(0, 1250)},

                  {'adversaires': [2, 9, 1], 'points': 32, 'chapeaux': 0, 'victoires': 2, 'parties': 3, 'forfaits': 0,
                      'moy_billon': 10.67, 'max_billon': 12, 'min_billon': 8,
                      'moy_duree': timedelta(0, 1400), 'max_duree': timedelta(0, 1650), 'min_duree': timedelta(0, 1250)},

                  {'adversaires': [2, 9, 1, 5], 'points': 44, 'chapeaux': 0, 'victoires': 3, 'parties': 4, 'forfaits': 0,
                      'moy_billon': 11.0, 'max_billon': 12, 'min_billon': 8,
                      'moy_duree': timedelta(0, 1425), 'max_duree': timedelta(0, 1650), 'min_duree': timedelta(0, 1250)},

                  {'adversaires': [2, 9, 1, 5, 4], 'points': 56, 'chapeaux': 0, 'victoires': 4, 'parties': 5, 'forfaits': 0,
                      'moy_billon': 11.20, 'max_billon': 12, 'min_billon': 8,
                      'moy_duree': timedelta(0, 1500), 'max_duree': timedelta(0, 1800), 'min_duree': timedelta(0, 1250)}]

#--- Equipe 9-------------------------------------------------------------------

PARTIES_9 = [{'points': 10, 'etat': PERDU, 'debut': datetime(2010, 6, 20, 12), 'duree': timedelta(0, 1450), 'adversaires': [5]},
             {'points': 12, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 13), 'duree': timedelta(0, 1250), 'adversaires': [8]},
             {'points': 14, 'etat': GAGNE, 'debut': datetime(
                 2010, 6, 20, 14), 'duree': timedelta(0, 1450), 'adversaires': [4]},
             {'points': 0, 'etat': FORFAIT, 'debut': datetime(2010, 6, 20, 15), 'duree': None, 'adversaires': []},
             {'points': 12, 'etat': GAGNE, 'debut': datetime(2010, 6, 20, 16), 'duree': timedelta(0, 1050), 'adversaires': [2]}]


JOUEURS_9 = [("Jean-Louis", "Gaugau", "35"), ("Carole", "Rourou", "33")]

# Statistiques après chaque fin de partie
STATISTIQUES_9 = [{'adversaires': [5], 'points': 10, 'chapeaux': 0, 'victoires': 0, 'parties': 1, 'forfaits': 0,
                   'moy_billon': 10.0, 'max_billon': 10, 'min_billon': 10,
                   'moy_duree': timedelta(0, 1450), 'max_duree': timedelta(0, 1450), 'min_duree': timedelta(0, 1450)},

                  {'adversaires': [5, 8], 'points': 22, 'chapeaux': 0, 'victoires': 1, 'parties': 2, 'forfaits': 0,
                      'moy_billon': 11.0, 'max_billon': 12, 'min_billon': 10,
                      'moy_duree': timedelta(0, 1350), 'max_duree': timedelta(0, 1450), 'min_duree': timedelta(0, 1250)},

                  {'adversaires': [5, 8, 4], 'points': 36, 'chapeaux': 0, 'victoires': 2, 'parties': 3, 'forfaits': 0,
                      'moy_billon': 12.0, 'max_billon': 14, 'min_billon': 10,
                      'moy_duree': timedelta(0, 1383, 333333), 'max_duree': timedelta(0, 1450), 'min_duree': timedelta(0, 1250)},

                  {'adversaires': [5, 8, 4], 'points': 36, 'chapeaux': 0, 'victoires': 2, 'parties': 3, 'forfaits': 1,
                      'moy_billon': 12.0, 'max_billon': 14, 'min_billon': 10,
                      'moy_duree': timedelta(0, 1383, 333333), 'max_duree': timedelta(0, 1450), 'min_duree': timedelta(0, 1250)},

                  {'adversaires': [5, 8, 4, 2], 'points': 48, 'chapeaux': 0, 'victoires': 3, 'parties': 4, 'forfaits': 1,
                      'moy_billon': 12.0, 'max_billon': 14, 'min_billon': 10,
                      'moy_duree': timedelta(0, 1300), 'max_duree': timedelta(0, 1450), 'min_duree': timedelta(0, 1050)}]
