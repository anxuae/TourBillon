# -*- coding: UTF-8 -*-

"""Draw algorithms metadata endpoint."""

from fastapi import APIRouter, Depends

from .. import services, schemas
from ..state import get_state

router = APIRouter(prefix="/api/draws", tags=["draws"])


@router.get("", response_model=list[schemas.DrawInfoDTO])
def list_draws(state=Depends(get_state)):
    """Return the available draw algorithms and their effective options."""
    return services.list_draws(state)
