# -*- coding: UTF-8 -*-

"""Tests for the health-check and version endpoints."""


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
