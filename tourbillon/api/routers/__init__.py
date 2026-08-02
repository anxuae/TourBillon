# -*- coding: UTF-8 -*-

"""API routers."""

from . import tournament, teams, rounds, rankings, draws, history, ws

ROUTERS = (
    tournament.router,
    teams.router,
    rounds.router,
    rankings.router,
    draws.router,
    history.router,
    ws.router,
)
