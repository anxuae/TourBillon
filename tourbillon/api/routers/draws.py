# -*- coding: UTF-8 -*-

"""Draw algorithms metadata endpoint."""

from fastapi import APIRouter

from .. import services, schemas

router = APIRouter(prefix="/api/draws", tags=["draws"])


@router.get("", response_model=list[schemas.DrawInfoDTO])
def list_draws():
    """Return the available draw algorithms and their default options."""
    return services.list_draws()
