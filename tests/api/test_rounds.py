# -*- coding: UTF-8 -*-

"""Tests for round creation, result entry and deletion (``/api/rounds``)."""


def test_create_round_and_get(registered, create_round):
    resp = create_round(registered)
    assert resp.status_code == 200, resp.text
    rnd = resp.json()
    assert rnd["number"] == 1
    assert rnd["status"] == "in_progress"
    # 4 teams / 2 per match -> 2 matches, no BYE.
    assert len(rnd["matches"]) == 2
    assert rnd["byes"] == []

    got = registered.get("/api/rounds/1").json()
    assert got["number"] == 1


def test_ranking_after_result(registered, create_round):
    create_round(registered)
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


def test_rankings_round_query_uses_round_limit(registered, create_round):
    first = create_round(registered)
    assert first.status_code == 200, first.text
    first_round = first.json()

    for match in first_round["matches"]:
        teams = match["teams"]
        points = {str(teams[0]): 12, str(teams[1]): 6}
        resp = registered.put("/api/rounds/1/matches/1", json={"points": points})
        assert resp.status_code == 200, resp.text

    ranking_round_1 = registered.get("/api/rankings?round=1")
    assert ranking_round_1.status_code == 200, ranking_round_1.text
    wins_round_1 = sum(row["wins"] for row in ranking_round_1.json())
    assert wins_round_1 == 2

    second = create_round(registered)
    assert second.status_code == 200, second.text
    second_round = second.json()

    for match in second_round["matches"]:
        teams = match["teams"]
        points = {str(teams[0]): 6, str(teams[1]): 12}
        resp = registered.put("/api/rounds/2/matches/1", json={"points": points})
        assert resp.status_code == 200, resp.text

    ranking_current = registered.get("/api/rankings")
    assert ranking_current.status_code == 200, ranking_current.text
    wins_current = sum(row["wins"] for row in ranking_current.json())
    assert wins_current == 4


def test_delete_round(registered, create_round):
    created = create_round(registered)
    assert created.status_code == 200

    deleted = registered.delete("/api/rounds/1")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] == 1

    rounds = registered.get("/api/rounds")
    assert rounds.status_code == 200
    assert rounds.json() == []


def test_delete_unknown_round_returns_400(registered):
    resp = registered.delete("/api/rounds/1")
    assert resp.status_code == 400
