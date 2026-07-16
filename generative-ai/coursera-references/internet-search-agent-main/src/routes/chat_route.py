import logging
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.pregel import Pregel
from langgraph.types import Command

from src import config
from src.graphs.get_agents import get_agent
from src.models.chat_schemas import ChatInput, ChatMessage, ChatRunResponse
from src.utils import langchain_to_chat_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix=f"/api/{config.API_VERSION}", tags=["Agent"])


async def _handle_input(user_input: ChatInput, agent: Pregel) -> tuple[dict[str, Any], UUID]:
    """
    Parse user input and handle any required interrupt resumption.
    Returns kwargs for agent invocation and the run_id.
    """
    run_id = uuid4()
    thread_id = user_input.thread_id or str(uuid4())
    user_id = user_input.user_id or str(uuid4())

    configurable = {"thread_id": thread_id, "user_id": user_id}

    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
    )

    # Check for interrupts that need to be resumed
    state = await agent.aget_state(config=config)
    interrupted_tasks = [task for task in state.tasks if hasattr(task, "interrupts") and task.interrupts]

    input: Command | dict[str, Any]
    if interrupted_tasks:
        # assume user input is response to resume agent execution from interrupt
        input = Command(resume=user_input.message)
    else:
        input = {"messages": [HumanMessage(content=user_input.message)]}

    kwargs = {
        "input": input,
        "config": config,
    }

    return kwargs, run_id


@router.post("/chat/wait", response_model=ChatMessage)
async def chat_wait(user_input: ChatInput):
    # awaits until the agent is ready to process the input
    agent: Pregel = get_agent(user_input.agent_id)
    kwargs, run_id = await _handle_input(user_input, agent)
    try:
        response_events: list[tuple[str, Any]] = await agent.ainvoke(**kwargs, stream_mode=["updates", "values"])  # type: ignore # fmt: skip
        response_type, response = response_events[-1]
        if response_type == "values":
            # Normal response, the agent completed successfully
            output = langchain_to_chat_message(response["messages"][-1])
        elif response_type == "updates" and "__interrupt__" in response:
            # The last thing to occur was an interrupt
            # Return the value of the first interrupt as an AIMessage
            output = langchain_to_chat_message(AIMessage(content=response["__interrupt__"][0].value))
        else:
            raise ValueError(f"Unexpected response type: {response_type}")

        output.run_id = str(run_id)
        return output
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/chat", response_model=ChatRunResponse)
async def chat(user_input: ChatInput, background_tasks: BackgroundTasks):
    """
    Start agent invocation without awaiting completion.
    Returns the run_id immediately while processing continues in the background.
    """
    agent: Pregel = get_agent(user_input.agent_id)
    kwargs, run_id = await _handle_input(user_input, agent)
    try:
        # Add the agent invocation as a background task
        background_tasks.add_task(agent.ainvoke, **kwargs, stream_mode=["updates", "values"])
        return ChatRunResponse(run_id=str(run_id))
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
