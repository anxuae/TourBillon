# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from tourbillon.core.cst import BYE, WON, LOST, FORFEIT

#--- Tournament used for data extraction --------------------------------------

TEAMS_BY_MATCH = 2
POINTS_BY_MATCH = 12
PLAYERS_BY_TEAM = 2

#--- Team 1 -------------------------------------------------------------------

ROUNDS_1 = [{'points': 12, 'result': WON, 'start': datetime(2010, 6, 20, 12), 'duration': timedelta(0, 1750), 'opponents': [4]},
             {'points': 0, 'result': FORFEIT, 'start': datetime(2010, 6, 20, 13), 'duration': None, 'opponents': []},
             {'points': 9, 'result': LOST, 'start': datetime(
                 2010, 6, 20, 14), 'duration': timedelta(0, 1300), 'opponents': [8]},
             {'points': 12, 'result': BYE, 'start': datetime(2010, 6, 20, 15), 'duration': None, 'opponents': []},
             {'points': 10, 'result': LOST, 'start': datetime(2010, 6, 20, 16), 'duration': timedelta(0, 2500), 'opponents': [5]}]


PLAYERS_1 = [("Guillaume", "Cuicui"), ("Thomas", "Rourou")]

# Statistics after each round
STATS_1 = [{'opponents': [4], 'points': 12, 'byes': 0, 'wins': 1, 'rounds': 1, 'forfeits': 0,
                   'average_score': 12.0, 'max_score': 12, 'min_score': 12,
                   'average_duration': timedelta(0, 1750), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1750)},

                  {'opponents': [4], 'points': 12, 'byes': 0, 'wins': 1, 'rounds': 1, 'forfeits': 1,
                      'average_score': 12.0, 'max_score': 12, 'min_score': 12,
                      'average_duration': timedelta(0, 1750), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1750)},

                  {'opponents': [4, 8], 'points': 21, 'byes': 0, 'wins': 1, 'rounds': 2, 'forfeits': 1,
                      'average_score': 10.5, 'max_score': 12, 'min_score': 9,
                      'average_duration': timedelta(0, 1525), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1300)},

                  {'opponents': [4, 8], 'points': 33, 'byes': 1, 'wins': 1, 'rounds': 3, 'forfeits': 1,
                      'average_score': 11.0, 'max_score': 12, 'min_score': 9,
                      'average_duration': timedelta(0, 1525), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1300)},

                  {'opponents': [4, 8, 5], 'points': 43, 'byes': 1, 'wins': 1, 'rounds': 4, 'forfeits': 1,
                      'average_score': 10.75, 'max_score': 12, 'min_score': 9,
                      'average_duration': timedelta(0, 1850), 'max_duration': timedelta(0, 2500), 'min_duration': timedelta(0, 1300)}]

#--- Team 2-------------------------------------------------------------------

ROUNDS_2 = [{'points': 9, 'result': LOST, 'start': datetime(2010, 6, 20, 12), 'duration': timedelta(0, 1650), 'opponents': [8]},
             {'points': 12, 'result': BYE, 'start': datetime(2010, 6, 20, 13), 'duration': None, 'opponents': []},
             {'points': 10, 'result': LOST, 'start': datetime(
                 2010, 6, 20, 14), 'duration': timedelta(0, 1900), 'opponents': [5]},
             {'points': 9, 'result': LOST, 'start': datetime(
                 2010, 6, 20, 15), 'duration': timedelta(0, 1550), 'opponents': [4]},
             {'points': 5, 'result': LOST, 'start': datetime(2010, 6, 20, 16), 'duration': timedelta(0, 1050), 'opponents': [9]}]


PLAYERS_2 = [("Christophe", "Dudu"), ("Christophe", "Rourou")]

# Statistics after each round
STATS_2 = [{'opponents': [8], 'points': 9, 'byes': 0, 'wins': 0, 'rounds': 1, 'forfeits': 0,
                   'average_score': 9.0, 'max_score': 9, 'min_score': 9,
                   'average_duration': timedelta(0, 1650), 'max_duration': timedelta(0, 1650), 'min_duration': timedelta(0, 1650)},

                  {'opponents': [8], 'points': 21, 'byes': 1, 'wins': 0, 'rounds': 2, 'forfeits': 0,
                      'average_score': 10.5, 'max_score': 12, 'min_score': 9,
                      'average_duration': timedelta(0, 1650), 'max_duration': timedelta(0, 1650), 'min_duration': timedelta(0, 1650)},

                  {'opponents': [8, 5], 'points': 31, 'byes': 1, 'wins': 0, 'rounds': 3, 'forfeits': 0,
                      'average_score': 10.33, 'max_score': 12, 'min_score': 9,
                      'average_duration': timedelta(0, 1775), 'max_duration': timedelta(0, 1900), 'min_duration': timedelta(0, 1650)},

                  {'opponents': [8, 5, 4], 'points': 40, 'byes': 1, 'wins': 0, 'rounds': 4, 'forfeits': 0,
                      'average_score': 10.0, 'max_score': 12, 'min_score': 9,
                      'average_duration': timedelta(0, 1700), 'max_duration': timedelta(0, 1900), 'min_duration': timedelta(0, 1550)},

                  {'opponents': [8, 5, 4, 9], 'points': 45, 'byes': 1, 'wins': 0, 'rounds': 5, 'forfeits': 0,
                      'average_score': 9.0, 'max_score': 12, 'min_score': 5,
                      'average_duration': timedelta(0, 1537, 500000), 'max_duration': timedelta(0, 1900), 'min_duration': timedelta(0, 1050)}]

#--- Team 4-------------------------------------------------------------------

ROUNDS_4 = [{'points': 7, 'result': LOST, 'start': datetime(2010, 6, 20, 12), 'duration': timedelta(0, 1750), 'opponents': [1]},
             {'points': 13, 'result': WON, 'start': datetime(
                 2010, 6, 20, 13), 'duration': timedelta(0, 1600), 'opponents': [5]},
             {'points': 13, 'result': WON, 'start': datetime(
                 2010, 6, 20, 14), 'duration': timedelta(0, 1450), 'opponents': [9]},
             {'points': 12, 'result': WON, 'start': datetime(
                 2010, 6, 20, 15), 'duration': timedelta(0, 1550), 'opponents': [2]},
             {'points': 8, 'result': LOST, 'start': datetime(2010, 6, 20, 16), 'duration': timedelta(0, 1800), 'opponents': [8]}]


PLAYERS_4 = [("Jean-Philipe", "Rourou"), ("Erwan", "Rourou")]

# Statistics after each round
STATS_4 = [{'opponents': [1], 'points': 7, 'byes': 0, 'wins': 0, 'rounds': 1, 'forfeits': 0,
                   'average_score': 7.0, 'max_score': 7, 'min_score': 7,
                   'average_duration': timedelta(0, 1750), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1750)},

                  {'opponents': [1, 5], 'points': 20, 'byes': 0, 'wins': 1, 'rounds': 2, 'forfeits': 0,
                      'average_score': 10.0, 'max_score': 13, 'min_score': 7,
                      'average_duration': timedelta(0, 1675), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1600)},

                  {'opponents': [1, 5, 9], 'points': 33, 'byes': 0, 'wins': 2, 'rounds': 3, 'forfeits': 0,
                      'average_score': 11.0, 'max_score': 13, 'min_score': 7,
                      'average_duration': timedelta(0, 1600), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1450)},

                  {'opponents': [1, 5, 9, 2], 'points': 45, 'byes': 0, 'wins': 3, 'rounds': 4, 'forfeits': 0,
                      'average_score': 11.25, 'max_score': 13, 'min_score': 7,
                      'average_duration': timedelta(0, 1587, 500000), 'max_duration': timedelta(0, 1750), 'min_duration': timedelta(0, 1450)},

                  {'opponents': [1, 5, 9, 2, 8], 'points': 53, 'byes': 0, 'wins': 3, 'rounds': 5, 'forfeits': 0,
                      'average_score': 10.6, 'max_score': 13, 'min_score': 7,
                      'average_duration': timedelta(0, 1630), 'max_duration': timedelta(0, 1800), 'min_duration': timedelta(0, 1450)}]

#--- Team 5-------------------------------------------------------------------

ROUNDS_5 = [{'points': 12, 'result': WON, 'start': datetime(2010, 6, 20, 12), 'duration': timedelta(0, 1450), 'opponents': [9]},
             {'points': 12, 'result': WON, 'start': datetime(
                 2010, 6, 20, 13), 'duration': timedelta(0, 1600), 'opponents': [4]},
             {'points': 13, 'result': WON, 'start': datetime(
                 2010, 6, 20, 14), 'duration': timedelta(0, 1900), 'opponents': [2]},
             {'points': 11, 'result': LOST, 'start': datetime(
                 2010, 6, 20, 15), 'duration': timedelta(0, 1500), 'opponents': [8]},
             {'points': 13, 'result': WON, 'start': datetime(2010, 6, 20, 16), 'duration': timedelta(0, 2500), 'opponents': [1]}]


PLAYERS_5 = [("Marie", "Rourou"), ("Anaïs", "Gaga")]

# Statistics after each round
STATS_5 = [{'opponents': [9], 'points': 12, 'byes': 0, 'wins': 1, 'rounds': 1, 'forfeits': 0,
                   'average_score': 12.0, 'max_score': 12, 'min_score': 12,
                   'average_duration': timedelta(0, 1450), 'max_duration': timedelta(0, 1450), 'min_duration': timedelta(0, 1450)},

                  {'opponents': [9, 4], 'points': 24, 'byes': 0, 'wins': 2, 'rounds': 2, 'forfeits': 0,
                      'average_score': 12.0, 'max_score': 12, 'min_score': 12,
                      'average_duration': timedelta(0, 1525), 'max_duration': timedelta(0, 1600), 'min_duration': timedelta(0, 1450)},

                  {'opponents': [9, 4, 2], 'points': 37, 'byes': 0, 'wins': 3, 'rounds': 3, 'forfeits': 0,
                      'average_score': 12.33, 'max_score': 13, 'min_score': 12,
                      'average_duration': timedelta(0, 1650), 'max_duration': timedelta(0, 1900), 'min_duration': timedelta(0, 1450)},

                  {'opponents': [9, 4, 2, 8], 'points': 48, 'byes': 0, 'wins': 3, 'rounds': 4, 'forfeits': 0,
                      'average_score': 12.0, 'max_score': 13, 'min_score': 11,
                      'average_duration': timedelta(0, 1612, 500000), 'max_duration': timedelta(0, 1900), 'min_duration': timedelta(0, 1450)},

                  {'opponents': [9, 4, 2, 8, 1], 'points': 61, 'byes': 0, 'wins': 4, 'rounds': 5, 'forfeits': 0,
                      'average_score': 12.20, 'max_score': 13, 'min_score': 11,
                      'average_duration': timedelta(0, 1790), 'max_duration': timedelta(0, 2500), 'min_duration': timedelta(0, 1450)}]

#--- Team 8-------------------------------------------------------------------

ROUNDS_8 = [{'points': 12, 'result': WON, 'start': datetime(2010, 6, 20, 12), 'duration': timedelta(0, 1650), 'opponents': [2]},
             {'points': 8, 'result': LOST, 'start': datetime(
                 2010, 6, 20, 13), 'duration': timedelta(0, 1250), 'opponents': [9]},
             {'points': 12, 'result': WON, 'start': datetime(
                 2010, 6, 20, 14), 'duration': timedelta(0, 1300), 'opponents': [1]},
             {'points': 12, 'result': WON, 'start': datetime(
                 2010, 6, 20, 15), 'duration': timedelta(0, 1500), 'opponents': [5]},
             {'points': 12, 'result': WON, 'start': datetime(2010, 6, 20, 16), 'duration': timedelta(0, 1800), 'opponents': [4]}]


PLAYERS_8 = [("Thibaut", "Cuicui"), ("Antoine", "Rourou")]

# Statistics after each round
STATS_8 = [{'opponents': [2], 'points': 12, 'byes': 0, 'wins': 1, 'rounds': 1, 'forfeits': 0,
                   'average_score': 12.0, 'max_score': 12, 'min_score': 12,
                   'average_duration': timedelta(0, 1650), 'max_duration': timedelta(0, 1650), 'min_duration': timedelta(0, 1650)},

                  {'opponents': [2, 9], 'points': 20, 'byes': 0, 'wins': 1, 'rounds':2, 'forfeits': 0,
                      'average_score': 10.0, 'max_score': 12, 'min_score': 8,
                      'average_duration': timedelta(0, 1450), 'max_duration': timedelta(0, 1650), 'min_duration': timedelta(0, 1250)},

                  {'opponents': [2, 9, 1], 'points': 32, 'byes': 0, 'wins': 2, 'rounds': 3, 'forfeits': 0,
                      'average_score': 10.67, 'max_score': 12, 'min_score': 8,
                      'average_duration': timedelta(0, 1400), 'max_duration': timedelta(0, 1650), 'min_duration': timedelta(0, 1250)},

                  {'opponents': [2, 9, 1, 5], 'points': 44, 'byes': 0, 'wins': 3, 'rounds': 4, 'forfeits': 0,
                      'average_score': 11.0, 'max_score': 12, 'min_score': 8,
                      'average_duration': timedelta(0, 1425), 'max_duration': timedelta(0, 1650), 'min_duration': timedelta(0, 1250)},

                  {'opponents': [2, 9, 1, 5, 4], 'points': 56, 'byes': 0, 'wins': 4, 'rounds': 5, 'forfeits': 0,
                      'average_score': 11.20, 'max_score': 12, 'min_score': 8,
                      'average_duration': timedelta(0, 1500), 'max_duration': timedelta(0, 1800), 'min_duration': timedelta(0, 1250)}]

#--- Team 9-------------------------------------------------------------------

ROUNDS_9 = [{'points': 10, 'result': LOST, 'start': datetime(2010, 6, 20, 12), 'duration': timedelta(0, 1450), 'opponents': [5]},
             {'points': 12, 'result': WON, 'start': datetime(
                 2010, 6, 20, 13), 'duration': timedelta(0, 1250), 'opponents': [8]},
             {'points': 14, 'result': WON, 'start': datetime(
                 2010, 6, 20, 14), 'duration': timedelta(0, 1450), 'opponents': [4]},
             {'points': 0, 'result': FORFEIT, 'start': datetime(2010, 6, 20, 15), 'duration': None, 'opponents': []},
             {'points': 12, 'result': WON, 'start': datetime(2010, 6, 20, 16), 'duration': timedelta(0, 1050), 'opponents': [2]}]


PLAYERS_9 = [("Jean-Louis", "Gaugau"), ("Carole", "Rourou")]

# Statistics after each round
STATS_9 = [{'opponents': [5], 'points': 10, 'byes': 0, 'wins': 0, 'rounds': 1, 'forfeits': 0,
                   'average_score': 10.0, 'max_score': 10, 'min_score': 10,
                   'average_duration': timedelta(0, 1450), 'max_duration': timedelta(0, 1450), 'min_duration': timedelta(0, 1450)},

                  {'opponents': [5, 8], 'points': 22, 'byes': 0, 'wins': 1, 'rounds': 2, 'forfeits': 0,
                      'average_score': 11.0, 'max_score': 12, 'min_score': 10,
                      'average_duration': timedelta(0, 1350), 'max_duration': timedelta(0, 1450), 'min_duration': timedelta(0, 1250)},

                  {'opponents': [5, 8, 4], 'points': 36, 'byes': 0, 'wins': 2, 'rounds': 3, 'forfeits': 0,
                      'average_score': 12.0, 'max_score': 14, 'min_score': 10,
                      'average_duration': timedelta(0, 1383, 333333), 'max_duration': timedelta(0, 1450), 'min_duration': timedelta(0, 1250)},

                  {'opponents': [5, 8, 4], 'points': 36, 'byes': 0, 'wins': 2, 'rounds': 3, 'forfeits': 1,
                      'average_score': 12.0, 'max_score': 14, 'min_score': 10,
                      'average_duration': timedelta(0, 1383, 333333), 'max_duration': timedelta(0, 1450), 'min_duration': timedelta(0, 1250)},

                  {'opponents': [5, 8, 4, 2], 'points': 48, 'byes': 0, 'wins': 3, 'rounds': 4, 'forfeits': 1,
                      'average_score': 12.0, 'max_score': 14, 'min_score': 10,
                      'average_duration': timedelta(0, 1300), 'max_duration': timedelta(0, 1450), 'min_duration': timedelta(0, 1050)}]
