# -*- coding: UTF-8 -*-

import pytest
from datetime import datetime, timedelta

from tourbillon.core import tournoi
from tourbillon.core.exceptions import NumeroError, LimiteError
from tourbillon.core import constantes as cst

import data2e2j

EQUIPES = {1: data2e2j.JOUEURS_1,
           2: data2e2j.JOUEURS_2,
           4: data2e2j.JOUEURS_4,
           5: data2e2j.JOUEURS_5,
           8: data2e2j.JOUEURS_8,  # Changé en n°3
           9: data2e2j.JOUEURS_9}  # Changé en n°6

NB_EQUIPES = len(EQUIPES)


def test_config(trb2e2j):
    assert trb2e2j.equipes_par_manche == data2e2j.EQUIPES_PAR_MANCHE
    assert trb2e2j.joueurs_par_equipe == data2e2j.JOUEURS_PAR_EQUIPE
    assert trb2e2j.points_par_manche == data2e2j.POINTS_PAR_MANCHE


def test_status(trb2e2j):
    assert trb2e2j.statut == cst.T_INSCRIPTION


def test_statistiques(trb2e2j):
    assert trb2e2j.statistiques() == {}
    assert trb2e2j.statistiques([1, 2, 8], 2) == {}


def test_nb_equipes(trb2e2j):
    assert trb2e2j.nb_equipes() == 0
    assert trb2e2j.equipes() == []


def test_equipe_inexistante(trb2e2j):
    with pytest.raises(NumeroError):
        trb2e2j.equipe(4)


def test_suppr_equipe(trb2e2j):
    with pytest.raises(NumeroError):
        trb2e2j.suppr_equipe(10)


def test_nb_parties(trb2e2j):
    assert trb2e2j.nb_parties() == 0
    assert trb2e2j.parties() == []


def test_partie_inexistante(trb2e2j):
    with pytest.raises(NumeroError):
        trb2e2j.partie(3)


def test_partie_courante(trb2e2j):
    assert trb2e2j.partie_courante() == None


def test_suppr_partie(trb2e2j):
    with pytest.raises(NumeroError):
        trb2e2j.suppr_partie(3)


@pytest.mark.parametrize('numero', EQUIPES)
def test_ajout_equipes(trb2e2j, numero):
    assert trb2e2j.ajout_equipe(numero).statut == cst.E_INCOMPLETE


@pytest.mark.parametrize('numero', EQUIPES)
def test_joker(trb2e2j, numero):
    equipe = trb2e2j.equipe(numero)
    equipe.joker = trb2e2j.generer_numero_joker()
    assert equipe.joker < 1001
    assert [e.joker for e in trb2e2j.equipes()].count(equipe.joker) == 1


def test_nb_equipes_apres_inscription(trb2e2j):
    assert trb2e2j.nb_equipes() == NB_EQUIPES


def test_nb_parties_apres_inscription(trb2e2j):
    assert trb2e2j.nb_parties() == 0


@pytest.mark.parametrize('numero,joueurs', EQUIPES.items())
def test_ajout_joueurs(trb2e2j, numero, joueurs):
    e = trb2e2j.equipe(numero)
    for joueur in joueurs:
        j = e.ajout_joueur(joueur[0], joueur[1], joueur[2])
        assert j.prenom == joueur[0]
        assert j.nom == joueur[1]
        assert j.age == joueur[2]
    assert e.statut == cst.E_ATTEND_TIRAGE


def test_nb_joueurs(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.nb_joueurs() == data2e2j.JOUEURS_PAR_EQUIPE


def test_trop_joueurs(trb2e2j):
    for equipe in trb2e2j.equipes():
        with pytest.raises(LimiteError):
            equipe.ajout_joueur("Prenom", "Nom", "00")


def test_changer_numero(trb2e2j):
    # 8 -> 1
    equipe = trb2e2j.equipe(8)
    with pytest.raises(NumeroError):
        trb2e2j.modif_numero_equipe(8, 1)
    # 8 -> 3
    trb2e2j.modif_numero_equipe(8, 3)
    assert equipe.numero == 3
    # 8 a disparu
    with pytest.raises(NumeroError):
        trb2e2j.equipe(8)
    # 9 -> 3
    equipe = trb2e2j.equipe(9)
    trb2e2j.modif_numero_equipe(9, 6)
    assert equipe.numero == 6
    # 9 a disparu
    with pytest.raises(NumeroError):
        trb2e2j.equipe(9)

    # Changer le dictionnaire global pour le reste des tests
    EQUIPES[3] = EQUIPES.pop(8)
    EQUIPES[6] = EQUIPES.pop(9)


def test_adversaires(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.adversaires() == []


def test_total_points(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.points() == 0


def test_total_victoires(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.victoires() == 0


def test_total_forfaits(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.forfaits() == 0


def test_total_parties(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.parties() == 0


def test_total_chapeaux(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.chapeaux() == 0


def test_moyenne_billon(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.moyenne_billon() == 0


def test_min_billon(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.min_billon() == 0


def test_max_billon(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.max_billon() == 0


def test_moyenne_duree(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.moyenne_duree() == timedelta(0)


def test_min_duree(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.min_duree() == timedelta(0)


def test_max_duree(trb2e2j):
    for equipe in trb2e2j.equipes():
        assert equipe.max_duree() == timedelta(0)


def test_enregistrer(trb2e2j, tmpfile):
    assert trb2e2j.modifie
    tournoi.enregistrer_tournoi(tmpfile('trb2e2j.yml'))
    assert not trb2e2j.modifie


def test_date_enregistrement(trb2e2j):
    d = datetime.now()
    d1 = trb2e2j.date_enregistrement - timedelta(0, trb2e2j.date_enregistrement.second, trb2e2j.date_enregistrement.microsecond)
    d2 = d - timedelta(0, d.second, d.microsecond)
    assert d1 == d2


def test_charger(tmpfile):
    tournoi.charger_tournoi(tmpfile('trb2e2j.yml'))
    assert not tournoi.tournoi().modifie


def test_date_chargement():
    d = datetime.now()
    d1 = tournoi.tournoi().date_chargement - timedelta(0, 0, tournoi.tournoi().date_chargement.microsecond)
    d2 = d - timedelta(0, 0, d.microsecond)
    assert d1 == d2


def test_nb_equipes_apres_chargement():
    assert tournoi.tournoi().nb_equipes() == NB_EQUIPES


def test_nb_parties_apres_chargement():
    assert tournoi.tournoi().nb_parties() == 0


def test_nb_joueurs_apres_chargement():
    for equipe in tournoi.tournoi().equipes():
        assert equipe.nb_joueurs() == data2e2j.JOUEURS_PAR_EQUIPE


def test_nom_prenom_joueurs():
    for equipe in tournoi.tournoi().equipes():
        ind_joueur = 0
        for joueur in equipe.joueurs():
            eq_ref = EQUIPES[equipe.numero]
            assert joueur.prenom == eq_ref[ind_joueur][0]
            assert joueur.nom == eq_ref[ind_joueur][1]
            assert joueur.age == eq_ref[ind_joueur][2]
            ind_joueur += 1
