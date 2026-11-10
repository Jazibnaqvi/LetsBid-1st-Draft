from app.schemas.analyze import AnalyzeResponse
from app.schemas.compliance import ComplianceMatrixResponse
from app.schemas.documents import DocumentIngestionResponse
from app.schemas.go_nogo import GoNoGoRequest, GoNoGoResponse
from app.schemas.ner import NerExtractionResponse
from app.schemas.proposal import ProposalGenerateRequest, ProposalResponse
from app.schemas.rag import RagMatchResponse
from app.services.compliance_matrix import build_compliance_matrix
from app.services.document_ingestion import ingest_document
from app.services.go_nogo_scoring import calculate_go_nogo
from app.services.ner_extraction import extract_entities
from app.services.proposal_generation import generate_proposal
from app.services.rag_service import ensure_indexed, match_requirements


def run_analysis(
    content: bytes,
    filename: str,
    mime_type: str | None,
) -> AnalyzeResponse:
    ensure_indexed()

    ingestion: DocumentIngestionResponse = ingest_document(content, filename, mime_type)
    ner: NerExtractionResponse = extract_entities(ingestion=ingestion)

    requirements = ner.entities.mandatory_requirements
    rag: RagMatchResponse = match_requirements(requirements)

    compliance: ComplianceMatrixResponse = build_compliance_matrix(rag.requirement_matches)
    go_nogo: GoNoGoResponse = calculate_go_nogo(
        GoNoGoRequest(entities=ner.entities, requirement_matches=rag.requirement_matches)
    )
    proposal: ProposalResponse = generate_proposal(
        ProposalGenerateRequest(
            entities=ner.entities,
            requirement_matches=rag.requirement_matches,
            compliance_rows=compliance.rows,
            go_nogo=go_nogo,
            document_name=filename,
        )
    )

    return AnalyzeResponse(
        ingestion=ingestion,
        ner=ner,
        rag=rag,
        compliance=compliance,
        go_nogo=go_nogo,
        proposal=proposal,
    )
