from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import ValidationError

from app.schemas.ner import NerDocumentExtractionResponse, NerExtractionResponse, NerTextRequest
from app.services.document_ingestion import SUPPORTED_EXTENSIONS, ingest_document
from app.services.gemini_client import GeminiClientError
from app.services.ner_extraction import extract_entities

router = APIRouter(prefix="/ner")


@router.post("/extract", response_model=NerExtractionResponse)
async def extract_ner_from_text(payload: NerTextRequest):
    try:
        return extract_entities(text=payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail=f"NER response validation failed: {exc}") from exc


@router.post("/extract-document", response_model=NerDocumentExtractionResponse)
async def extract_ner_from_document(file: UploadFile = File(...)):
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
        ingestion = ingest_document(content, file.filename, file.content_type)
        ner = extract_entities(ingestion=ingestion)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail=f"NER response validation failed: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to process document: {exc}") from exc

    return NerDocumentExtractionResponse(ingestion=ingestion, ner=ner)
