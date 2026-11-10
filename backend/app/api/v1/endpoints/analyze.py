from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.analyze import AnalyzeResponse
from app.services.analyze_pipeline import run_analysis
from app.services.document_ingestion import SUPPORTED_EXTENSIONS
from app.services.gemini_client import GeminiClientError

router = APIRouter(prefix="/analyze")


@router.post("/document", response_model=AnalyzeResponse)
async def analyze_document(file: UploadFile = File(...)):
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
        return run_analysis(content, file.filename, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Analysis failed: {exc}") from exc
