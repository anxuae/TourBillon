# -*- coding: UTF-8 -*-

"""Renvoyer une liste de manches par ordre croissant de numéros d'équipe."""

from tourbillon.core.tirages.utils import BaseThreadTirage, creer_manches, tri_stat
from tourbillon.core import constantes as cst


class ThreadTirage(BaseThreadTirage):
    NOM = "croissant"

    DESCRIPTION = "Par ordre croissant"

    DEFAUT = {'PAR_NUMERO': True,
              'PAR_POINTS': False,
              'PAR_VICTOIRES': False,
              'INVERSER': False}

    def __init__(self, *args, **kargs):
        BaseThreadTirage.__init__(self, *args, **kargs)

    def demarrer(self):
        for num in self.chapeaux:
            # Suppression des chapeaux pré-séléctionnées
            self.statistiques.pop(int(num))

        equipes = []

        # Créer des manches par numéro d'équipe croissant/décroissant
        if self.config['par_numero'] and not self.config['par_points'] and not self.config['par_victoires']:
            equipes = sorted(self.statistiques.keys(), reverse=self.config['inverser'])

        # Créer des manches par total de points croissant/décroissant
        elif self.config['par_points']:
            tri = tri_stat(self.statistiques, cst.STAT_POINTS)
            for cle in sorted(tri, reverse=self.config['inverser']):
                if self.config['par_numero']:
                    equipes.extend(sorted(tri[cle], reverse=self.config['inverser']))
                else:
                    equipes.extend(tri[cle])

        # Créer des manches par total de victoires croissant/décroissant
        if self.config['par_victoires']:
            tri = tri_stat(self.statistiques, cst.STAT_VICTOIRES)
            for cle in sorted(tri, reverse=self.config['inverser']):
                if self.config['par_numero']:
                    equipes.extend(sorted(tri[cle], reverse=self.config['inverser']))
                else:
                    equipes.extend(tri[cle])

        self.tirage = creer_manches(equipes, self.equipes_par_manche)

        if len(self.tirage[-1]) < self.equipes_par_manche:
            self.chapeaux += self.tirage.pop(-1)
