# -*- coding: UTF-8 -*-

"""Integration tests for the FastAPI backend."""


# --------------------------------------------------------------------------- #
# Health & draws metadata
# --------------------------------------------------------------------------- #

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_draws(client):
    resp = client.get("/api/draws")
    assert resp.status_code == 200
    names = {d["name"] for d in resp.json()}
    assert names == {"deterministic", "genetic", "random"}


# --------------------------------------------------------------------------- #
# Tournament lifecycle
# --------------------------------------------------------------------------- #

def test_get_tournament_404_when_none(client):
    assert client.get("/api/tournament").status_code == 404


def test_create_tournament(client):
    resp = client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body["teams_by_match"] == 2
    assert body["players_by_team"] == 1
    assert body["status"] == "registration"
    assert body["nb_teams"] == 0


# --------------------------------------------------------------------------- #
# Teams
# --------------------------------------------------------------------------- #

def test_add_and_list_teams(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    resp = client.post(
        "/api/teams",
        json={"number": 1, "players": [{"firstname": "Jean", "lastname": "Dupont"}]},
    )
    assert resp.status_code == 200
    assert resp.json()["number"] == 1

    teams = client.get("/api/teams").json()
    assert len(teams) == 1
    assert teams[0]["players"][0]["firstname"] == "Jean"


def test_add_duplicate_team_returns_400(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    client.post("/api/teams", json={"number": 1, "players": [{"firstname": "A", "lastname": "B"}]})
    resp = client.post("/api/teams", json={"number": 1, "players": []})
    assert resp.status_code == 400


def test_delete_team(registered):
    resp = registered.delete("/api/teams/4")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 4
    assert len(registered.get("/api/teams").json()) == 3


# --------------------------------------------------------------------------- #
# Rounds, draw and results
# --------------------------------------------------------------------------- #

def test_create_round_and_get(registered):
    resp = registered.post("/api/rounds", json={"algorithm": "deterministic"})
    assert resp.status_code == 200, resp.text
    rnd = resp.json()
    assert rnd["number"] == 1
    assert rnd["status"] == "in_progress"
    # 4 teams / 2 per match -> 2 matches, no BYE.
    assert len(rnd["matches"]) == 2
    assert rnd["byes"] == []

    got = registered.get("/api/rounds/1").json()
    assert got["number"] == 1


def test_ranking_after_result(registered):
    registered.post("/api/rounds", json={"algorithm": "deterministic"})
    rnd = registered.get("/api/rounds/1").json()

    # Feed a winning score to the first team of each match.
    for match in rnd["matches"]:
        teams = match["teams"]
        points = {str(teams[0]): 12, str(teams[1]): 6}
        resp = registered.put("/api/rounds/1/matches/1", json={"points": points})
        assert resp.status_code == 200, resp.text

    ranking = registered.get("/api/rankings").json()
    assert len(ranking) == 4
    assert ranking[0]["rank"] == 1
