# -*- coding: UTF-8 -*-

"""Définitions des équipes."""

import os
import sys
import importlib.util

from ..exception import DrawError

HERE = os.path.dirname(os.path.abspath(__file__))
TIRAGES = {}

# Dynamic draw modules import
for filename in os.listdir(HERE):
    if filename.endswith('.py') and filename not in ('__init__.py', 'utils.py'):
        name = '.'.join((__name__, os.path.splitext(filename)[0]))
        spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        TIRAGES[module.ThreadTirage.NOM] = module.ThreadTirage


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
