from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.documents import DocumentIngestionResponse
from app.services.document_ingestion import SUPPORTED_EXTENSIONS, ingest_document

router = APIRouter(prefix="/documents")


@router.post("/ingest", response_model=DocumentIngestionResponse)
async def ingest_uploaded_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if f".{extension}" not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{extension}'. Supported: {supported}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        return ingest_document(content, file.filename, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse document: {exc}") from exc
