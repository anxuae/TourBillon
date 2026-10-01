# -*- coding: UTF-8 -*-

"""Tests for the ``/api/settings`` endpoints."""


def test_get_settings(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    body = resp.json()
    assert "default_draw" in body["tournament"]
    assert "rank_by_buchholz" in body["tournament"]
    assert "rank_by_goal_avg" in body["tournament"]
    assert "rotation_seconds" in body["display"]
    assert "show_ranking_criteria" in body["display"]
    assert "auto_switch" in body["display"]
    assert "draws" in body
    assert "genetic" in body["draws"]


def test_update_settings_persisted(client):
    resp = client.put(
        "/api/settings",
        json={
            "tournament": {
                "rank_by_joker": False,
                "rank_by_buchholz": False,
                "rank_by_goal_avg": False,
            },
            "display": {
                "rotation_seconds": 9,
                "show_ranking_criteria": True,
                "auto_switch": False,
            },
            "draws": {"genetic": {"max_disparity": 5}},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tournament"]["rank_by_joker"] is False
    assert body["tournament"]["rank_by_buchholz"] is False
    assert body["tournament"]["rank_by_goal_avg"] is False
    assert body["display"]["rotation_seconds"] == 9
    assert body["display"]["show_ranking_criteria"] is True
    assert body["display"]["auto_switch"] is False
    assert body["draws"]["genetic"]["max_disparity"] == 5

    # The change is reflected on the next read.
    reread = client.get("/api/settings").json()
    assert reread["tournament"]["rank_by_joker"] is False
    assert reread["tournament"]["rank_by_buchholz"] is False
    assert reread["tournament"]["rank_by_goal_avg"] is False
    assert reread["display"]["rotation_seconds"] == 9
    assert reread["display"]["show_ranking_criteria"] is True
    assert reread["display"]["auto_switch"] is False
    assert reread["draws"]["genetic"]["max_disparity"] == 5


def test_update_settings_ignores_unknown_keys(client):
    resp = client.put("/api/settings", json={"tournament": {"rank_by_joker": False}})
    assert resp.status_code == 200
    assert resp.json()["tournament"]["rank_by_joker"] is False


def test_rankings_use_rank_by_joker_setting(client):
    created = client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    assert created.status_code == 200

    team_1 = client.post(
        "/api/teams",
        json={"number": 1, "joker": 0, "players": [{"firstname": "A", "lastname": "X"}]},
    )
    team_2 = client.post(
        "/api/teams",
        json={"number": 2, "joker": 9, "players": [{"firstname": "B", "lastname": "X"}]},
    )
    assert team_1.status_code == 200
    assert team_2.status_code == 200

    # Same wins/points: with joker enabled, the highest joker comes first.
    ranking = client.get("/api/rankings")
    assert ranking.status_code == 200
    assert ranking.json()[0]["team"] == 2

    disabled = client.put("/api/settings", json={"tournament": {"rank_by_joker": False}})
    assert disabled.status_code == 200

    ranking = client.get("/api/rankings")
    assert ranking.status_code == 200
    assert ranking.json()[0]["team"] == 1
