from pydantic import BaseModel, Field


class CapabilityRecord(BaseModel):
    capability_id: str
    title: str
    description: str
    domain: str
    certifications: list[str] = Field(default_factory=list)
    client_types: list[str] = Field(default_factory=list)
    min_contract_value: float = 0
    max_contract_value: float = 0
    project_year: int = 0
    bid_outcome: str = ""
    evidence_text: str = ""
    proof_document: str = ""
