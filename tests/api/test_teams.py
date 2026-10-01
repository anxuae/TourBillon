# -*- coding: UTF-8 -*-

"""Tests for the teams endpoints (``/api/teams``)."""


def test_add_and_list_teams(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    resp = client.post(
        "/api/teams",
        json={"number": 1, "joker": 123, "players": [{"firstname": "Jean", "lastname": "Dupont"}]},
    )
    assert resp.status_code == 200
    assert resp.json()["number"] == 1
    assert resp.json()["joker"] == 123

    teams = client.get("/api/teams").json()
    assert len(teams) == 1
    assert teams[0]["players"][0]["firstname"] == "Jean"
    assert teams[0]["joker"] == 123


def test_add_duplicate_team_returns_400(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    client.post("/api/teams", json={"number": 1, "players": [{"firstname": "A", "lastname": "B"}]})
    resp = client.post("/api/teams", json={"number": 1, "players": []})
    assert resp.status_code == 400


def test_update_team_completes_players(client):
    """An incomplete team can be completed through the update endpoint."""
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    client.post("/api/teams", json={"number": 1, "players": []})
    assert client.get("/api/teams").json()[0]["status"] == "incomplete"

    resp = client.put(
        "/api/teams/1",
        json={"joker": 7, "players": [{"firstname": "Jean", "lastname": "Dupont"}]},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] != "incomplete"
    assert resp.json()["joker"] == 7
    assert resp.json()["players"][0]["lastname"] == "Dupont"


def test_update_team_replaces_players(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    client.post("/api/teams", json={"number": 1, "players": [{"firstname": "A", "lastname": "B"}]})

    resp = client.put("/api/teams/1", json={"players": [{"firstname": "C", "lastname": "D"}]})
    assert resp.status_code == 200
    players = resp.json()["players"]
    assert len(players) == 1
    assert players[0]["firstname"] == "C"


def test_update_unknown_team_returns_404(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    resp = client.put("/api/teams/99", json={"joker": 1})
    assert resp.status_code == 404


def test_update_team_too_many_players_returns_400(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    client.post("/api/teams", json={"number": 1, "players": []})
    resp = client.put(
        "/api/teams/1",
        json={"players": [
            {"firstname": "A", "lastname": "B"},
            {"firstname": "C", "lastname": "D"},
        ]},
    )
    assert resp.status_code == 400


def test_delete_team(registered):
    resp = registered.delete("/api/teams/4")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 4
    assert len(registered.get("/api/teams").json()) == 3


def test_delete_team_rejected_when_linked_to_rounds(registered, create_round):
    created = create_round(registered)
    assert created.status_code == 200

    resp = registered.delete("/api/teams/4")
    assert resp.status_code == 400
