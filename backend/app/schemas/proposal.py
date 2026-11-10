from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.compliance import ComplianceRow
from app.schemas.go_nogo import GoNoGoResponse
from app.schemas.ner import NerEntities
from app.schemas.rag import RequirementMatch


class SectionStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"


class ProposalSection(BaseModel):
    section_id: str
    title: str
    draft_content: str
    edited_content: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    status: SectionStatus = SectionStatus.DRAFT


class ProposalGenerateRequest(BaseModel):
    entities: NerEntities
    requirement_matches: list[RequirementMatch] = Field(default_factory=list)
    compliance_rows: list[ComplianceRow] = Field(default_factory=list)
    go_nogo: GoNoGoResponse | None = None
    document_name: str = "Untitled Bid"


class ProposalResponse(BaseModel):
    proposal_id: str
    document_name: str
    sections: list[ProposalSection]
    created_at: str


class ProposalSectionUpdate(BaseModel):
    edited_content: str


class ProposalExportResponse(BaseModel):
    proposal_id: str
    document_name: str
    exported_at: str
    content: str
    sections: list[ProposalSection]
