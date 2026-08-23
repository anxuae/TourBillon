# -*- coding: UTF-8 -*-

"""Shared display view endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from .. import schemas, services
from ..state import get_state

router = APIRouter(prefix="/api/display", tags=["display"])


@router.get("/view", response_model=schemas.DisplayViewDTO)
def get_display_view(state=Depends(get_state)):
    """Return the current display view shared by all clients."""
    return services.get_display_view(state)


@router.put("/view", response_model=schemas.DisplayViewDTO)
async def set_display_view(payload: schemas.DisplayViewDTO, state=Depends(get_state)):
    """Update the shared display view and notify display clients."""
    async with state.lock:
        try:
            result = services.set_display_view(state, payload.view)
        except ValueError as ex:
            raise HTTPException(status_code=400, detail=str(ex)) from ex

        await state.progress.publish({"type": "display_view_changed", "view": result["view"]})
        return result