# -*- coding: UTF-8 -*-

"""Team registration endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from .. import services, schemas
from ...core.exception import StatusError
from ..state import get_state

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("", response_model=list[schemas.TeamDTO])
def list_teams(state=Depends(get_state)):
    """Return every registered team."""
    try:
        return services.list_teams(state)
    except LookupError as ex:
        raise HTTPException(status_code=404, detail="No tournament loaded") from ex


@router.post("", response_model=schemas.TeamDTO)
async def add_team(payload: schemas.TeamCreateDTO, state=Depends(get_state)):
    """Register a new team."""
    async with state.lock:
        try:
            dto = services.add_team(state, payload)
        except LookupError as ex:
            raise HTTPException(status_code=404, detail="No tournament loaded") from ex
        except ValueError as ex:
            raise HTTPException(status_code=400, detail=str(ex)) from ex
        await state.progress.publish({"type": "teams_updated"})
        return dto


@router.delete("/{number}")
async def delete_team(number: int, state=Depends(get_state)):
    """Remove a team."""
    async with state.lock:
        try:
            services.delete_team(state, number)
        except LookupError as ex:
            raise HTTPException(status_code=404, detail="No tournament loaded") from ex
        except StatusError as ex:
            raise HTTPException(status_code=400, detail=str(ex)) from ex
        except ValueError as ex:
            raise HTTPException(status_code=400, detail=str(ex)) from ex
        await state.progress.publish({"type": "teams_updated"})
        return {"deleted": number}
