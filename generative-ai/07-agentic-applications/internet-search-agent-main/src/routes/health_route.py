from fastapi import APIRouter, status

from src import config
from src.models.schemas import HealthResponse

router = APIRouter(prefix=f"/api/{config.API_VERSION}", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    return HealthResponse(message="ALL IS WELL", status=status.HTTP_200_OK)
