from pydantic import BaseModel

from app.schemas.compliance import ComplianceMatrixResponse
from app.schemas.documents import DocumentIngestionResponse
from app.schemas.go_nogo import GoNoGoResponse
from app.schemas.ner import NerExtractionResponse
from app.schemas.proposal import ProposalResponse
from app.schemas.rag import RagMatchResponse


class AnalyzeResponse(BaseModel):
    ingestion: DocumentIngestionResponse
    ner: NerExtractionResponse
    rag: RagMatchResponse
    compliance: ComplianceMatrixResponse
    go_nogo: GoNoGoResponse
    proposal: ProposalResponse
