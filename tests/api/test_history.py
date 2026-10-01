# -*- coding: UTF-8 -*-

"""Integration tests for the ``/api/history`` endpoints."""

import json
from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from tourbillon.api.app import create_app
from tourbillon.settings import Settings


def _ndjson(resp):
    """Parse a streamed NDJSON response body into a list of dicts."""
    return [json.loads(line) for line in resp.text.splitlines() if line.strip()]


def _make_client(save_dir):
    """Return a fresh TestClient backed by ``save_dir`` as the save directory."""
    settings = Settings(
        {"save_dir": str(save_dir), "auto_save": False},
        path=str(save_dir / "settings.yml"),
    )
    app = create_app(settings)
    return TestClient(app)


def _create_round(client, algorithm="deterministic"):
    """Run a draw preview then commit it as a new round.

    Not reused from the shared ``create_round`` fixture (see
    ``tests/conftest.py``) because this module needs several independent
    ``TestClient`` instances sharing the same save directory (one per
    simulated tournament edition), while the fixture only wraps a single
    client.
    """
    preview = client.post("/api/draws/run", json={"algorithm": algorithm})
    assert preview.status_code == 200, preview.text
    draft = preview.json()
    resp = client.post(
        "/api/rounds",
        json={
            "matches": [match["teams"] for match in draft["matches"]],
            "byes": draft["byes"],
            "forfeits": draft["forfeits"],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _build_tournament(client, teams, filepath):
    """Create a tournament, register ``teams`` and play a full round.

    :param teams: list of ``(number, [(firstname, lastname), ...], joker)``
    :param filepath: explicit absolute path to save under (the save endpoint
        uses a given filename as-is instead of joining it with the save
        directory, and otherwise derives one from the current timestamp,
        which is not granular enough to guarantee two editions saved back to
        back land in distinct files)
    :return: the base filename the tournament was saved under
    """
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    for number, players, joker in teams:
        resp = client.post(
            "/api/teams",
            json={
                "number": number,
                "joker": joker,
                "players": [{"firstname": f, "lastname": l} for f, l in players],
            },
        )
        assert resp.status_code == 200, resp.text

    rnd = _create_round(client)
    # Give a clear winner/loser on every match so rankings are deterministic.
    # The ``match`` path segment is only kept for REST symmetry by the backend
    # (the match is actually identified by the team ids in the payload), so
    # any value works here.
    for index, match in enumerate(rnd["matches"], start=1):
        match_teams = match["teams"]
        points = {str(match_teams[0]): 12, str(match_teams[1]): 6}
        resp = client.put(f"/api/rounds/1/matches/{index}", json={"points": points})
        assert resp.status_code == 200, resp.text

    saved = client.post("/api/tournament/save", params={"filename": str(filepath)}).json()["filename"]
    return Path(saved).name


@pytest.fixture
def save_dir(tmp_path):
    return tmp_path


@pytest.fixture
def two_tournaments(save_dir):
    """Save two editions sharing one player spelled differently in each.

    Edition 1: teams 1-2, with "José Gómez" (accented spelling).
    Edition 2: teams 1-2, with "Jose Gomez" (plain ASCII spelling) plus a
    distinct player only present in that edition.
    """
    client1 = _make_client(save_dir)
    filename1 = _build_tournament(
        client1,
        [
            (1, [("José", "Gómez")], 0),
            (2, [("Alice", "Martin")], 0),
        ],
        save_dir / "edition1.yml",
    )

    client2 = _make_client(save_dir)
    filename2 = _build_tournament(
        client2,
        [
            (1, [("Jose", "Gomez")], 0),
            (2, [("Bob", "Durand")], 0),
        ],
        save_dir / "edition2.yml",
    )

    return save_dir, filename1, filename2


# --------------------------------------------------------------------------- #
# /api/history/tournaments
# --------------------------------------------------------------------------- #

def test_list_history_tournaments_streams_every_save_file(two_tournaments):
    save_dir, filename1, filename2 = two_tournaments
    client = _make_client(save_dir)

    resp = client.get("/api/history/tournaments")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/x-ndjson")

    items = _ndjson(resp)
    filenames = {item["filename"] for item in items}
    assert filenames == {filename1, filename2}
    for item in items:
        assert item["nb_teams"] == 2
        assert item["nb_rounds"] == 1


def test_list_history_tournaments_empty_dir(save_dir):
    client = _make_client(save_dir)
    resp = client.get("/api/history/tournaments")
    assert resp.status_code == 200
    assert _ndjson(resp) == []


# --------------------------------------------------------------------------- #
# /api/history/tournaments/{filename}/players
# --------------------------------------------------------------------------- #

def test_get_history_tournament_players(two_tournaments):
    save_dir, filename1, _ = two_tournaments
    client = _make_client(save_dir)

    resp = client.get(f"/api/history/tournaments/{filename1}/players")
    assert resp.status_code == 200
    body = resp.json()
    assert body["filename"] == filename1
    assert body["nb_teams"] == 2
    assert body["nb_rounds"] == 1

    names = {player["name"] for player in body["players"]}
    assert names == {"José Gómez", "Alice Martin"}
    # The winning team (12 points) outranks the losing one (6 points).
    ranks = {player["name"]: player["rank"] for player in body["players"]}
    assert ranks["José Gómez"] == 1
    assert ranks["Alice Martin"] == 2


def test_get_history_tournament_players_unknown_filename(save_dir):
    client = _make_client(save_dir)
    resp = client.get("/api/history/tournaments/does-not-exist.yml/players")
    assert resp.status_code == 404


# --------------------------------------------------------------------------- #
# /api/history/players
# --------------------------------------------------------------------------- #

def test_list_history_players_merges_accents_and_case(two_tournaments):
    save_dir, _, _ = two_tournaments
    client = _make_client(save_dir)

    resp = client.get("/api/history/players")
    assert resp.status_code == 200
    players = resp.json()

    names = {player["name"] for player in players}
    # "José Gómez" and "Jose Gomez" merge into a single entry; the two
    # remaining players (one per edition) stay distinct.
    assert names == {"José Gómez", "Alice Martin", "Bob Durand"}

    gomez = next(p for p in players if p["name"] == "José Gómez")
    assert gomez["participations"] == 2
    # Each edition's winning team scored 12 points and 1 win.
    assert gomez["wins"] == 2
    assert gomez["points"] == 24
    assert sorted(gomez["years"]) == sorted(gomez["years"])
    assert len(gomez["years"]) == 2

    alice = next(p for p in players if p["name"] == "Alice Martin")
    assert alice["participations"] == 1


def test_list_history_players_empty_dir(save_dir):
    client = _make_client(save_dir)
    resp = client.get("/api/history/players")
    assert resp.status_code == 200
    assert resp.json() == []


# --------------------------------------------------------------------------- #
# /api/history/players/{name}
# --------------------------------------------------------------------------- #

def test_get_history_player_detail_merges_editions(two_tournaments):
    save_dir, _, _ = two_tournaments
    client = _make_client(save_dir)

    resp = client.get("/api/history/players/Jose Gomez")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "José Gómez"
    assert len(body["editions"]) == 2

    raw_names = {edition["raw_name"] for edition in body["editions"]}
    assert raw_names == {"José Gómez", "Jose Gomez"}
    for edition in body["editions"]:
        assert edition["wins"] == 1
        assert edition["points"] == 12
        assert edition["rank"] == 1


def test_get_history_player_detail_unknown_player(two_tournaments):
    save_dir, _, _ = two_tournaments
    client = _make_client(save_dir)

    resp = client.get("/api/history/players/Nobody Here")
    assert resp.status_code == 404
