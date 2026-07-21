from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

from src.models.search_schemas import BingSearchResult


class CustomState(MessagesState):
    """Conversation state carried through the graph."""

    should_search: bool  # router decision
    search_results: list[BingSearchResult]  # results added by search node


class OutlinePlan(BaseModel):
    outline: list[str] = Field(description="A list of section titles for the report outline.")


class HealthResponse(BaseModel):
    message: str
    status: int


class AgentInfo(BaseModel):
    """Info about an available agent."""

    key: str = Field(
        description="Agent key.",
        examples=["research-assistant"],
    )
    description: str = Field(
        description="Description of the agent.",
        examples=["A research assistant for generating research papers."],
    )


class ServiceMetadata(BaseModel):
    """Metadata about the service including available agents and models."""

    agents: list[AgentInfo] = Field(
        description="List of available agents.",
    )
    default_agent: str = Field(
        description="Default agent used when none is specified.",
        examples=["research-assistant"],
    )
