# -*- coding: UTF-8 -*-

"""Définitions des équipes."""

import os

from tourbillon.core.exception import DrawError
from tourbillon.core.draws import ascending, random_ag, level_ag, level_dt


ICI = os.path.dirname(os.path.abspath(__file__))
TIRAGES = {ascending.ThreadTirage.NOM: ascending.ThreadTirage,
           random_ag.ThreadTirage.NOM: random_ag.ThreadTirage,
           level_ag.ThreadTirage.NOM: level_ag.ThreadTirage,
           level_dt.ThreadTirage.NOM: level_dt.ThreadTirage}


def creer_generateur(algorithme, equipes_par_manche, statistiques, chapeaux=[], callback=None):
    """Crée un nouveau générateur de tirage (objet Thread). Le tirage est
    configuré avec ses parametes par defaut, la methode 'configurer' du générateur
    permet de les mettre à jour.

    algorithme (str)          : nom de l'algorithme à utiliser
    equipes_par_manche (int)  : nombre d'équipe dans une manche (i.e. nb adversaires)
    statistiques (dict)       : données de toutes les parties précédentes
    chapeaux (list)           : liste des équipes à mettre au chapeaux si besoin
                                (par défaut vide pour choix automatique)
    callback (callable)       : fonction à appeler après la fin de la génération
                                du tirage (par défaut vide)
    """
    if algorithme not in TIRAGES:
        raise DrawError("Categorie de tirage '%s' inconnue." % algorithme)

    # Création thread tirage
    return TIRAGES[algorithme](equipes_par_manche, statistiques, chapeaux, callback)
