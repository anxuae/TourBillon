#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des exceptions spécifiques à Tourbillon."""

#--- class ---------------------------------------------------------------------

class TourBillonError(Exception):pass

class ConfigError(TourBillonError):pass
class FichierError(TourBillonError):pass
class NumeroError(TourBillonError):pass
class DureeError(TourBillonError):pass
class StatutError(TourBillonError):pass
class LimiteError(TourBillonError):pass
class IncoherenceError(TourBillonError):pass
class ResultatError(TourBillonError):pass

# ARRET TIRAGE: erreur sur les paramètres
class TirageError(TourBillonError):pass

# ARRET TIRAGE: utilisateur
class StopTirageError(TourBillonError):pass

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

class SolutionError(TourBillonError):
    def __init__(self, code, args):
        self.code = code
        self.args = args
        self.msg = ERREUR_MSG[self.code]

    def __str__(self):
        return "Erreur %s: %s (%s)" % (self.code, self.msg, self.args)
