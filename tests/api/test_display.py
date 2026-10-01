# -*- coding: UTF-8 -*-

"""Tests for the shared display-view endpoint (``/api/display/view``)."""


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
