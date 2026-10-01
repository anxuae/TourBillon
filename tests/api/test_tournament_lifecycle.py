# -*- coding: UTF-8 -*-

"""Tests for the tournament lifecycle endpoints (``/api/tournament``)."""

from pathlib import Path


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
    resp = client.post("/api/tournament/load", json={"filename": Path(saved).name})
    assert resp.status_code == 200
    assert resp.json()["status"] == "registration"


def test_upload_tournament_conflict_and_overwrite(client):
    # Produce a valid save file to reuse as the uploaded content.
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    saved = client.post("/api/tournament/save").json()["filename"]

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


def test_delete_tournament_file(client):
    client.post("/api/tournament", json={"teams_by_match": 2, "players_by_team": 1})
    saved = client.post("/api/tournament/save").json()["filename"]

    resp = client.delete(f"/api/tournament/files/{Path(saved).name}")
    assert resp.status_code == 204

    assert not Path(saved).exists()
    assert client.get("/api/tournament").status_code == 404
