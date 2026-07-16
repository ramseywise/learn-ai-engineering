"""
Test configuration and fixtures for the internet search agent tests.
"""
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage

# Set up test environment variables before importing the app
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test_key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT_NAME", "test_deployment")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-02-01")
os.environ.setdefault("BING_SUBSCRIPTION_KEY", "test_bing_key")

from src.main import app
from src.models.schemas import CustomState
from src.models.search_schemas import BingSearchResult
from src.models.state_schemas import Message, MessageType


@pytest.fixture
def client() -> TestClient:
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_llm():
    """Mock LLM client for testing."""
    with patch("src.graphs.simple_search_agent.llm") as mock_simple, \
         patch("src.graphs.workflow_agent.llm") as mock_workflow:
        # Configure default responses for both agents
        for mock in [mock_simple, mock_workflow]:
            mock.invoke.return_value = AIMessage(content="Test response")
            mock.with_structured_output.return_value.invoke.return_value = {"should_search": True}
        yield mock_simple


@pytest.fixture
def mock_bing_search():
    """Mock Bing search client for testing."""
    with patch("src.graphs.simple_search_agent.bing_search") as mock_simple, \
         patch("src.graphs.workflow_agent.bing_search") as mock_workflow:
        # Configure default search results for both agents
        for mock in [mock_simple, mock_workflow]:
            mock.invoke.return_value = '[{"snippet": "Test snippet", "link": "https://example.com", "name": "Test Title"}]'
        yield mock_simple


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        BingSearchResult(
            body="Test snippet 1",
            href="https://example1.com",
            title="Test Title 1",
            index=1,
            content="Detailed content 1"
        ),
        BingSearchResult(
            body="Test snippet 2", 
            href="https://example2.com",
            title="Test Title 2",
            index=2,
            content="Detailed content 2"
        )
    ]


@pytest.fixture
def sample_messages():
    """Sample message history for testing."""
    return [
        HumanMessage(content="What are the latest sustainability trends?"),
        AIMessage(content="Based on recent research...")
    ]


@pytest.fixture
def sample_custom_state(sample_messages, sample_search_results):
    """Sample CustomState for testing."""
    return CustomState(
        messages=sample_messages,
        should_search=True,
        search_results=sample_search_results
    )


@pytest.fixture
def temp_sqlite_db():
    """Temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        temp_path = temp_file.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "AZURE_OPENAI_API_KEY": "test_key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test_deployment",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "BING_SUBSCRIPTION_KEY": "test_bing_key",
        "SQLITE_DB_LOCAL_PATH": "test.db"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_crawler_response():
    """Mock crawl4ai response for testing."""
    return {
        "success": True,
        "data": {
            "markdown": "# Test Content\nThis is test markdown content from the webpage.",
            "cleaned_html": "<h1>Test Content</h1><p>This is test content.</p>"
        }
    }


@pytest.fixture
def sample_state_history():
    """Sample state history for testing."""
    return [
        Message(
            content="What are the latest sustainability trends?",
            type=MessageType.HUMAN,
            id="msg1",
            name=None
        ),
        Message(
            content="Based on recent research, here are the key trends...",
            type=MessageType.AI,
            id="msg2", 
            name=None
        )
    ]


@pytest.fixture
def mock_requests():
    """Mock requests for external API calls."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "markdown": "Test content"
            }
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        yield mock_post


# Async fixtures for async testing
@pytest.fixture
async def async_mock_checkpointer():
    """Mock checkpointer for async testing."""
    checkpointer = AsyncMock()
    checkpointer.setup = AsyncMock()
    checkpointer.aget_state_history = AsyncMock(return_value=[])
    yield checkpointer


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    agent = MagicMock()
    agent.aget_state_history = AsyncMock(return_value=[])
    agent.invoke = MagicMock(return_value={"messages": [AIMessage(content="Test response")]})
    agent.ainvoke = AsyncMock(return_value={"messages": [AIMessage(content="Test response")]})
    return agent


# Test data constants
TEST_THREAD_ID = "test-thread-123"
TEST_USER_ID = "test-user-456"
TEST_AGENT_ID = "simple-search"

# Test messages
SUSTAINABILITY_QUERY = "What are the latest sustainability trends in the automotive industry?"
NON_SUSTAINABILITY_QUERY = "How tall is the Eiffel Tower?"
GREETING_MESSAGE = "Hello, how are you?"
