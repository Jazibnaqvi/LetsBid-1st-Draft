import uuid
from datetime import datetime, timezone

from app.schemas.proposal import (
    ProposalExportResponse,
    ProposalGenerateRequest,
    ProposalResponse,
    ProposalSection,
    ProposalSectionUpdate,
    SectionStatus,
)
from app.services.gemini_client import GeminiClientError, get_gemini_client

PROPOSAL_SECTIONS = [
    "executive_summary",
    "technical_approach",
    "compliance_certifications",
    "past_performance",
    "commercial_response",
]

SECTION_TITLES = {
    "executive_summary": "Executive Summary",
    "technical_approach": "Technical Approach",
    "compliance_certifications": "Compliance & Certifications",
    "past_performance": "Past Performance",
    "commercial_response": "Commercial Response",
}

_proposals_store: dict[str, dict] = {}


def _evidence_context(request: ProposalGenerateRequest) -> str:
    evidence_lines: list[str] = []
    for match in request.requirement_matches[:10]:
        if match.matches:
            best = match.matches[0]
            evidence_lines.append(
                f"- Requirement: {match.requirement_text}\n"
                f"  Capability: {best.title} ({best.capability_id})\n"
                f"  Evidence: {best.evidence_text}"
            )
    for row in request.compliance_rows[:10]:
        if row.evidence_text:
            evidence_lines.append(
                f"- Compliance: {row.requirement_text} [{row.status.value}] — {row.evidence_text}"
            )
    return "\n".join(evidence_lines) or "No direct evidence available."


def _generate_section_content(section_id: str, request: ProposalGenerateRequest) -> tuple[str, list[str]]:
    evidence = _evidence_context(request)
    refs = [
        match.matches[0].capability_id
        for match in request.requirement_matches
        if match.matches
    ][:5]

    prompt = f"""Write a proposal section for a bid response.

Section: {SECTION_TITLES[section_id]}
Document: {request.document_name}

Extracted bid context:
- Mandatory requirements: {len(request.entities.mandatory_requirements)}
- Compliance clauses: {len(request.entities.compliance_clauses)}
- Evaluation criteria: {len(request.entities.evaluation_criteria)}

Retrieved evidence (MUST ground claims in this evidence):
{evidence}

GO/NO-GO summary: {request.go_nogo.summary if request.go_nogo else "Not available"}

Rules:
- Write 2-4 professional paragraphs.
- Reference specific capabilities and evidence.
- Do not invent projects or certifications not in the evidence.
- Return plain text only, no markdown headers.
"""

    try:
        client = get_gemini_client()
        raw = client.generate_structured_json(
            prompt,
            {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "evidence_refs": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["content"],
            },
        )
        content = raw.get("content", "")
        evidence_refs = raw.get("evidence_refs", refs)
        return content, evidence_refs
    except GeminiClientError:
        fallback = (
            f"Our organization addresses the requirements outlined in {request.document_name}. "
            f"Based on retrieved evidence from {', '.join(refs[:3]) or 'our capability library'}, "
            f"we demonstrate relevant experience and compliance capability for this opportunity."
        )
        return fallback, refs


def generate_proposal(request: ProposalGenerateRequest) -> ProposalResponse:
    proposal_id = str(uuid.uuid4())
    sections: list[ProposalSection] = []

    for section_id in PROPOSAL_SECTIONS:
        content, refs = _generate_section_content(section_id, request)
        sections.append(
            ProposalSection(
                section_id=section_id,
                title=SECTION_TITLES[section_id],
                draft_content=content,
                evidence_refs=refs,
                status=SectionStatus.DRAFT,
            )
        )

    created_at = datetime.now(timezone.utc).isoformat()
    _proposals_store[proposal_id] = {
        "proposal_id": proposal_id,
        "document_name": request.document_name,
        "sections": [section.model_dump() for section in sections],
        "created_at": created_at,
    }

    return ProposalResponse(
        proposal_id=proposal_id,
        document_name=request.document_name,
        sections=sections,
        created_at=created_at,
    )


def get_proposal(proposal_id: str) -> ProposalResponse | None:
    data = _proposals_store.get(proposal_id)
    if not data:
        return None
    return ProposalResponse(
        proposal_id=data["proposal_id"],
        document_name=data["document_name"],
        sections=[ProposalSection(**section) for section in data["sections"]],
        created_at=data["created_at"],
    )


def update_proposal_section(
    proposal_id: str,
    section_id: str,
    update: ProposalSectionUpdate,
) -> ProposalSection | None:
    data = _proposals_store.get(proposal_id)
    if not data:
        return None

    for section in data["sections"]:
        if section["section_id"] == section_id:
            section["edited_content"] = update.edited_content
            return ProposalSection(**section)
    return None


def approve_proposal_section(proposal_id: str, section_id: str) -> ProposalSection | None:
    data = _proposals_store.get(proposal_id)
    if not data:
        return None

    for section in data["sections"]:
        if section["section_id"] == section_id:
            section["status"] = SectionStatus.APPROVED.value
            return ProposalSection(**section)
    return None


def export_proposal(proposal_id: str) -> ProposalExportResponse | None:
    proposal = get_proposal(proposal_id)
    if not proposal:
        return None

    parts: list[str] = [f"# Proposal: {proposal.document_name}", ""]
    for section in proposal.sections:
        content = section.edited_content or section.draft_content
        parts.extend([f"## {section.title}", "", content, ""])
        if section.evidence_refs:
            parts.append(f"_Evidence: {', '.join(section.evidence_refs)}_")
            parts.append("")

    return ProposalExportResponse(
        proposal_id=proposal.proposal_id,
        document_name=proposal.document_name,
        exported_at=datetime.now(timezone.utc).isoformat(),
        content="\n".join(parts),
        sections=proposal.sections,
    )
