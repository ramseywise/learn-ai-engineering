from pydantic import BaseModel, Field

from src import config
from src.models.chat_schemas import ChatMessage


class ChatHistoryInput(BaseModel):
    """Input for retrieving chat history."""

    thread_id: str = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    agent_id: str = config.DEFAULT_AGENT


class ChatHistory(BaseModel):
    messages: list[ChatMessage]


class StateHistoryRequest(BaseModel):
    thread_id: str
    agent_id: str = config.DEFAULT_AGENT
