# -*- coding: UTF-8 -*-

import pytest
import os.path as osp

from data import t2teams2players
from tourbillon import config
from tourbillon.core import player, team, tournament


def pytest_generate_tests(metafunc):
    """
    Modification of the configuration of tests when they are organized in a class: for each set of parameters,
    all the class tests are carried out in order.
    """
    if metafunc.cls and metafunc.cls.scenarios:
        idlist = []
        argvalues = []
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario[0])
            items = scenario[1].items()
            argnames = [x[0] for x in items]
            argvalues.append(([x[1] for x in items]))
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


@pytest.fixture(scope='session')
def tmpfile(tmpdir_factory):
    path = tmpdir_factory.mktemp('pytest_TourBillon')
    def wrap(nom):
        return str(path.join(nom))
    return wrap


@pytest.fixture(scope='session')
def cfg(tmpfile):
    return config.TypedConfigParser(tmpfile('config'))


@pytest.fixture(scope='session', autouse=True)
def players_history(tmpfile):
    return player.PlayerHistory(tmpfile('history'))


@pytest.fixture(scope="module")
def namespace():
    class NameSpace:
        def __init__(self):
            self.current_draw = None
    yield NameSpace()


@pytest.fixture(scope="module")
def equ2jn1():
    """
    Equipe n°1 vide (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    return team.Team(tournament.Tournament(t2teams2players.EQUIPES_PAR_MANCHE,
                                           t2teams2players.POINTS_PAR_MANCHE,
                                           t2teams2players.JOUEURS_PAR_EQUIPE), 1)


@pytest.fixture(scope="module")
def part3e2j():
    """
    Partie vide: (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    trb = tournament.Tournament(t2teams2players.EQUIPES_PAR_MANCHE,
                                t2teams2players.POINTS_PAR_MANCHE,
                                t2teams2players.JOUEURS_PAR_EQUIPE)

    for info_equipe in [t2teams2players.JOUEURS_1,
                        t2teams2players.JOUEURS_2,
                        t2teams2players.JOUEURS_4]:
        eq = trb.ajout_equipe()
        for joueur in info_equipe:
            eq.ajout_joueur(*joueur)
    return trb.ajout_partie()


@pytest.fixture(scope="module")
def trb2e2j():
    """
    Tournoi vide (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    return tournament.nouveau_tournoi(t2teams2players.EQUIPES_PAR_MANCHE,
                                      t2teams2players.POINTS_PAR_MANCHE,
                                      t2teams2players.JOUEURS_PAR_EQUIPE)


@pytest.fixture(scope="module")
def trb4e1j():
    """
    Tournoi avec 5 parties: 4 équipes par manche, 1 joueur par équipe
    """
    return tournament.charger_tournoi(osp.join(osp.dirname(__file__), 'data', 't4teams1players.yml'))
