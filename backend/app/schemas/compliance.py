from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.rag import RequirementMatch


class ComplianceStatus(str, Enum):
    PASS = "Pass"
    FAIL = "Fail"
    PARTIAL = "Partial"


class ComplianceRow(BaseModel):
    row_id: int
    requirement_text: str
    source_quote: str
    page: int | None = None
    section: str | None = None
    status: ComplianceStatus
    matched_capability_id: str | None = None
    matched_capability_title: str | None = None
    evidence_text: str | None = None
    proof_document: str | None = None
    similarity_score: float | None = None
    missing_capability: bool = False
    missing_proof: bool = False
    notes: str = ""


class ComplianceMatrixResponse(BaseModel):
    rows: list[ComplianceRow]
    summary: dict[str, int]


class ComplianceMatrixRequest(BaseModel):
    requirement_matches: list[RequirementMatch]
    pass_threshold: float = Field(default=0.65, ge=0, le=1)
    partial_threshold: float = Field(default=0.45, ge=0, le=1)
