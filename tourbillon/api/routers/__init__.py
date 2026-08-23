# -*- coding: UTF-8 -*-

"""API routers."""

from . import tournament, teams, rounds, rankings, draws, history, settings, display, ws

ROUTERS = (
    tournament.router,
    teams.router,
    rounds.router,
    rankings.router,
    draws.router,
    display.router,
    history.router,
    settings.router,
    ws.router,
)
