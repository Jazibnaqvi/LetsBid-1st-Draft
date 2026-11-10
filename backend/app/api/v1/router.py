from fastapi import APIRouter

from app.api.v1.endpoints import analyze, compliance, documents, go_nogo, health, ner, proposals, rag

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(ner.router, tags=["ner"])
api_router.include_router(rag.router, tags=["rag"])
api_router.include_router(compliance.router, tags=["compliance"])
api_router.include_router(go_nogo.router, tags=["go-nogo"])
api_router.include_router(proposals.router, tags=["proposals"])
api_router.include_router(analyze.router, tags=["analyze"])
