# -*- coding: UTF-8 -*-

import pytest
from pathlib import Path

from fastapi.testclient import TestClient

from data import t2teams2players
from tourbillon.core import cst, team, tournament
from tourbillon.api.app import create_app
from tourbillon.settings import Settings


@pytest.fixture(autouse=True)
def isolate_settings_file(tmp_path, monkeypatch):
    """Redirect the user settings file into a temp dir for every test.

    Guarantees that no test ever reads or writes the real application settings
    file (``default_settings_path()``), even when ``Settings.load`` or
    ``Settings.save`` are called without an explicit path.
    """
    import tourbillon.settings as settings_mod

    config_file = tmp_path / "settings.yml"
    monkeypatch.setattr(settings_mod, "default_settings_path", lambda: config_file)


def make_stats(specs):
    """Build a ``stats`` mapping from a compact spec.

    :param specs: dict ``{team_number: (points, wins, byes)}``
    :return: statistics mapping compatible with the draws
    """
    stats = {}
    ordered = sorted(
        specs.items(),
        key=lambda kv: (kv[1][1] + kv[1][2], kv[1][0]),
        reverse=True,
    )
    ranking = {num: i + 1 for i, (num, _) in enumerate(ordered)}
    for num, (points, wins, byes) in specs.items():
        stats[num] = {
            cst.STAT_POINTS: points,
            cst.STAT_WINS: wins,
            cst.STAT_BYES: byes,
            cst.STAT_OPPONENTS: [],
            cst.STAT_MATCHES: []
        }
    return stats


@pytest.fixture(scope='session')
def tmpfile(tmpdir_factory):
    path = tmpdir_factory.mktemp('pytest_TourBillon')
    def wrap(nom):
        return str(path.join(nom))
    return wrap


@pytest.fixture(scope="module")
def equ2jn1():
    """
    Equipe n°1 vide (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    return team.Team(tournament.Tournament(t2teams2players.TEAMS_BY_MATCH,
                                           t2teams2players.POINTS_BY_MATCH,
                                           t2teams2players.PLAYERS_BY_TEAM), 1)


@pytest.fixture(scope="module")
def part3e2j():
    """
    Partie vide: (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    trb = tournament.Tournament(t2teams2players.TEAMS_BY_MATCH,
                                t2teams2players.POINTS_BY_MATCH,
                                t2teams2players.PLAYERS_BY_TEAM)

    for info_equipe in [t2teams2players.PLAYERS_1,
                        t2teams2players.PLAYERS_2,
                        t2teams2players.PLAYERS_4]:
        eq = trb.add_team()
        for joueur in info_equipe:
            eq.add_player(*joueur)
    return trb.add_round()


@pytest.fixture(scope="module")
def trb2e2j():
    """
    Tournoi vide (cfg: 2 équipes par manches, 2 joueurs par équipe)
    """
    return tournament.Tournament(t2teams2players.TEAMS_BY_MATCH,
                                 t2teams2players.POINTS_BY_MATCH,
                                 t2teams2players.PLAYERS_BY_TEAM)


@pytest.fixture(scope="module")
def trb4e1j():
    """
    Tournoi avec 5 parties: 4 équipes par manche, 1 joueur par équipe
    """
    return tournament.load(str(Path(__file__).parent / 'data' / 't4teams1players.yml'))


@pytest.fixture
def stats_even():
    """8 teams, all distinct strengths, no history."""
    return make_stats({n: (n * 3, n % 4, 0) for n in range(1, 9)})


@pytest.fixture
def stats_odd():
    """7 teams (an odd number -> one BYE needed for pairs)."""
    return make_stats({n: (n * 3, n % 3, 0) for n in range(1, 8)})


@pytest.fixture
def client(tmp_path):
    """Return a TestClient backed by a fresh app with a temp save dir.

    Both the save directory and the settings file live under ``tmp_path`` so
    the tests never touch the real application settings file.
    """
    settings = Settings(
        {"save_dir": str(tmp_path), "auto_save": False},
        path=str(tmp_path / "settings.yml"),
    )
    app = create_app(settings)
    return TestClient(app)


@pytest.fixture
def registered(client):
    """Create a tournament (2 teams/match, 1 player/team) with 4 teams."""
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    for n in range(1, 5):
        client.post(
            "/api/teams",
            json={"number": n, "players": [{"firstname": f"P{n}", "lastname": "X"}]},
        )
    return client
