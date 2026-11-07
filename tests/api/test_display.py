# -*- coding: UTF-8 -*-

"""Tests for the shared display-view endpoint (``/api/display/view``)."""


def test_get_display_view_default(client):
    resp = client.get("/api/display/view")
    assert resp.status_code == 200
    assert resp.json()["view"] == "display-rankings"
    assert resp.json()["manual"] is False


def test_set_display_view(client):
    resp = client.put("/api/display/view", json={"view": "display-teams"})
    assert resp.status_code == 200
    assert resp.json()["view"] == "display-teams"
    # Defaults to a manual pick (the admin sidebar is the main caller)
    assert resp.json()["manual"] is True

    reread = client.get("/api/display/view")
    assert reread.status_code == 200
    assert reread.json()["view"] == "display-teams"
    assert reread.json()["manual"] is True


def test_set_display_view_auto_clears_manual_flag(client):
    """The auto-switch logic explicitly clears the manual flag.

    A freshly opened Display tab must not keep honoring a stale manual
    choice forever: it should resume recomputing the auto view as soon as
    the frontend auto-switch logic synced a view with ``manual: false``.
    """
    client.put("/api/display/view", json={"view": "display-teams", "manual": True})
    resp = client.put("/api/display/view", json={"view": "display-round", "manual": False})
    assert resp.status_code == 200
    assert resp.json()["manual"] is False

    reread = client.get("/api/display/view")
    assert reread.json()["manual"] is False


def test_set_display_view_rejects_unknown(client):
    resp = client.put("/api/display/view", json={"view": "display-unknown"})
    assert resp.status_code == 400

