from fastapi import APIRouter

from app.schemas.go_nogo import GoNoGoRequest, GoNoGoResponse
from app.services.go_nogo_scoring import calculate_go_nogo

router = APIRouter(prefix="/go-nogo")


@router.post("/score", response_model=GoNoGoResponse)
async def score_bid_opportunity(payload: GoNoGoRequest):
    return calculate_go_nogo(payload)
