# -*- coding: UTF-8 -*-

"""Test unitaires de TourBillon: test de toutest les methodes des classes Equipe
et Partie (Partie manipule les données stockées dans Equipe).

Note: les tests peuvent être lancés en chaine grâce à l'outil 'pytest' de la
      bibliothèque logilab.common
"""

import unittest
from datetime import timedelta
from tourbillon.core import tournoi
from tourbillon.core import equipe
from tourbillon.core.exceptions import NumeroError, StatutError
from tourbillon.core.constantes import CHAPEAU, FORFAIT, E_INCOMPLETE, E_ATTEND_TIRAGE, E_EN_COURS

# Donnée de l'équipe 1 servant pour le test
from data import EQUIPES_PAR_MANCHE, POINTS_PAR_MANCHE, JOUEURS_PAR_EQUIPE
from data import STATISTIQUES_1 as STATISTIQUES
from data import PARTIES_1 as PARTIES
from data import JOUEURS_1 as JOUEURS

EQUIPE = equipe.Equipe(tournoi.Tournoi(EQUIPES_PAR_MANCHE, POINTS_PAR_MANCHE, JOUEURS_PAR_EQUIPE), 1)

STAT0 = {'adversaires': [], 'points': 0, 'victoires': 0, 'forfaits': 0, 'parties': 0, 'chapeaux': 0,
         'moy_billon': 0, 'min_billon': 0, 'max_billon': 0,
         'moy_duree': timedelta(0), 'min_duree': timedelta(0), 'max_duree': timedelta(0)}


def verif_statistiques(self, adversaires=[], points=0, victoires=0, forfaits=0, parties=0, chapeaux=0,
                       moy_billon=0, min_billon=0, max_billon=0,
                       moy_duree=timedelta(0), min_duree=timedelta(0), max_duree=timedelta(0)):

    self.assertEqual(EQUIPE.adversaires(), adversaires)
    self.assertEqual(EQUIPE.total_points(), points)
    self.assertEqual(EQUIPE.total_victoires(), victoires)
    self.assertEqual(EQUIPE.total_forfaits(), forfaits)
    self.assertEqual(EQUIPE.total_parties(), parties)
    self.assertEqual(EQUIPE.total_chapeaux(), chapeaux)
    self.assertEqual(EQUIPE.moyenne_billon(), moy_billon)
    self.assertEqual(EQUIPE.min_billon(), min_billon)
    self.assertEqual(EQUIPE.max_billon(), max_billon)
    self.assertEqual(EQUIPE.moyenne_duree(), moy_duree)
    self.assertEqual(EQUIPE.min_duree(), min_duree)
    self.assertEqual(EQUIPE.max_duree(), max_duree)


class Test01EquipeVide(unittest.TestCase):

    def test01_statut(self):
        self.assertEqual(EQUIPE.statut, E_INCOMPLETE)

    def test02_nb_joueurs(self):
        self.assertEqual(EQUIPE.nb_joueurs(), 0)

    def test03_statistiques(self):
        verif_statistiques(self, adversaires=[], points=0, victoires=0, forfaits=0, parties=0, chapeaux=0,
                           moy_billon=0, min_billon=0, max_billon=0,
                           moy_duree=timedelta(0), min_duree=timedelta(0), max_duree=timedelta(0))


class Test02EquipeComplete(unittest.TestCase):

    def test01_ajouter_joueur(self):
        for i in range(JOUEURS_PAR_EQUIPE):
            EQUIPE.ajout_joueur(JOUEURS[i][0], JOUEURS[i][1], JOUEURS[i][2])

    def test02_statut(self):
        self.assertEqual(EQUIPE.statut, E_ATTEND_TIRAGE)

    def test03_nb_joueurs(self):
        self.assertEqual(EQUIPE.nb_joueurs(), JOUEURS_PAR_EQUIPE)

    def test04_statistiques(self):
        verif_statistiques(self, adversaires=[], points=0, victoires=0, forfaits=0, parties=0, chapeaux=0,
                           moy_billon=0, min_billon=0, max_billon=0,
                           moy_duree=timedelta(0), min_duree=timedelta(0), max_duree=timedelta(0))


class Test03EquipePartie1(unittest.TestCase):
    num = 0

    def setUp(self):
        if PARTIES[self.num]['etat'] != FORFAIT and PARTIES[self.num]['etat'] != CHAPEAU:
            # L'état est inconnu et la manche est en cours
            self.etat = None
            self.statut = E_EN_COURS
            self.fin = PARTIES[self.num]['debut'] + PARTIES[self.num]['duree']
        else:
            # L'équipe est CHAPEAU ou FORFAIT
            self.etat = PARTIES[self.num]['etat']
            self.statut = E_ATTEND_TIRAGE
            self.fin = None

    def test01_statut(self):
        self.assertEqual(EQUIPE.statut, E_ATTEND_TIRAGE)

    def test02_ajout_partie(self):
        EQUIPE._ajout_partie(PARTIES[self.num]['debut'], PARTIES[self.num]['adversaires'], self.etat, 1)
        if PARTIES[self.num]['etat'] != FORFAIT and PARTIES[self.num]['etat'] != CHAPEAU:
            # L'état est inconnu et la manche est en cours
            self.assertRaises(StatutError, EQUIPE._ajout_partie, PARTIES[self.num][
                              'debut'], PARTIES[self.num]['adversaires'], None, 1)

    def test03_statut(self):
        """
        Equipe FORFAIT attend toujour un tirage.
        """
        self.assertEqual(EQUIPE.statut, self.statut)

    def test04_statistiques_avant_resultat(self):
        if PARTIES[self.num]['etat'] != FORFAIT and PARTIES[self.num]['etat'] != CHAPEAU:
            num_av = self.num - 1
            if num_av < 0:
                stat = STAT0
            else:
                stat = STATISTIQUES[num_av]

            verif_statistiques(self, adversaires=STATISTIQUES[self.num]['adversaires'], points=stat['points'], victoires=stat['victoires'],
                               forfaits=stat['forfaits'], parties=STATISTIQUES[
                self.num]['parties'], chapeaux=stat['chapeaux'],
                moy_billon=stat['moy_billon'], min_billon=stat[
                'min_billon'], max_billon=stat['max_billon'],
                moy_duree=stat['moy_duree'], min_duree=stat['min_duree'], max_duree=stat['max_duree'])
        else:
            verif_statistiques(self, **STATISTIQUES[self.num])

    def test05_modifier_partie(self):
        self.assertRaises(NumeroError, EQUIPE._modif_partie, 10, PARTIES[
                          self.num]['points'], PARTIES[self.num]['etat'], self.fin)
        EQUIPE._modif_partie(self.num + 1, PARTIES[self.num]['points'], PARTIES[self.num]['etat'], self.fin)

    def test06_statistiques_apres_resultat(self):
        verif_statistiques(self, **STATISTIQUES[self.num])


class Test04EquipePartie2(Test03EquipePartie1):
    num = 1


class Test05EquipePartie3(Test03EquipePartie1):
    num = 2


class Test06EquipePartie4(Test03EquipePartie1):
    num = 3


class Test07EquipePartie5(Test03EquipePartie1):
    num = 4
