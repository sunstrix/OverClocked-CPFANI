from fastapi import APIRouter
from overclocked_helpdesk.utils.qr import generate_team_qr

router = APIRouter(prefix="/qr", tags=["QR"])

@router.get("/team/{team_id}")
def get_team_qr(team_id: int):
    path = generate_team_qr(team_id)
    return {
        "team_id": team_id,
        "qr_url": path
    }
