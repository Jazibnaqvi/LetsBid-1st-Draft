from fastapi import APIRouter, HTTPException

from app.schemas.proposal import (
    ProposalExportResponse,
    ProposalGenerateRequest,
    ProposalResponse,
    ProposalSection,
    ProposalSectionUpdate,
)
from app.services.proposal_generation import (
    approve_proposal_section,
    export_proposal,
    generate_proposal,
    get_proposal,
    update_proposal_section,
)

router = APIRouter(prefix="/proposals")


@router.post("/generate", response_model=ProposalResponse)
async def create_proposal(payload: ProposalGenerateRequest):
    return generate_proposal(payload)


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def read_proposal(proposal_id: str):
    proposal = get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal


@router.put("/{proposal_id}/sections/{section_id}", response_model=ProposalSection)
async def edit_proposal_section(
    proposal_id: str,
    section_id: str,
    payload: ProposalSectionUpdate,
):
    section = update_proposal_section(proposal_id, section_id, payload)
    if not section:
        raise HTTPException(status_code=404, detail="Proposal or section not found.")
    return section


@router.post("/{proposal_id}/sections/{section_id}/approve", response_model=ProposalSection)
async def approve_section(proposal_id: str, section_id: str):
    section = approve_proposal_section(proposal_id, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Proposal or section not found.")
    return section


@router.get("/{proposal_id}/export", response_model=ProposalExportResponse)
async def export_final_proposal(proposal_id: str):
    exported = export_proposal(proposal_id)
    if not exported:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return exported
