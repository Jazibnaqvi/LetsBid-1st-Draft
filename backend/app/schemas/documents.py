from pydantic import BaseModel, Field


class TextSegment(BaseModel):
    text: str
    index: int = Field(description="Zero-based segment index within the document")
    page: int | None = Field(default=None, description="Source page number (PDF)")
    section: str | None = Field(default=None, description="Nearest heading/section (DOCX)")


class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    mime_type: str
    size_bytes: int
    page_count: int | None = None
    segment_count: int
    char_count: int
    word_count: int
    title: str | None = None
    author: str | None = None


class DocumentIngestionResponse(BaseModel):
    metadata: DocumentMetadata
    segments: list[TextSegment]
    full_text: str
