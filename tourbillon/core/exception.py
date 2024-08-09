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


# ARRET TIRAGE: pas de solution acceptable
#
ERREUR_MSG = {100: "Le nombre de chapeaux donné et superieur au nombre d'équipes par manche.",
              #
              #                   args: nb_chapeaux_donnés, nb_equipes_par_manche
              #
              101: "Toutes les équipes on déjà été chapeau au moins une fois et la redondance n'est pas autorisée.",
              #
              #                   args: nb_chapeaux_min, nb_chapeaux_max
              #
              102: "Le nombre de chapeaux donné ne correspond pas au nombre attendu.",
              #
              #                   args: nb_chapeaux_attendu - nb_chapeaux_donnés
              #
              150: "Une même équipe apparaît plusieurs fois dans le tirage.",
              #
              #                   args: (equipe1, nb_occurrence), (equipe2, nb_occurrence), ...
              #
              151: "Au moins une manche qui a déjà été disputée se trouve dans le tirage et la redondance n'est pas autorisée.",
              #
              #                   args: manche1, manche2, ...
              #
              152: "Une des manches du tirage ne comporte pas le bon nombre d'équipes.",
              #
              #                   args: manche, nb_equipes_par_manche
              #
              153: "Au moins une des équipes données n'existe pas.",
              #
              #                   args: equipe1, equipe2, ...
              #
              154: "Toutes les équipes se sont rencontrées, la redondance doit être autorisée.",
              #
              #                   args:
              155: "La disparité est trop faible pour trouver une solution.",
              #
              #                   args:
              156: "La disparité doit être augmentée ou la redondance autorisée.", }
              #
              #                   args:


class DrawResultError(DrawError):

    def __init__(self, code, args):
        DrawError.__init__()
        self.code = code
        self.args = args
        self.msg = ERREUR_MSG[self.code]

    def __str__(self):
        return "Erreur %s: %s (%s)" % (self.code, self.msg, self.args)
