from fastapi import APIRouter

from src import config
from src.graphs.get_agents import get_all_agent_info
from src.models.schemas import ServiceMetadata

router = APIRouter(prefix=f"/api/{config.API_VERSION}", tags=["Info"])


@router.get("/info", response_model=ServiceMetadata)
async def info():
    return ServiceMetadata(
        agents=get_all_agent_info(),
        default_agent=config.DEFAULT_AGENT,
    )
