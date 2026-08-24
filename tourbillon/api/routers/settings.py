# -*- coding: UTF-8 -*-

"""Application settings endpoints."""

from fastapi import APIRouter, Depends

from .. import services, schemas
from ..state import get_state

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=schemas.SettingsDTO)
def get_settings(state=Depends(get_state)):
    """Return the current application settings."""
    return services.get_settings(state)


@router.put("", response_model=schemas.SettingsDTO)
async def update_settings(update: schemas.SettingsUpdateDTO, state=Depends(get_state)):
    """Update the application settings and persist them to disk."""
    async with state.lock:
        settings = services.update_settings(state, update.model_dump(exclude_unset=True))
    await state.progress.publish({"type": "settings_updated"})
    return settings
