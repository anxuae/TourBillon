# -*- coding: UTF-8 -*-

"""Tournament lifecycle endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile

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
async def create_tournament(payload: schemas.TournamentCreateDTO, state=Depends(get_state)):
    """Create a new tournament."""
    async with state.lock:
        services.create_tournament(state, payload)
        await state.progress.publish({"type": "tournament_changed", "action": "created"})
        await state.progress.publish({"type": "teams_updated"})
        return services.tournament_dto(state)


@router.post("/load", response_model=schemas.TournamentDTO)
async def load_tournament(payload: schemas.TournamentLoadDTO, state=Depends(get_state)):
    """Load a tournament from a YAML file (name relative to the save dir)."""
    async with state.lock:
        try:
            services.load_tournament(state, payload.filename)
        except Exception as ex:
            raise HTTPException(status_code=400, detail=str(ex))
        await state.progress.publish({"type": "tournament_changed", "action": "loaded"})
        await state.progress.publish({"type": "teams_updated"})
        return services.tournament_dto(state)


@router.post("/upload", response_model=schemas.TournamentDTO)
async def upload_tournament(
    file: UploadFile = File(...),
    overwrite: bool = False,
    state=Depends(get_state),
):
    """Upload a YAML save file into the save dir and load it.

    Returns HTTP 409 if a file with the same name already exists and
    ``overwrite`` is not set, so the frontend can ask for confirmation.
    """
    content = await file.read()
    async with state.lock:
        try:
            services.upload_tournament(state, file.filename, content, overwrite)
        except FileExistsError as ex:
            raise HTTPException(status_code=409, detail=str(ex)) from ex
        except Exception as ex:
            raise HTTPException(status_code=400, detail=str(ex)) from ex
        await state.progress.publish({"type": "tournament_changed", "action": "uploaded"})
        await state.progress.publish({"type": "teams_updated"})
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


@router.delete("/file", status_code=204)
async def delete_tournament_file(state=Depends(get_state)):
    """Delete the save file of the currently loaded tournament."""
    async with state.lock:
        try:
            services.delete_tournament_file(state)
        except LookupError:
            raise HTTPException(status_code=404, detail="No tournament loaded")
        except FileNotFoundError as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex
        except ValueError as ex:
            raise HTTPException(status_code=400, detail=str(ex)) from ex
        await state.progress.publish({"type": "tournament_changed", "action": "deleted"})
        await state.progress.publish({"type": "teams_updated"})
        return Response(status_code=204)
