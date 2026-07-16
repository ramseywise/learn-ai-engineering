from dataclasses import dataclass

from langgraph.pregel import Pregel

from src import config
from src.graphs.simple_search_agent import graph as simple_search_graph
from src.graphs.workflow_agent import graph as workflow_graph
from src.models.schemas import AgentInfo


@dataclass
class Agent:
    """Class to store an agent and its metadata."""

    description: str
    graph: Pregel


agents: dict[str, Agent] = {
    "simple-search": Agent(
        description="A simple search agent that can answer questions using web search.", graph=simple_search_graph
    ),
    "workflow": Agent(
        description="A more advanced agent that creates detailed reports with multiple sections using web search.",
        graph=workflow_graph,
    ),
}


def get_agent(agent_id: str = None) -> Pregel:
    """Get the agent graph by ID.

    Args:
        agent_id: The ID of the agent to retrieve. If None, returns the default agent.

    Returns:
        The agent's compiled graph

    Raises:
        KeyError: If the agent_id is not found
    """
    # Use default agent if none is provided
    if agent_id is None:
        agent_id = config.DEFAULT_AGENT

    if agent_id not in agents:
        raise KeyError(f"Agent {agent_id} not found. Available agents: {list(agents.keys())}")

    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    """Get information about all available agents.

    Returns:
        List of AgentInfo objects for all registered agents
    """
    return [AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()]
