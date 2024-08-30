# -*- coding: UTF-8 -*-

import pytest
import os.path as osp

import data2e2j
from tourbillon import config
from tourbillon.core import team, tournament


def pytest_generate_tests(metafunc):
    """
    Modification de la paramétrisation des tests lors qu'ils sont organisés
    dans une classe: pour chaque jeu de paramètres, tous les tests de
    la classe sont executés dans l'ordre.
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
    print "\nTMPFILE:", path

    def wrap(nom):
        return str(path.join(nom))
    return wrap


@pytest.fixture(scope='session')
def cfg(tmpfile):
    config.CONFIGPATH = tmpfile('config')
    return config.load()


@pytest.fixture(scope="module")
def equ2jn1():
    """
    Equipe n°1 vide (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    return team.Team(tournament.Tournament(data2e2j.EQUIPES_PAR_MANCHE,
                                         data2e2j.POINTS_PAR_MANCHE,
                                         data2e2j.JOUEURS_PAR_EQUIPE), 1)


@pytest.fixture(scope="module")
def part3e2j():
    """
    Partie vide: (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    # On crée un tournoi avec des équipes car Partie n'est qu'un proxy sur Equipe
    trb = tournament.Tournament(data2e2j.EQUIPES_PAR_MANCHE,
                          data2e2j.POINTS_PAR_MANCHE,
                          data2e2j.JOUEURS_PAR_EQUIPE)

    for info_equipe in [data2e2j.JOUEURS_1, data2e2j.JOUEURS_2, data2e2j.JOUEURS_4]:
        eq = trb.ajout_equipe()
        for joueur in info_equipe:
            eq.ajout_joueur(*joueur)
    return trb.ajout_partie()


@pytest.fixture(scope="module")
def trb2e2j():
    """
    Tournoi vide (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    return tournament.nouveau_tournoi(data2e2j.EQUIPES_PAR_MANCHE,
                                   data2e2j.POINTS_PAR_MANCHE,
                                   data2e2j.JOUEURS_PAR_EQUIPE)


@pytest.fixture(scope="module")
def trb4e1j():
    """
    Tournoi avec 5 parties: 4 équipes par manche, 1 joueur par équipe
    """
    return tournament.charger_tournoi(osp.join(osp.dirname(__file__), 'data4e1j.yml'))
