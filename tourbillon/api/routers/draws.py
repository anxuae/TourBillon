# -*- coding: UTF-8 -*-

"""Draw algorithms metadata and execution endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from .. import services, schemas
from ...core.exception import DrawError, StatusError
from ..state import get_state

router = APIRouter(prefix="/api/draws", tags=["draws"])


@router.get("", response_model=list[schemas.DrawInfoDTO])
def list_draws(state=Depends(get_state)):
    """Return the available draw algorithms and their effective options."""
    return services.list_draws(state)


@router.post("/run", response_model=schemas.DrawPreviewDTO)
async def run_draw(request: schemas.DrawRequestDTO, state=Depends(get_state)):
    """Run a draw preview without creating a round."""
    async with state.lock:

        async def on_progress(percent, message):
            await state.progress.publish(
                {"type": "draw_progress", "percent": percent, "message": message}
            )

        try:
            dto = await services.preview_draw(state, request, on_progress=on_progress)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail="No tournament loaded") from exc
        except (DrawError, StatusError) as exc:
            await state.progress.publish({"type": "draw_error", "message": str(exc)})
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        await state.progress.publish({"type": "draw_preview_ready"})
        return dto
