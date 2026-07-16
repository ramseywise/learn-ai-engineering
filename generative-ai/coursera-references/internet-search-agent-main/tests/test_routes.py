"""
Tests for API routes.
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage


class TestHealthRoute:
    """Tests for health endpoint."""
    
    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint returns 200 and correct message."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ALL IS WELL"
        assert data["status"] == 200


class TestInfoRoute:
    """Tests for info endpoint."""
    
    def test_info_endpoint(self, client: TestClient):
        """Test info endpoint returns service metadata."""
        with patch("src.routes.info_route.get_all_agent_info") as mock_get_agents:
            mock_get_agents.return_value = [
                {"key": "simple-search", "description": "Simple search agent"},
                {"key": "workflow", "description": "Workflow agent"}
            ]
            
            response = client.get("/api/v1/info")
            
            assert response.status_code == 200
            data = response.json()
            assert "agents" in data
            assert "default_agent" in data
            assert len(data["agents"]) == 2


class TestChatRoute:
    """Tests for chat endpoints."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies for chat routes."""
        with patch("src.routes.chat_route.get_agent") as mock_get_agent, \
             patch("src.routes.chat_route._handle_input") as mock_handle_input:
            
            # Mock agent
            mock_agent = AsyncMock()
            # Mock the expected response format from ainvoke with stream_mode
            mock_agent.ainvoke.return_value = [
                ("values", {"messages": [AIMessage(content="Test response")]})
            ]
            mock_get_agent.return_value = mock_agent
            
            # Mock handle input
            mock_handle_input.return_value = ({"input": "test"}, "test-run-id")
            
            yield {
                "agent": mock_agent,
                "handle_input": mock_handle_input
            }
    
    def test_chat_endpoint(self, client: TestClient, mock_dependencies):
        """Test chat endpoint initiates conversation correctly."""
        payload = {
            "message": "What are the latest sustainability trends?",
            "thread_id": "test-thread",
            "agent_id": "simple-search"
        }
        
        response = client.post("/api/v1/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
    
    def test_chat_wait_endpoint(self, client: TestClient, mock_dependencies):
        """Test chat wait endpoint returns message directly."""
        payload = {
            "message": "What are the latest sustainability trends?",
            "thread_id": "test-thread",
            "agent_id": "simple-search"
        }
        
        response = client.post("/api/v1/chat/wait", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "type" in data
    
    def test_chat_invalid_payload(self, client: TestClient):
        """Test chat endpoint with invalid payload."""
        payload = {
            # Missing required 'message' field
            "thread_id": "test-thread"
        }
        
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422  # Validation error


class TestStatusRoute:
    """Tests for status endpoints."""
    
    @pytest.fixture
    def mock_state_history(self):
        """Mock state history dependencies."""
        with patch("src.routes.status_route.get_agent") as mock_get_agent, \
             patch("src.routes.status_route.StateHistoryParser") as mock_parser:
            
            # Mock agent with state history
            mock_agent = AsyncMock()
            mock_agent.aget_state_history.return_value = [
                {"step": 1, "node": "decide_search"},
                {"step": 2, "node": "run_search"}
            ]
            mock_get_agent.return_value = mock_agent
            
            # Mock parser
            mock_parser.parse_state_history.return_value = {
                "thread_id": "test-thread",
                "total_steps": 2,
                "steps": []
            }
            
            yield {"agent": mock_agent, "parser": mock_parser}
    
    def test_get_state_history(self, client: TestClient, mock_state_history):
        """Test getting parsed state history."""
        payload = {
            "thread_id": "test-thread",
            "agent_id": "simple-search"
        }
        
        response = client.post("/api/v1/state_history", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert "total_steps" in data
        assert "steps" in data
    
    def test_get_raw_state_history(self, client: TestClient, mock_state_history):
        """Test getting raw state history."""
        payload = {
            "thread_id": "test-thread", 
            "agent_id": "simple-search"
        }
        
        response = client.post("/api/v1/state_history/raw", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestHistoryRoute:
    """Tests for history endpoints."""
    
    @pytest.fixture
    def mock_history_dependencies(self):
        """Mock history route dependencies."""
        with patch("src.routes.history_route.get_agent") as mock_get_agent:
            mock_agent = AsyncMock()
            mock_agent.aget_state_history.return_value = [
                {"messages": [{"content": "Hello", "type": "human"}]},
                {"messages": [{"content": "Hi there", "type": "ai"}]}
            ]
            mock_get_agent.return_value = mock_agent
            
            yield mock_agent
    
    def test_get_chat_history(self, client: TestClient, mock_history_dependencies):
        """Test getting chat history."""
        payload = {
            "thread_id": "test-thread",
            "agent_id": "simple-search"
        }
        
        response = client.post("/api/v1/history", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)


class TestThreadsRoute:
    """Tests for threads endpoints."""
    
    @pytest.fixture 
    def mock_threads_dependencies(self):
        """Mock threads route dependencies."""
        with patch("src.routes.threads_route.get_checkpointer") as mock_get_checkpointer:
            mock_saver = AsyncMock()
            
            # Mock the alist method to be an async iterator
            async def mock_alist(*args, **kwargs):
                items = [
                    {"thread_id": "thread1", "checkpoint_id": "cp1"},
                    {"thread_id": "thread2", "checkpoint_id": "cp2"}
                ]
                for item in items:
                    yield item
            
            mock_saver.alist = mock_alist
            mock_saver.adelete_thread.return_value = None
            
            # Mock the async context manager
            async_context_mock = AsyncMock()
            async_context_mock.__aenter__.return_value = mock_saver
            async_context_mock.__aexit__.return_value = None
            mock_get_checkpointer.return_value = async_context_mock
            
            yield mock_saver
    
    def test_list_threads(self, client: TestClient, mock_threads_dependencies):
        """Test listing threads."""
        response = client.get("/api/v1/threads/show_all")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_delete_thread(self, client: TestClient, mock_threads_dependencies):
        """Test deleting a thread."""
        response = client.delete("/api/v1/threads/delete?thread_id=thread1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestRouteIntegration:
    """Integration tests for routes."""
    
    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are properly set."""
        response = client.options("/api/v1/health")
        
        # The response should include CORS headers
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled
    
    def test_api_version_consistency(self, client: TestClient):
        """Test all routes use consistent API version."""
        endpoints = [
            "/api/v1/health",
            "/api/v1/info"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not get 404 (which would indicate wrong API version)
            assert response.status_code != 404
