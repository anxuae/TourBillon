#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
from datetime import datetime, timedelta

from tourbillon.trb_core import tournois
from tourbillon.trb_core.exceptions import FichierError, NumeroError, StatutError, LimiteError
from tourbillon.trb_core.constantes import (E_INCOMPLETE, E_ATTEND_TIRAGE, P_NON_DEMARREE, P_EN_COURS,
                                            P_COMPLETE,
                                            T_INSCRIPTION, T_ATTEND_TIRAGE, T_PARTIE_EN_COURS)

# Données
from tourbillon.trb_test.data import EQUIPES_PAR_MANCHE, POINTS_PAR_MANCHE, JOUEURS_PAR_EQUIPE
from tourbillon.trb_test import data

EQUIPES = {1: data.JOUEURS_1,
           2: data.JOUEURS_2,
           4: data.JOUEURS_4,
           5: data.JOUEURS_5,
           8: data.JOUEURS_8,  # Changé en n°3
           9: data.JOUEURS_9}  # Changé en n°6

NB_EQUIPES = len(EQUIPES)

tournois.nouveau_tournoi(EQUIPES_PAR_MANCHE, POINTS_PAR_MANCHE, JOUEURS_PAR_EQUIPE)


class TestCreationTournoi(unittest.TestCase):

    def setUp(self):
        self.tournoi = tournois.tournoi()

    def test01_status(self):
        self.assertEqual(self.tournoi.statut, T_INSCRIPTION)

    def test02_statistiques(self):
        self.assertEqual(self.tournoi.statistiques(), {})
        self.assertEqual(self.tournoi.statistiques([1, 2, 8], 2), {})

    def test03_nb_equipes(self):
        self.assertEqual(self.tournoi.nb_equipes(), 0)

    def test04_equipe(self):
        self.assertRaises(NumeroError, self.tournoi.equipe, 4)

    def test05_equipes(self):
        self.assertEqual(self.tournoi.equipes(), [])

    def test06_suppr_equipe(self):
        self.assertRaises(NumeroError, self.tournoi.suppr_equipe, 4)

    def test07_nb_parties(self):
        self.assertEqual(self.tournoi.nb_parties(), 0)

    def test08_partie(self):
        self.assertRaises(NumeroError, self.tournoi.partie, 3)

    def test09_parties(self):
        self.assertEqual(self.tournoi.parties(), [])

    def test10_partie_courante(self):
        self.assertEqual(self.tournoi.partie_courante(), None)

    def test11_suppr_partie(self):
        self.assertRaises(NumeroError, self.tournoi.suppr_partie, 3)

    def test12_config(self):
        self.assertEqual(self.tournoi.equipes_par_manche, EQUIPES_PAR_MANCHE)
        self.assertEqual(self.tournoi.joueurs_par_equipe, JOUEURS_PAR_EQUIPE)
        self.assertEqual(self.tournoi.points_par_manche, POINTS_PAR_MANCHE)


class TestInscriptionTournoi(unittest.TestCase):

    def setUp(self):
        self.tournoi = tournois.tournoi()

    def test01_ajout_equipe(self):
        for equipe in EQUIPES:
            e = self.tournoi.ajout_equipe(equipe)
            self.assertEqual(e.statut, E_INCOMPLETE)

    def test02_nb_equipes(self):
        self.assertEqual(self.tournoi.nb_equipes(), NB_EQUIPES)

    def test03_nb_parties(self):
        self.assertEqual(self.tournoi.nb_parties(), 0)

    def test04_ajout_joueur(self):
        for equipe in EQUIPES:
            e = self.tournoi.equipe(equipe)
            for joueur in EQUIPES[equipe]:
                j = e.ajout_joueur(joueur[0], joueur[1], joueur[2])
                self.assertEqual(j.prenom, joueur[0])
                self.assertEqual(j.nom, joueur[1])
                self.assertEqual(j.age, joueur[2])
            self.assertEqual(e.statut, E_ATTEND_TIRAGE)

    def test05_nb_joueurs(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.nb_joueurs(), JOUEURS_PAR_EQUIPE)

    def test06_trop_joueurs(self):
        for equipe in self.tournoi.equipes():
            self.assertRaises(LimiteError, equipe.ajout_joueur, "Prenom", "Nom", "00")

    def test07_changer_numero(self):
        # 8 -> 1
        e = self.tournoi.equipe(8)
        self.assertRaises(NumeroError, self.tournoi.modifier_numero_equipe, 8, 1)
        # 8 -> 3
        self.tournoi.modifier_numero_equipe(8, 3)
        self.assertEqual(e.numero, 3)
        # 8 a disparu
        self.assertRaises(NumeroError, self.tournoi.equipe, 8)
        # 9 -> 3
        e = self.tournoi.equipe(9)
        self.tournoi.modifier_numero_equipe(9, 6)
        self.assertEqual(e.numero, 6)
        # 9 a disparu
        self.assertRaises(NumeroError, self.tournoi.equipe, 9)

        # Changer le dictionnaire global pour le reste des tests
        EQUIPES[3] = EQUIPES.pop(8)
        EQUIPES[6] = EQUIPES.pop(9)

    def test08_adversaires(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.adversaires(), [])

    def test09_total_points(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.total_points(), 0)

    def test10_total_victoires(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.total_victoires(), 0)

    def test11_total_forfaits(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.total_forfaits(), 0)

    def test12_total_parties(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.total_parties(), 0)

    def test13_total_chapeaux(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.total_chapeaux(), 0)

    def test14_moyenne_billon(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.moyenne_billon(), 0)

    def test15_min_billon(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.min_billon(), 0)

    def test16_max_billon(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.max_billon(), 0)

    def test17_moyenne_duree(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.moyenne_duree(), timedelta(0))

    def test18_min_duree(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.min_duree(), timedelta(0))

    def test19_max_duree(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.max_duree(), timedelta(0))


class TestEnregistrerTournoi(unittest.TestCase):

    def setUp(self):
        self.tournoi = tournois.tournoi()

    def test01_enregistrer(self):
        self.assertEqual(self.tournoi.modifie, True)
        tournois.enregistrer_tournoi('test.trb')
        self.assertEqual(self.tournoi.modifie, False)

    def test02_date_enregistrement(self):
        d = datetime.now()
        d1 = self.tournoi.date_enregistrement - timedelta(0, 0, self.tournoi.date_enregistrement.microsecond)
        d2 = d - timedelta(0, 0, d.microsecond)
        self.assertEqual(d1, d2)


class TestChargerTournoi(unittest.TestCase):

    def setUp(self):
        self.tournoi = tournois.tournoi()

    def test01_enregistrer(self):
        tournois.charger_tournoi('test.trb')
        self.assertEqual(self.tournoi.modifie, False)

    def test02_date_chargement(self):
        d = datetime.now()
        d1 = self.tournoi.date_chargement - timedelta(0, 0, self.tournoi.date_chargement.microsecond)
        d2 = d - timedelta(0, 0, d.microsecond)
        self.assertEqual(d1, d2)

    def test03_nb_equipes(self):
        self.assertEqual(self.tournoi.nb_equipes(), NB_EQUIPES)

    def test04_nb_parties(self):
        self.assertEqual(self.tournoi.nb_parties(), 0)

    def test05_nb_joueurs(self):
        for equipe in self.tournoi.equipes():
            self.assertEqual(equipe.nb_joueurs(), JOUEURS_PAR_EQUIPE)

    def test06_nom_prenom_joueurs(self):
        for equipe in self.tournoi.equipes():
            ind_joueur = 0
            for joueur in equipe.joueurs():
                eq_ref = EQUIPES[equipe.numero]
                self.assertEqual(joueur.prenom, eq_ref[ind_joueur][0])
                self.assertEqual(joueur.nom, eq_ref[ind_joueur][1])
                self.assertEqual(joueur.age, eq_ref[ind_joueur][2])
                ind_joueur += 1
