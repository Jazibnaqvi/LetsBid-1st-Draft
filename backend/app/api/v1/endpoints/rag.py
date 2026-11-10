from fastapi import APIRouter, HTTPException

from app.schemas.rag import RagIndexResponse, RagMatchRequest, RagMatchResponse
from app.services.rag_service import index_capability_library, match_requirements

router = APIRouter(prefix="/rag")


@router.post("/index", response_model=RagIndexResponse)
async def index_capabilities(force: bool = False):
    try:
        return index_capability_library(force=force)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/match", response_model=RagMatchResponse)
async def match_capabilities(payload: RagMatchRequest):
    if not payload.requirements:
        raise HTTPException(status_code=400, detail="At least one requirement is required.")
    return match_requirements(payload.requirements, top_k=payload.top_k)
