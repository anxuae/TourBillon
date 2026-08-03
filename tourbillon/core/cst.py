# -*- coding: UTF-8 -*-

# Match result.
# These values are the in-memory (English) representation. Persistence stays
# retro-compatible with the historical archives: the French literals are
# restored/translated at the (de)serialization boundary in ``match.py`` (see
# ``Match.load``/``Match.dump``). DO NOT persist these English values as-is.
BYE = 'bye'          # BYE
WON = 'won'          # WIN
LOST = 'lost'        # LOSS
FORFEIT = 'forfeit'  # FORFEIT

# States below (match/team/round/tournament) are computed on the fly and never
# persisted, so they use plain English values exposed directly by the API.

# State of a match
MATCH_IN_PROGRESS = "in_progress"
MATCH_FINISHED = "finished"

# State of a team
TEAM_INCOMPLETE = "incomplete"
TEAM_WAITING_DRAW = "awaiting_draw"
TEAM_IN_PROGRESS = "in_progress"

# State of a round
ROUND_WAITING_DRAW = "awaiting_draw"
ROUND_IN_PROGRESS = "in_progress"
ROUND_COMPLETE = "complete"
ROUND_FINISHED = "finished"

# State of a tournament
TOURNAMENT_REGISTRATION = "registration"
TOURNAMENT_WAITING_DRAW = "awaiting_draw"
TOURNAMENT_ROUND_IN_PROGRESS = "round_in_progress"

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
