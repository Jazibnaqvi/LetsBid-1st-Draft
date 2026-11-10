from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.ner import NerEntities
from app.schemas.rag import RequirementMatch


class GoNoGoRecommendation(str, Enum):
    GO = "GO"
    NO_GO = "NO-GO"
    CONDITIONAL = "CONDITIONAL"


class ScoreFactor(BaseModel):
    name: str
    weight: float
    score: float
    weighted_score: float
    rationale: str


class GoNoGoRequest(BaseModel):
    entities: NerEntities
    requirement_matches: list[RequirementMatch] = Field(default_factory=list)
    bid_domain: str | None = None
    bid_client_type: str | None = None
    bid_contract_value: float | None = None


class GoNoGoResponse(BaseModel):
    score: float = Field(ge=0, le=100)
    win_probability: float = Field(ge=0, le=1)
    recommendation: GoNoGoRecommendation
    factors: list[ScoreFactor]
    summary: str
