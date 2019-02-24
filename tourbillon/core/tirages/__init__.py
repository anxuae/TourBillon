# -*- coding: UTF-8 -*-

"""Définitions des équipes."""

import sys
import os
import imp
import re
from tourbillon.core.exceptions import TirageError
from tourbillon.core.tirages import aleatoire_ag, niveau_ag, niveau2008_dt, croissant

ICI = os.path.dirname(os.path.abspath(__file__))
TIRAGES = {croissant.ThreadTirage.NOM: croissant.ThreadTirage,
           aleatoire_ag.ThreadTirage.NOM: aleatoire_ag.ThreadTirage,
           niveau_ag.ThreadTirage.NOM: niveau_ag.ThreadTirage,
           niveau2008_dt.ThreadTirage.NOM: niveau2008_dt.ThreadTirage}


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
        raise TirageError(u"Categorie de tirage '%s' inconnue." % algorithme)

    # Création thread tirage
    return TIRAGES[algorithme](equipes_par_manche, statistiques, chapeaux, callback)
