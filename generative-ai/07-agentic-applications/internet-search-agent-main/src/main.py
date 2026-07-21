import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import config
from src.graphs.get_agents import get_agent, get_all_agent_info
from src.persistence import get_checkpointer
from src.routes import (
    chat_route,
    health_route,
    history_route,
    info_route,
    status_route,
    threads_route,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Configurable lifespan that initializes the appropriate database checkpointer and store
    based on settings.
    """
    try:
        # Initialize checkpointer (for short-term memory)
        async with get_checkpointer() as saver:
            if hasattr(saver, "setup"):
                await saver.setup()

            agents = get_all_agent_info()
            for a in agents:
                agent = get_agent(a.key)
                agent.checkpointer = saver
            yield
    except Exception as e:
        logger.error(f"Error during lifespan: {e}")
        raise


app = FastAPI(
    title="Internet Search Agent",
    description="Internet Search Agent API",
    version=config.API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_route.router)
app.include_router(info_route.router)
app.include_router(chat_route.router)
app.include_router(status_route.router)
app.include_router(history_route.router)
app.include_router(threads_route.router)
