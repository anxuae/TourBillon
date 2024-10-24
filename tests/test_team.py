# -*- coding: UTF-8 -*-

import pytest
from datetime import timedelta

from tourbillon.core import cst
from tourbillon.core.exception import StatusError
from data import t2teams2players


def test_statistiques(equ2jn1, adversaires=[], points=0, victoires=0, forfaits=0, parties=0,
                      chapeaux=0, moy_billon=0, min_billon=0, max_billon=0,
                      moy_duree=timedelta(0), min_duree=timedelta(0), max_duree=timedelta(0)):
    assert equ2jn1.adversaires() == adversaires
    assert equ2jn1.points() == points
    assert equ2jn1.victoires() == victoires
    assert equ2jn1.forfaits() == forfaits
    assert equ2jn1.parties() == parties
    assert equ2jn1.chapeaux() == chapeaux
    assert equ2jn1.moyenne_billon() == moy_billon
    assert equ2jn1.min_billon() == min_billon
    assert equ2jn1.max_billon() == max_billon
    assert equ2jn1.moyenne_duree() == moy_duree
    assert equ2jn1.min_duree() == min_duree
    assert equ2jn1.max_duree() == max_duree


def test_statut_equipe_vide(equ2jn1):
    assert equ2jn1.statut == cst.E_INCOMPLETE


def test_nb_joueurs_equipe_vide(equ2jn1):
    assert equ2jn1.nb_joueurs == 0


@pytest.mark.parametrize('joueur', t2teams2players.JOUEURS_1)
def test_ajouter_joueur(equ2jn1, joueur):
    equ2jn1.ajout_joueur(*joueur)


def test_statut_equipe_complete(equ2jn1):
    assert equ2jn1.statut == cst.E_ATTEND_TIRAGE


def test_nb_joueurs_equipe_complete(equ2jn1):
    assert equ2jn1.nb_joueurs == t2teams2players.JOUEURS_PAR_EQUIPE


def test_statistiques_equipe_complete(equ2jn1):
    test_statistiques(equ2jn1)


class TestAjoutParties:

    scenarios = [('parie%s' % i, {'data_partie': t2teams2players.PARTIES_1[i], 'data_stat': t2teams2players.STATISTIQUES_1[i]})
                 for i in range(len(t2teams2players.PARTIES_1))]
    stat_precedent = None

    def test_statut(self, equ2jn1, data_partie, data_stat):
        assert equ2jn1.statut == cst.E_ATTEND_TIRAGE

    def test_ajout_partie(self, equ2jn1, data_partie, data_stat):
        if data_partie['etat'] != cst.FORFAIT and data_partie['etat'] != cst.CHAPEAU:
            # L'état est inconnu et la manche est en cours
            equ2jn1._ajout_partie(data_partie['debut'], data_partie['adversaires'], None, 1)
            with pytest.raises(StatusError):
                equ2jn1._ajout_partie(data_partie['debut'], data_partie['adversaires'], None, 1)
        else:
            equ2jn1._ajout_partie(data_partie['debut'], data_partie['adversaires'], data_partie['etat'], 1)

    def test_statut_apres_partie(self, equ2jn1, data_partie, data_stat):
        if data_partie['etat'] != cst.FORFAIT and data_partie['etat'] != cst.CHAPEAU:
            assert equ2jn1.statut == cst.E_EN_COURS
        else:
            assert equ2jn1.statut == cst.E_ATTEND_TIRAGE

    def test_statistiques_avant_resultat(self, equ2jn1, data_partie, data_stat):
        if data_partie['etat'] != cst.FORFAIT and data_partie['etat'] != cst.CHAPEAU:
            if not TestAjoutParties.stat_precedent:
                test_statistiques(equ2jn1, adversaires=data_stat['adversaires'],
                                  parties=data_stat['parties'])
            else:
                test_statistiques(equ2jn1, adversaires=data_stat['adversaires'],
                                  points=TestAjoutParties.stat_precedent['points'],
                                  victoires=TestAjoutParties.stat_precedent['victoires'],
                                  forfaits=TestAjoutParties.stat_precedent['forfaits'],
                                  parties=data_stat['parties'],
                                  chapeaux=TestAjoutParties.stat_precedent['chapeaux'],
                                  moy_billon=TestAjoutParties.stat_precedent['moy_billon'],
                                  min_billon=TestAjoutParties.stat_precedent['min_billon'],
                                  max_billon=TestAjoutParties.stat_precedent['max_billon'],
                                  moy_duree=TestAjoutParties.stat_precedent['moy_duree'],
                                  min_duree=TestAjoutParties.stat_precedent['min_duree'],
                                  max_duree=TestAjoutParties.stat_precedent['max_duree'])
        else:
            test_statistiques(equ2jn1, **data_stat)

    def test_modifier_partie(self, equ2jn1, data_partie, data_stat):
        if data_partie['etat'] != cst.FORFAIT and data_partie['etat'] != cst.CHAPEAU:
            fin = data_partie['debut'] + data_partie['duree']
        else:
            # L'équipe est CHAPEAU ou FORFAIT
            fin = None
        with pytest.raises(ValueError):
            equ2jn1._modif_partie(10, data_partie['points'], data_partie['etat'], fin)
        equ2jn1._modif_partie(t2teams2players.PARTIES_1.index(data_partie) + 1,
                              data_partie['points'], data_partie['etat'], fin)

    def test_statistiques_apres_resultat(self, equ2jn1, data_partie, data_stat):
        test_statistiques(equ2jn1, **data_stat)
        TestAjoutParties.stat_precedent = data_stat
