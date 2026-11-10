from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.chroma import chroma_client
from app.db.sqlite import init_db
from app.services.rag_service import ensure_indexed


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    chroma_client.initialize()
    ensure_indexed()
    yield
    chroma_client.close()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "LetsBid API", "docs": "/docs"}
