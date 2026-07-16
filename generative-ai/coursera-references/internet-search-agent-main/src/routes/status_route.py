from fastapi import APIRouter
from langgraph.pregel import Pregel

from src import config
from src.graphs.get_agents import get_agent
from src.models.history_schemas import StateHistoryRequest
from src.models.state_schemas import ParsedStateHistory
from src.services.state_parser import StateHistoryParser

router = APIRouter(prefix=f"/api/{config.API_VERSION}", tags=["Agent"])


@router.post("/state_history", response_model=ParsedStateHistory)
async def get_state_history(request: StateHistoryRequest):
    """Get parsed state history for an agent conversation"""
    cfg = {"configurable": {"thread_id": request.thread_id}}
    items = []
    agent: Pregel = get_agent(request.agent_id)
    
    # aget_state_history returns a list, not an async iterator
    history = await agent.aget_state_history(cfg)
    items = list(history) if hasattr(history, '__iter__') else [history]
    
    # Parse the raw history into structured format
    parsed_history = StateHistoryParser.parse_state_history(items)
    return parsed_history


@router.post("/state_history/raw")
async def get_raw_state_history(request: StateHistoryRequest):
    """Get raw state history (for debugging)"""
    cfg = {"configurable": {"thread_id": request.thread_id}}
    items = []
    agent: Pregel = get_agent(request.agent_id)
    
    # aget_state_history returns a list, not an async iterator
    history = await agent.aget_state_history(cfg)
    items = list(history) if hasattr(history, '__iter__') else [history]
    
    return items