# -*- coding: UTF-8 -*-

"""Ranking endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Query

from .. import services, schemas
from ..state import get_state

router = APIRouter(prefix="/api/rankings", tags=["rankings"])


@router.get("", response_model=list[schemas.RankEntryDTO])
def get_rankings(round_number: int | None = Query(default=None, alias="round"), state=Depends(get_state)):
    """Return the current ranking of the tournament."""
    try:
        return services.ranking_dto(state, state.require_tournament(), round_limit=round_number)
    except LookupError as ex:
        raise HTTPException(status_code=404, detail="No tournament loaded") from ex
