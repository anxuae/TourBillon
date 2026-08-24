# -*- coding: UTF-8 -*-

"""Cross-tournament history endpoints.

Aggregates every save file present in the configured save directory to expose
per-player statistics across the years. Reading stays retro-compatible with the
legacy YAML files.
"""

from fastapi import APIRouter, Depends, HTTPException

from .. import history as history_service
from ..state import get_state

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/tournaments")
def list_history_tournaments(state=Depends(get_state)):
    """Return the list of save files found in the save directory."""
    return history_service.list_tournaments(state.settings.save_dir)


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
