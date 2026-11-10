from pydantic import BaseModel, Field

from app.schemas.capability import CapabilityRecord
from app.schemas.ner import MandatoryRequirement


class CapabilityMatch(BaseModel):
    capability_id: str
    title: str
    domain: str
    evidence_text: str
    proof_document: str
    similarity_score: float = Field(ge=0, le=1)
    capability: CapabilityRecord


class RequirementMatch(BaseModel):
    requirement_index: int
    requirement_text: str
    source_quote: str
    page: int | None = None
    section: str | None = None
    matches: list[CapabilityMatch] = Field(default_factory=list)


class RagIndexResponse(BaseModel):
    indexed_count: int
    collection: str
    message: str


class RagMatchRequest(BaseModel):
    requirements: list[MandatoryRequirement]
    top_k: int = Field(default=3, ge=1, le=10)


class RagMatchResponse(BaseModel):
    requirement_matches: list[RequirementMatch]
    total_requirements: int
    matched_requirements: int
