# -*- coding: UTF-8 -*-

"""Ranking endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from .. import services, schemas
from ..state import get_state

router = APIRouter(prefix="/api/rankings", tags=["rankings"])


@router.get("", response_model=list[schemas.RankEntryDTO])
def get_rankings(state=Depends(get_state)):
    """Return the current ranking of the tournament."""
    try:
        return services.ranking_dto(state.require_tournament())
    except LookupError:
        raise HTTPException(status_code=404, detail="No tournament loaded")
