#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import random
import datetime
from tourbillon.trb_test import data
from tourbillon.trb_core import tournoi
from tourbillon.trb_core import constantes as cst
from tourbillon.trb_core import tirages

class TestCreerTournoi(unittest.TestCase):

    def test01_nouveau(self):
        t = tournoi.nouveau_tournoi(4, 7, 1)
        self.assertIsNotNone(tournoi.tournoi())
        self.assertEqual(t.statut, cst.T_INSCRIPTION)
        self.assertEqual(t.nb_equipes(), 0)
        self.assertEqual(t.equipes(), [])
        self.assertEqual(t.nb_parties(), 0)
        self.assertIsNone(t.partie_courante())
        self.assertEqual(t.parties(), [])
        self.assertEqual(t.classement(), [])

    def test02_inscription(self):
        t = tournoi.tournoi()
        for ref_equipe in data.REF_TOURNOI.equipes():
            eq = t.ajout_equipe(t.nouveau_numero_equipe())
            self.assertEqual(eq.statut, cst.E_INCOMPLETE)
            ref_joueur = ref_equipe.joueurs()[0]
            eq.ajout_joueur(ref_joueur.prenom, ref_joueur.nom)
            self.assertEqual(eq.statut, cst.E_ATTEND_TIRAGE)
        self.assertEqual(t.statut, cst.T_ATTEND_TIRAGE)
        self.assertEqual(t.nb_equipes(), 50)

class TestAjoutParie1(unittest.TestCase):
    type_tirage = 'aleatoire_ag'
    def test01_nouvelle_partie(self):
        t = tournoi.tournoi()
        partie = t.ajout_partie()
        self.assertEqual(t.statut, cst.T_PARTIE_EN_COURS)
        for equipe in t.equipes():
            self.assertEqual(equipe.statut, cst.E_ATTEND_TIRAGE)

    def test02_nouveau_tirage(self):
        t = tournoi.tournoi()
        p = t.partie_courante()
        tir = tirages.tirage(self.type_tirage, t.equipes_par_manche, t.statistiques())
        tir.start()
        tir.join()
        p.demarrer(dict(zip(range(len(tir.tirage)), tir.tirage)), tir.chapeaux)
        for equipe in t.equipes():
            if equipe.resultat(p.numero).etat in [cst.CHAPEAU, cst.FORFAIT]:
                self.assertEqual(equipe.statut, cst.E_ATTEND_TIRAGE)
            else:
                self.assertEqual(equipe.statut, cst.E_JOUE)
        self.assertEqual(p.statut, cst.P_EN_COURS)
        self.assertEqual(t.statut, cst.T_PARTIE_EN_COURS)

    def test03_resultats(self):
        t = tournoi.tournoi()
        p = t.partie_courante()
        for manche in p.tirage():
            d = {}
            for eq in manche:
                if t.points_par_manche not in d.values():
                    d[eq] = 7
                else:
                    d[eq] = random.randint(2, 9)
            p.resultat(d, datetime.datetime.now())

        for equipe in t.equipes():
            self.assertEqual(equipe.statut, cst.E_ATTEND_TIRAGE)
        self.assertEqual(p.statut, cst.P_COMPLETE)
        self.assertEqual(t.statut, cst.T_ATTEND_TIRAGE)

class TestAjoutParie2(TestAjoutParie1):
    type_tirage = 'niveau2008_dt'
class TestAjoutParie3(TestAjoutParie1):
    type_tirage = 'niveau_ag'
