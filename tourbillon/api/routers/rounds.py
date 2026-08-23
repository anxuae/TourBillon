# -*- coding: UTF-8 -*-

"""Round and draw execution endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from .. import services, schemas
from ...core.exception import DrawError, StatusError
from ..state import get_state

router = APIRouter(prefix="/api/rounds", tags=["rounds"])


@router.get("", response_model=list[schemas.RoundDTO])
def list_rounds(state=Depends(get_state)):
    """Return every round of the tournament."""
    try:
        return services.list_rounds(state)
    except LookupError:
        raise HTTPException(status_code=404, detail="No tournament loaded")


@router.get("/{number}", response_model=schemas.RoundDTO)
def get_round(number: int, state=Depends(get_state)):
    """Return a single round and its matches."""
    try:
        return services.get_round(state, number)
    except LookupError:
        raise HTTPException(status_code=404, detail="No tournament loaded")
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.post("", response_model=schemas.RoundDTO)
async def create_round(request: schemas.DrawRequestDTO, state=Depends(get_state)):
    """Create a new round by running a draw (broadcasts progress on /ws/draw)."""
    async with state.lock:

        async def on_progress(percent, message):
            await state.progress.publish(
                {"type": "draw_progress", "percent": percent, "message": message}
            )

        try:
            dto = await services.create_round(state, request, on_progress=on_progress)
        except LookupError:
            raise HTTPException(status_code=404, detail="No tournament loaded")
        except (DrawError, StatusError) as ex:
            await state.progress.publish({"type": "draw_error", "message": str(ex)})
            raise HTTPException(status_code=409, detail=str(ex))

        await state.progress.publish({"type": "round_created", "round": dto.number})
        return dto


@router.put("/{number}/matches/{match}", response_model=schemas.RoundDTO)
async def set_result(number: int, match: int, result: schemas.MatchResultDTO, state=Depends(get_state)):
    """Register the score of a match (``match`` is kept for REST symmetry)."""
    async with state.lock:
        try:
            dto = services.set_match_result(state, number, result)
        except LookupError:
            raise HTTPException(status_code=404, detail="No tournament loaded")
        except Exception as ex:
            raise HTTPException(status_code=400, detail=str(ex))
        await state.progress.publish({"type": "score_updated", "round": number})
        return dto


@router.delete("/{number}")
async def delete_round(number: int, state=Depends(get_state)):
    """Delete an existing round."""
    async with state.lock:
        try:
            services.delete_round(state, number)
        except LookupError:
            raise HTTPException(status_code=404, detail="No tournament loaded")
        except ValueError as ex:
            raise HTTPException(status_code=400, detail=str(ex))

        await state.progress.publish({"type": "round_deleted", "round": number})
        return {"deleted": number}
