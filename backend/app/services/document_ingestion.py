from io import BytesIO

import fitz
from docx import Document

from app.schemas.documents import DocumentIngestionResponse, DocumentMetadata, TextSegment

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _build_response(
    *,
    filename: str,
    file_type: str,
    mime_type: str,
    size_bytes: int,
    segments: list[TextSegment],
    page_count: int | None = None,
    title: str | None = None,
    author: str | None = None,
) -> DocumentIngestionResponse:
    full_text = "\n\n".join(segment.text for segment in segments)
    return DocumentIngestionResponse(
        metadata=DocumentMetadata(
            filename=filename,
            file_type=file_type,
            mime_type=mime_type,
            size_bytes=size_bytes,
            page_count=page_count,
            segment_count=len(segments),
            char_count=len(full_text),
            word_count=_word_count(full_text),
            title=title,
            author=author,
        ),
        segments=segments,
        full_text=full_text,
    )


def parse_pdf(content: bytes, filename: str, mime_type: str) -> DocumentIngestionResponse:
    doc = fitz.open(stream=content, filetype="pdf")
    try:
        segments: list[TextSegment] = []
        for page_index in range(doc.page_count):
            page = doc[page_index]
            text = page.get_text().strip()
            if not text:
                continue
            segments.append(
                TextSegment(
                    text=text,
                    index=len(segments),
                    page=page_index + 1,
                    section=None,
                )
            )

        pdf_meta = doc.metadata or {}
        return _build_response(
            filename=filename,
            file_type="pdf",
            mime_type=mime_type,
            size_bytes=len(content),
            segments=segments,
            page_count=doc.page_count,
            title=pdf_meta.get("title") or None,
            author=pdf_meta.get("author") or None,
        )
    finally:
        doc.close()


def _is_heading(style_name: str | None) -> bool:
    if not style_name:
        return False
    normalized = style_name.lower()
    return normalized.startswith("heading") or normalized in {"title", "subtitle"}


def parse_docx(content: bytes, filename: str, mime_type: str) -> DocumentIngestionResponse:
    doc = Document(BytesIO(content))
    segments: list[TextSegment] = []
    current_section: str | None = None

    for paragraph_index, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue

        style_name = paragraph.style.name if paragraph.style else None
        if _is_heading(style_name):
            current_section = text
            section_ref = text
        else:
            section_ref = current_section

        segments.append(
            TextSegment(
                text=text,
                index=len(segments),
                page=None,
                section=section_ref,
            )
        )

    core_props = doc.core_properties
    return _build_response(
        filename=filename,
        file_type="docx",
        mime_type=mime_type,
        size_bytes=len(content),
        segments=segments,
        page_count=None,
        title=core_props.title or None,
        author=core_props.author or None,
    )


def ingest_document(content: bytes, filename: str, mime_type: str | None) -> DocumentIngestionResponse:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    normalized_mime = mime_type or ""

    if extension == "pdf" or normalized_mime == "application/pdf":
        return parse_pdf(content, filename, normalized_mime or "application/pdf")

    if extension == "docx" or normalized_mime in SUPPORTED_MIME_TYPES - {"application/pdf"}:
        return parse_docx(
            content,
            filename,
            normalized_mime
            or "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    raise ValueError(f"Unsupported file type. Supported extensions: {supported}")
