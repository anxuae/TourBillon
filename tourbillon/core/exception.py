# -*- coding: UTF-8 -*-

"""Definitions of specific exceptions to TourBillon"""


class TourBillonError(Exception):
    pass


class FileError(TourBillonError):
    pass


class StatusError(TourBillonError):
    pass


class BoundError(TourBillonError):
    pass


class InconsistencyError(TourBillonError):
    pass


class ResultError(TourBillonError):
    pass


# ARRET TIRAGE: erreur sur les paramètres
class DrawError(TourBillonError):
    pass


# ARRET TIRAGE: utilisateur
class DrawStopError(DrawError):
    pass


# STOP DRAW: no acceptable pairing found
#
ERREUR_MSG = {100: "Number of BYE shall be lower than the number of teams per round",
              #
              #                   args: nb_chapeaux_donnés, nb_equipes_par_manche
              #
              101: "All teams have already been BYE at least once and redundancy is not allowed",
              #
              #                   args: nb_chapeaux_min, nb_chapeaux_max
              #
              102: "Number of BYE given does not correspond to the expected number",
              #
              #                   args: nb_chapeaux_attendu - nb_chapeaux_donnés
              #
              150: "Same team appears several times in the same draw",
              #
              #                   args: (equipe1, nb_occurrence), (equipe2, nb_occurrence), ...
              #
              151: "At least one identical match has already been done and redundancy is not allowed",
              #
              #                   args: manche1, manche2, ...
              #
              154: "All the teams have met, redundancy must be authorized",
              #
              #                   args:
              155: "The disparity is too low to find a correct draw",
              #
              #                   args:
              156: "The disparity must be increased or the redundancy authorized", }
              #
              #                   args:


class DrawResultError(DrawError):

    def __init__(self, code, args):
        DrawError.__init__()
        self.code = code
        self.args = args
        self.msg = ERREUR_MSG[self.code]

    def __str__(self):
        return "Error %s: %s (%s)" % (self.code, self.msg, self.args)
