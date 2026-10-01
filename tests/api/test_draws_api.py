# -*- coding: UTF-8 -*-

"""Tests for the draws metadata and draw-preview endpoints (``/api/draws``)."""


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


def test_run_draw_endpoint_returns_preview(registered):
    resp = registered.post("/api/draws/run", json={"algorithm": "deterministic"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["algorithm"] == "deterministic"
    assert "matches" in body
    assert "byes" in body
    assert "forfeits" in body
    assert len(body["matches"]) == 2


def test_run_draw_endpoint_does_not_create_round(registered):
    before = registered.get("/api/rounds")
    assert before.status_code == 200, before.text
    assert before.json() == []

    run_resp = registered.post("/api/draws/run", json={"algorithm": "deterministic"})
    assert run_resp.status_code == 200, run_resp.text

    after = registered.get("/api/rounds")
    assert after.status_code == 200, after.text
    assert after.json() == []


def test_create_round_from_draft_creates_round(registered):
    preview = registered.post("/api/draws/run", json={"algorithm": "deterministic"})
    assert preview.status_code == 200, preview.text
    draft = preview.json()

    payload = {
        "matches": [match["teams"] for match in draft["matches"]],
        "byes": draft["byes"],
        "forfeits": draft["forfeits"],
    }
    created = registered.post("/api/rounds", json=payload)
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["number"] == 1
    assert body["status"] == "in_progress"
