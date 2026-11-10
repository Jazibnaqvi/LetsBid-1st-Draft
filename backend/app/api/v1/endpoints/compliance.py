from fastapi import APIRouter

from app.schemas.compliance import ComplianceMatrixRequest, ComplianceMatrixResponse
from app.services.compliance_matrix import build_compliance_matrix

router = APIRouter(prefix="/compliance")


@router.post("/matrix", response_model=ComplianceMatrixResponse)
async def create_compliance_matrix(payload: ComplianceMatrixRequest):
    return build_compliance_matrix(
        payload.requirement_matches,
        pass_threshold=payload.pass_threshold,
        partial_threshold=payload.partial_threshold,
    )
