# -*- coding: UTF-8 -*-

"""Cross-tournament history endpoints.

Aggregates every save file present in the configured save directory to expose
per-player statistics across the years. Reading stays retro-compatible with the
legacy YAML files.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from .. import history as history_service
from ..state import get_state

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/tournaments")
def list_history_tournaments(state=Depends(get_state)):
    """Stream the metadata of every save file found in the save directory.

    Parsing every save file can be slow (dozens of YAML archives), so the
    response is streamed as newline-delimited JSON (NDJSON): the frontend
    displays each entry as soon as it arrives instead of waiting for the whole
    history to be parsed. Starlette runs the underlying sync generator in a
    threadpool (see ``starlette.concurrency.iterate_in_threadpool``), so this
    does not block the event loop between items.
    """

    def generate():
        for item in history_service.iter_tournament_metadata(state.settings.save_dir):
            yield json.dumps(item, default=str) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@router.get("/tournaments/{filename}/players")
def get_history_tournament_players(filename: str, state=Depends(get_state)):
    """Return the per-player statistics of a single save file."""
    data = history_service.tournament_players(
        state.settings.save_dir,
        filename,
        with_wins=state.settings.rank_by_wins,
        with_joker=state.settings.rank_by_joker,
        with_buchholz=state.settings.rank_by_buchholz,
        with_goal_avg=state.settings.rank_by_goal_avg,
    )
    if data is None:
        raise HTTPException(status_code=404, detail=f"Unknown save file '{filename}'")
    return data


@router.get("/players")
def list_history_players(state=Depends(get_state)):
    """Return aggregated per-player statistics across every save file."""
    return history_service.aggregate_players(
        state.settings.save_dir,
        with_wins=state.settings.rank_by_wins,
        with_joker=state.settings.rank_by_joker,
        with_buchholz=state.settings.rank_by_buchholz,
        with_goal_avg=state.settings.rank_by_goal_avg,
    )


@router.get("/players/{name}")
def get_history_player(name: str, state=Depends(get_state)):
    """Return the year-by-year detail of a single player."""
    data = history_service.player_detail(
        state.settings.save_dir,
        name,
        with_wins=state.settings.rank_by_wins,
        with_joker=state.settings.rank_by_joker,
        with_buchholz=state.settings.rank_by_buchholz,
        with_goal_avg=state.settings.rank_by_goal_avg,
    )
    if data is None:
        raise HTTPException(status_code=404, detail=f"Unknown player '{name}'")
    return data
