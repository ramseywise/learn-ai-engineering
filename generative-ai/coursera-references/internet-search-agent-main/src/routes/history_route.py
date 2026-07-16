import logging

from fastapi import APIRouter, HTTPException
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.pregel import Pregel

from src import config
from src.graphs.get_agents import get_agent
from src.models.chat_schemas import ChatMessage
from src.models.history_schemas import ChatHistory, ChatHistoryInput
from src.utils import langchain_to_chat_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix=f"/api/{config.API_VERSION}", tags=["Agent"])


@router.post("/history", response_model=ChatHistory)
async def history(input: ChatHistoryInput):
    """
    Get chat history.
    """
    agent: Pregel = get_agent(input.agent_id)
    try:
        state_snapshot = await agent.aget_state(config=RunnableConfig(configurable={"thread_id": input.thread_id}))
        messages: list[AnyMessage] = state_snapshot.values["messages"]
        chat_messages: list[ChatMessage] = [langchain_to_chat_message(m) for m in messages]
        return ChatHistory(messages=chat_messages)
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
