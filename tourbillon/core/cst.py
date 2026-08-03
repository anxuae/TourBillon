# -*- coding: UTF-8 -*-

# Match result.
# The values are persisted in the YAML save files: DO NOT change them to keep
# the retro-compatibility with the historical archives.
BYE = 'chapeau'      # BYE
WON = 'gagné'        # WIN
LOST = 'perdu'       # LOSS
FORFEIT = 'forfait'  # FORFEIT

# State of a match
MATCH_IN_PROGRESS = "en cours"
MATCH_FINISHED = "terminée"

# State of a team
TEAM_INCOMPLETE = "incomplète"
TEAM_WAITING_DRAW = "attend tirage"
TEAM_IN_PROGRESS = "en cours"

# State of a round
ROUND_WAITING_DRAW = "attend tirage"
ROUND_IN_PROGRESS = "en cours"
ROUND_COMPLETE = "complète"
ROUND_FINISHED = "terminée"

# State of a tournament
TOURNAMENT_REGISTRATION = "inscription"
TOURNAMENT_WAITING_DRAW = "attend tirage"
TOURNAMENT_ROUND_IN_PROGRESS = "en cours"

# Genetic algorithm parameter
MAXIMIZE = "maximise"
MINIMIZE = "minimise"

# Keys of the statistics mapping consumed by the draws.
# These are in-memory keys only (not persisted), so they use English values.
STAT_POINTS = 'points'
STAT_WINS = 'wins'
STAT_BYES = 'byes'
STAT_OPPONENTS = 'opponents'
STAT_MATCHES = 'matches'
STAT_RANK = 'rank'
