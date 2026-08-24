# -*- coding: UTF-8 -*-

"""Integration tests for the FastAPI backend."""


# --------------------------------------------------------------------------- #
# Health & draws metadata
# --------------------------------------------------------------------------- #

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_version(client):
    import tourbillon

    resp = client.get("/api/version")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == tourbillon.__long_name__
    assert body["version"] == tourbillon.__version__


def test_list_draws(client):
    resp = client.get("/api/draws")
    assert resp.status_code == 200
    names = {d["name"] for d in resp.json()}
    assert names == {"deterministic", "genetic", "random"}


def test_list_draws_exposes_effective_config(client):
    resp = client.get("/api/draws")
    assert resp.status_code == 200
    genetic = next(d for d in resp.json() if d["name"] == "genetic")
    # By default the effective config matches the algorithm defaults.
    assert genetic["config"] == genetic["default"]


def test_get_settings(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    body = resp.json()
    assert "default_draw" in body["tournament"]
    assert "rank_by_buchholz" in body["tournament"]
    assert "rank_by_goal_avg" in body["tournament"]
    assert "rotation_seconds" in body["display"]
    assert "draws" in body
    assert "genetic" in body["draws"]


def test_update_settings_persisted(client):
    resp = client.put(
        "/api/settings",
        json={"tournament": {"rank_by_joker": False, "rank_by_buchholz": False, "rank_by_goal_avg": False},
              "display": {"rotation_seconds": 9},
              "draws": {"genetic": {"max_disparity": 5}}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tournament"]["rank_by_joker"] is False
    assert body["tournament"]["rank_by_buchholz"] is False
    assert body["tournament"]["rank_by_goal_avg"] is False
    assert body["display"]["rotation_seconds"] == 9
    assert body["draws"]["genetic"]["max_disparity"] == 5

    # The change is reflected on the next read.
    reread = client.get("/api/settings").json()
    assert reread["tournament"]["rank_by_joker"] is False
    assert reread["tournament"]["rank_by_buchholz"] is False
    assert reread["tournament"]["rank_by_goal_avg"] is False
    assert reread["display"]["rotation_seconds"] == 9
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


# --------------------------------------------------------------------------- #
# Shared display view
# --------------------------------------------------------------------------- #

def test_get_display_view_default(client):
    resp = client.get("/api/display/view")
    assert resp.status_code == 200
    assert resp.json()["view"] == "display-rankings"


def test_set_display_view(client):
    resp = client.put("/api/display/view", json={"view": "display-teams"})
    assert resp.status_code == 200
    assert resp.json()["view"] == "display-teams"

    reread = client.get("/api/display/view")
    assert reread.status_code == 200
    assert reread.json()["view"] == "display-teams"


def test_set_display_view_rejects_unknown(client):
    resp = client.put("/api/display/view", json={"view": "display-unknown"})
    assert resp.status_code == 400


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


def test_load_tournament_by_filename(client):
    # Create, save, then reload by bare filename (resolved against save_dir).
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    saved = client.post("/api/tournament/save").json()["filename"]
    from pathlib import Path

    resp = client.post("/api/tournament/load", json={"filename": Path(saved).name})
    assert resp.status_code == 200
    assert resp.json()["status"] == "registration"


def test_upload_tournament_conflict_and_overwrite(client):
    # Produce a valid save file to reuse as the uploaded content.
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    saved = client.post("/api/tournament/save").json()["filename"]
    from pathlib import Path

    content = Path(saved).read_bytes()

    # First upload under a new name succeeds.
    resp = client.post(
        "/api/tournament/upload",
        files={"file": ("uploaded.yml", content, "application/x-yaml")},
    )
    assert resp.status_code == 200

    # Same name without overwrite conflicts.
    resp = client.post(
        "/api/tournament/upload",
        files={"file": ("uploaded.yml", content, "application/x-yaml")},
    )
    assert resp.status_code == 409

    # With overwrite it succeeds again.
    resp = client.post(
        "/api/tournament/upload?overwrite=true",
        files={"file": ("uploaded.yml", content, "application/x-yaml")},
    )
    assert resp.status_code == 200


def test_upload_tournament_rejects_non_yaml(client):
    resp = client.post(
        "/api/tournament/upload",
        files={"file": ("bad.txt", b"nope", "text/plain")},
    )
    assert resp.status_code == 400


def test_delete_current_tournament_file(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    saved = client.post("/api/tournament/save").json()["filename"]

    resp = client.delete("/api/tournament/file")
    assert resp.status_code == 204

    from pathlib import Path

    assert not Path(saved).exists()
    assert client.get("/api/tournament").status_code == 404


def test_delete_current_tournament_file_without_filename(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    resp = client.delete("/api/tournament/file")
    assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# Teams
# --------------------------------------------------------------------------- #

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


def test_delete_team(registered):
    resp = registered.delete("/api/teams/4")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 4
    assert len(registered.get("/api/teams").json()) == 3


def test_delete_team_rejected_when_linked_to_rounds(registered):
    created = registered.post("/api/rounds", json={"algorithm": "deterministic"})
    assert created.status_code == 200

    resp = registered.delete("/api/teams/4")
    assert resp.status_code == 400


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


def test_rankings_round_query_uses_round_limit(registered):
    first = registered.post("/api/rounds", json={"algorithm": "deterministic"})
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

    second = registered.post("/api/rounds", json={"algorithm": "deterministic"})
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


def test_delete_round(registered):
    created = registered.post("/api/rounds", json={"algorithm": "deterministic"})
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
