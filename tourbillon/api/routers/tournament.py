# -*- coding: UTF-8 -*-

"""Tournament lifecycle endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from .. import services, schemas
from ..state import get_state

router = APIRouter(prefix="/api/tournament", tags=["tournament"])


@router.get("", response_model=schemas.TournamentDTO)
def get_tournament(state=Depends(get_state)):
    """Return the current tournament and its status."""
    try:
        return services.tournament_dto(state)
    except LookupError:
        raise HTTPException(status_code=404, detail="No tournament loaded")


@router.post("", response_model=schemas.TournamentDTO)
async def create_tournament(payload: schemas.TournamentCreate, state=Depends(get_state)):
    """Create a new tournament."""
    async with state.lock:
        services.create_tournament(state, payload)
        return services.tournament_dto(state)


@router.post("/load", response_model=schemas.TournamentDTO)
async def load_tournament(filename: str, state=Depends(get_state)):
    """Load a tournament from a YAML file."""
    async with state.lock:
        try:
            services.load_tournament(state, filename)
        except Exception as ex:
            raise HTTPException(status_code=400, detail=str(ex))
        return services.tournament_dto(state)


@router.post("/save")
async def save_tournament(filename: str | None = None, state=Depends(get_state)):
    """Persist the current tournament to a YAML file."""
    async with state.lock:
        try:
            saved = services.save_tournament(state, filename)
        except LookupError:
            raise HTTPException(status_code=404, detail="No tournament loaded")
        return {"filename": saved}
