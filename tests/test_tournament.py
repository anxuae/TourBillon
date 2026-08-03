# -*- coding: UTF-8 -*-

import pytest
from datetime import datetime, timedelta

from tourbillon.core import cst, tournament
from tourbillon.core.exception import BoundError

from data import t2teams2players


EQUIPES = {1: t2teams2players.PLAYERS_1,
           2: t2teams2players.PLAYERS_2,
           4: t2teams2players.PLAYERS_4,
           5: t2teams2players.PLAYERS_5,
           8: t2teams2players.PLAYERS_8,  # Changé en n°3
           9: t2teams2players.PLAYERS_9}  # Changé en n°6

NB_EQUIPES = len(EQUIPES)


def test_config(trb2e2j):
    assert trb2e2j.teams_by_match == t2teams2players.TEAMS_BY_MATCH
    assert trb2e2j.players_by_team == t2teams2players.PLAYERS_BY_TEAM
    assert trb2e2j.points_by_match == t2teams2players.POINTS_BY_MATCH


def test_status(trb2e2j):
    assert trb2e2j.status == cst.TOURNAMENT_REGISTRATION


def test_statistiques(trb2e2j):
    assert trb2e2j.statistics() == {}
    assert trb2e2j.statistics([1, 2, 8], 2) == {}


def test_nb_equipes(trb2e2j):
    assert trb2e2j.nb_teams() == 0
    assert trb2e2j.teams() == []


def test_equipe_inexistante(trb2e2j):
    with pytest.raises(ValueError):
        trb2e2j.team(4)


def test_suppr_equipe(trb2e2j):
    with pytest.raises(ValueError):
        trb2e2j.remove_team(10)


def test_nb_parties(trb2e2j):
    assert trb2e2j.nb_rounds() == 0
    assert trb2e2j.rounds() == []


def test_partie_inexistante(trb2e2j):
    with pytest.raises(ValueError):
        trb2e2j.round(3)


def test_partie_courante(trb2e2j):
    assert trb2e2j.current_round() == None


def test_suppr_partie(trb2e2j):
    with pytest.raises(ValueError):
        trb2e2j.remove_round(3)


@pytest.mark.parametrize('numero', EQUIPES)
def test_ajout_equipes(trb2e2j, numero):
    assert trb2e2j.add_team(numero).status == cst.TEAM_INCOMPLETE


@pytest.mark.parametrize('numero', EQUIPES)
def test_joker(trb2e2j, numero):
    equipe = trb2e2j.team(numero)
    equipe.joker = trb2e2j.generate_joker()
    assert equipe.joker < 1001
    assert [e.joker for e in trb2e2j.teams()].count(equipe.joker) == 1


def test_nb_equipes_apres_inscription(trb2e2j):
    assert trb2e2j.nb_teams() == NB_EQUIPES


def test_nb_parties_apres_inscription(trb2e2j):
    assert trb2e2j.nb_rounds() == 0


@pytest.mark.parametrize('numero,joueurs', EQUIPES.items())
def test_add_players(trb2e2j, numero, joueurs):
    e = trb2e2j.team(numero)
    for joueur in joueurs:
        j = e.add_player(joueur[0], joueur[1])
        assert j.firstname == joueur[0]
        assert j.lastname == joueur[1]
    assert e.status == cst.TEAM_WAITING_DRAW


def test_nb_players(trb2e2j):
    for equipe in trb2e2j.teams():
        assert len(equipe.players()) == t2teams2players.PLAYERS_BY_TEAM


def test_too_many_players(trb2e2j):
    for equipe in trb2e2j.teams():
        with pytest.raises(BoundError):
            equipe.add_player("Prenom", "Nom")


def test_update_team_number(trb2e2j):
    # 8 -> 1
    equipe = trb2e2j.team(8)
    with pytest.raises(ValueError):
        trb2e2j.change_team_id(8, 1)
    # 8 -> 3
    trb2e2j.change_team_id(8, 3)
    assert equipe.id == 3
    # 8 a disparu
    with pytest.raises(ValueError):
        trb2e2j.team(8)
    # 9 -> 3
    equipe = trb2e2j.team(9)
    trb2e2j.change_team_id(9, 6)
    assert equipe.id == 6
    # 9 a disparu
    with pytest.raises(ValueError):
        trb2e2j.team(9)

    # Changer le dictionnaire global pour le reste des tests
    EQUIPES[3] = EQUIPES.pop(8)
    EQUIPES[6] = EQUIPES.pop(9)


def test_team_competitors(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.opponents() == []


def test_total_points(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.points() == 0


def test_total_wins(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.wins() == 0


def test_total_forfeits(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.forfeits() == 0


def test_total_rounds(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.rounds() == 0


def test_total_byes(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.byes() == 0


def test_mean_billon(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.average_score() == 0


def test_min_billon(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.min_score() == 0


def test_max_billon(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.max_score() == 0


def test_mean_duration(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.average_duration() == timedelta(0)


def test_min_duration(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.min_duration() == timedelta(0)


def test_max_duration(trb2e2j):
    for equipe in trb2e2j.teams():
        assert equipe.max_duration() == timedelta(0)


def test_save(trb2e2j, tmpfile):
    assert trb2e2j.changed
    tournament.dump(trb2e2j, tmpfile('trb2e2j.yml'))
    assert not trb2e2j.changed


def test_save_date(trb2e2j):
    d = datetime.now()
    d1 = trb2e2j.save_date - \
        timedelta(0, trb2e2j.save_date.second, trb2e2j.save_date.microsecond)
    d2 = d - timedelta(0, d.second, d.microsecond)
    assert d1 == d2


def test_load(tmpfile):
    t = tournament.load(tmpfile('trb2e2j.yml'))
    assert not t.changed


def test_load_date(tmpfile):
    t = tournament.load(tmpfile('trb2e2j.yml'))
    d = datetime.now()
    d1 = t.load_date - timedelta(0, 0, t.load_date.microsecond)
    d2 = d - timedelta(0, 0, d.microsecond)
    assert d1 == d2


def test_nb_teams_after_load(tmpfile):
    t = tournament.load(tmpfile('trb2e2j.yml'))
    assert t.nb_teams() == NB_EQUIPES


def test_nb_rounds_after_load(tmpfile):
    t = tournament.load(tmpfile('trb2e2j.yml'))
    assert t.nb_rounds() == 0


def test_nb_players_after_load(tmpfile):
    t = tournament.load(tmpfile('trb2e2j.yml'))
    for equipe in t.teams():
        assert len(equipe.players()) == t2teams2players.PLAYERS_BY_TEAM


def test_firstname_lastname_after_load(tmpfile):
    t = tournament.load(tmpfile('trb2e2j.yml'))
    for equipe in t.teams():
        ind_joueur = 0
        for joueur in equipe.players():
            eq_ref = EQUIPES[equipe.id]
            assert joueur.firstname == eq_ref[ind_joueur][0]
            assert joueur.lastname == eq_ref[ind_joueur][1]
            ind_joueur += 1
