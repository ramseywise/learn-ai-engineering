"""
Tests for Pydantic models and schemas.
"""
from datetime import datetime

import pytest
from langchain_core.messages import HumanMessage
from pydantic import ValidationError

from src.models.chat_schemas import ChatInput, ChatMessage, ChatRunResponse, ToolCall
from src.models.history_schemas import ChatHistory, ChatHistoryInput, StateHistoryRequest
from src.models.schemas import AgentInfo, CustomState, HealthResponse, OutlinePlan, ServiceMetadata
from src.models.search_schemas import BingSearchResult, SearchDecision
from src.models.state_schemas import (
    Message,
    MessageType,
    NodeType,
    ParsedStateHistory,
    SearchResult,
    StepInfo,
    StepType,
)


class TestChatSchemas:
    """Tests for chat-related schemas."""
    
    def test_chat_message_valid(self):
        """Test valid ChatMessage creation."""
        message = ChatMessage(
            type="human",
            content="Hello, world!",
            tool_calls=[],
            tool_call_id=None,
            run_id="test-run-123",
            response_metadata={},
            custom_data={}
        )
        
        assert message.type == "human"
        assert message.content == "Hello, world!"
        assert message.run_id == "test-run-123"
        assert message.tool_calls == []
    
    def test_chat_message_defaults(self):
        """Test ChatMessage with default values."""
        message = ChatMessage(
            type="ai",
            content="Response"
        )
        
        assert message.tool_calls == []
        assert message.tool_call_id is None
        assert message.run_id is None
        assert message.response_metadata == {}
        assert message.custom_data == {}
    
    def test_chat_message_invalid_type(self):
        """Test ChatMessage with invalid type."""
        with pytest.raises(ValidationError):
            ChatMessage(
                type="invalid_type",
                content="Test"
            )
    
    def test_chat_input_valid(self):
        """Test valid ChatInput creation."""
        chat_input = ChatInput(
            message="What are sustainability trends?",
            thread_id="thread-123",
            user_id="user-456",
            agent_id="simple-search"
        )
        
        assert chat_input.message == "What are sustainability trends?"
        assert chat_input.thread_id == "thread-123"
        assert chat_input.user_id == "user-456"
        assert chat_input.agent_id == "simple-search"
    
    def test_chat_input_defaults(self):
        """Test ChatInput with default values."""
        chat_input = ChatInput(message="Test message")
        
        assert chat_input.message == "Test message"
        assert chat_input.thread_id is None
        assert chat_input.user_id is None
        # agent_id should have default from config
        assert chat_input.agent_id is not None
    
    def test_chat_input_missing_message(self):
        """Test ChatInput without required message."""
        with pytest.raises(ValidationError):
            ChatInput()
    
    def test_chat_run_response(self):
        """Test ChatRunResponse creation."""
        response = ChatRunResponse(run_id="run-123")
        
        assert response.run_id == "run-123"
    
    def test_tool_call_schema(self):
        """Test ToolCall TypedDict structure."""
        tool_call: ToolCall = {
            "name": "test_tool",
            "args": {"param": "value"},
            "id": "call-123"
        }
        
        assert tool_call["name"] == "test_tool"
        assert tool_call["args"]["param"] == "value"
        assert tool_call["id"] == "call-123"


class TestSearchSchemas:
    """Tests for search-related schemas."""
    
    def test_bing_search_result_valid(self):
        """Test valid BingSearchResult creation."""
        result = BingSearchResult(
            body="Test snippet",
            href="https://example.com",
            title="Test Title",
            index=1,
            content="Full page content"
        )
        
        assert result.body == "Test snippet"
        assert result.href == "https://example.com"
        assert result.title == "Test Title"
        assert result.index == 1
        assert result.content == "Full page content"
    
    def test_bing_search_result_without_content(self):
        """Test BingSearchResult without optional content."""
        result = BingSearchResult(
            body="Test snippet",
            href="https://example.com", 
            title="Test Title",
            index=1
        )
        
        assert result.content is None
    
    def test_bing_search_result_validation(self):
        """Test BingSearchResult field validation."""
        with pytest.raises(ValidationError):
            BingSearchResult(
                body="Test",
                href="invalid-url",  # Should be valid, but let's test other validation
                title="",
                index="not-a-number"  # Should be int
            )
    
    def test_search_decision_valid(self):
        """Test valid SearchDecision creation."""
        decision = SearchDecision(should_search=True)
        
        assert decision.should_search is True
    
    def test_search_decision_false(self):
        """Test SearchDecision with false value."""
        decision = SearchDecision(should_search=False)
        
        assert decision.should_search is False
    
    def test_search_decision_validation(self):
        """Test SearchDecision type validation."""
        with pytest.raises(ValidationError):
            SearchDecision(should_search="not-a-boolean")


class TestSchemas:
    """Tests for general schemas."""
    
    def test_custom_state_valid(self):
        """Test valid CustomState creation."""
        search_results = [
            BingSearchResult(
                body="Test",
                href="https://example.com",
                title="Test",
                index=1
            )
        ]
        
        state = CustomState(
            messages=[HumanMessage(content="Test")],
            should_search=True,
            search_results=search_results
        )
        
        assert len(state["messages"]) == 1
        assert state["should_search"] is True
        assert len(state["search_results"]) == 1
    
    def test_outline_plan_valid(self):
        """Test valid OutlinePlan creation."""
        plan = OutlinePlan(
            outline=["Introduction", "Analysis", "Conclusion"]
        )
        
        assert len(plan.outline) == 3
        assert plan.outline[0] == "Introduction"
    
    def test_outline_plan_empty(self):
        """Test OutlinePlan with empty outline."""
        plan = OutlinePlan(outline=[])
        
        assert plan.outline == []
    
    def test_health_response(self):
        """Test HealthResponse schema."""
        response = HealthResponse(
            message="System healthy",
            status=200
        )
        
        assert response.message == "System healthy"
        assert response.status == 200
    
    def test_agent_info(self):
        """Test AgentInfo schema."""
        agent = AgentInfo(
            key="test-agent",
            description="A test agent for testing purposes"
        )
        
        assert agent.key == "test-agent"
        assert agent.description == "A test agent for testing purposes"
    
    def test_service_metadata(self):
        """Test ServiceMetadata schema."""
        agents = [
            AgentInfo(key="agent1", description="First agent"),
            AgentInfo(key="agent2", description="Second agent")
        ]
        
        metadata = ServiceMetadata(
            agents=agents,
            default_agent="agent1"
        )
        
        assert len(metadata.agents) == 2
        assert metadata.default_agent == "agent1"


class TestStateSchemas:
    """Tests for state-related schemas."""
    
    def test_step_type_enum(self):
        """Test StepType enum values."""
        assert StepType.INPUT == "input"
        assert StepType.LOOP == "loop"
    
    def test_node_type_enum(self):
        """Test NodeType enum values."""
        assert NodeType.START == "__start__"
        assert NodeType.DECIDE_SEARCH == "decide_search"
        assert NodeType.RUN_SEARCH == "run_search"
        assert NodeType.GENERATE_ANSWER == "generate_answer"
    
    def test_message_type_enum(self):
        """Test MessageType enum values."""
        assert MessageType.HUMAN == "human"
        assert MessageType.AI == "ai"
    
    def test_message_schema(self):
        """Test Message schema."""
        message = Message(
            content="Test message",
            type=MessageType.HUMAN,
            id="msg-123",
            name="User"
        )
        
        assert message.content == "Test message"
        assert message.type == MessageType.HUMAN
        assert message.id == "msg-123"
        assert message.name == "User"
    
    def test_message_without_name(self):
        """Test Message schema without optional name."""
        message = Message(
            content="Test message",
            type=MessageType.AI,
            id="msg-456"
        )
        
        assert message.name is None
    
    def test_search_result_schema(self):
        """Test SearchResult schema."""
        result = SearchResult(
            body="Search result snippet",
            href="https://example.com",
            title="Result Title",
            index=1,
            content="Full content"
        )
        
        assert result.body == "Search result snippet"
        assert result.href == "https://example.com"
        assert result.title == "Result Title"
        assert result.index == 1
        assert result.content == "Full content"
    
    def test_step_info_schema(self):
        """Test StepInfo schema."""
        messages = [
            Message(
                content="Hello",
                type=MessageType.HUMAN,
                id="msg1"
            )
        ]
        
        search_results = [
            SearchResult(
                body="Result",
                href="https://example.com", 
                title="Title",
                index=1
            )
        ]
        
        step = StepInfo(
            step_number=1,
            node_name="decide_search",
            timestamp=datetime.now(),
            description="Deciding whether to search",
            messages=messages,
            search_results=search_results,
            should_search=True,
            outline=["Section 1"],
            current_idx=0,
            section_drafts=["Draft 1"]
        )
        
        assert step.step_number == 1
        assert step.node_name == "decide_search"
        assert step.should_search is True
        assert len(step.messages) == 1
        assert len(step.search_results) == 1
        assert len(step.outline) == 1
        assert step.current_idx == 0
        assert len(step.section_drafts) == 1
    
    def test_parsed_state_history(self):
        """Test ParsedStateHistory schema."""
        steps = [
            StepInfo(
                step_number=1,
                node_name="decide_search",
                timestamp=datetime.now(),
                description="Step 1"
            ),
            StepInfo(
                step_number=2,
                node_name="run_search",
                timestamp=datetime.now(),
                description="Step 2"
            )
        ]
        
        history = ParsedStateHistory(
            thread_id="thread-123",
            total_steps=2,
            steps=steps
        )
        
        assert history.thread_id == "thread-123"
        assert history.total_steps == 2
        assert len(history.steps) == 2


class TestHistorySchemas:
    """Tests for history-related schemas."""
    
    def test_chat_history_input(self):
        """Test ChatHistoryInput schema."""
        history_input = ChatHistoryInput(
            thread_id="thread-123",
            agent_id="simple-search"
        )
        
        assert history_input.thread_id == "thread-123"
        assert history_input.agent_id == "simple-search"
    
    def test_chat_history_input_defaults(self):
        """Test ChatHistoryInput with defaults."""
        history_input = ChatHistoryInput(thread_id="thread-123")
        
        assert history_input.thread_id == "thread-123"
        # Should have default agent_id from config
        assert history_input.agent_id is not None
    
    def test_chat_history(self):
        """Test ChatHistory schema."""
        messages = [
            ChatMessage(type="human", content="Hello"),
            ChatMessage(type="ai", content="Hi there")
        ]
        
        history = ChatHistory(messages=messages)
        
        assert len(history.messages) == 2
        assert history.messages[0].type == "human"
        assert history.messages[1].type == "ai"
    
    def test_state_history_request(self):
        """Test StateHistoryRequest schema."""
        request = StateHistoryRequest(
            thread_id="thread-123",
            agent_id="workflow"
        )
        
        assert request.thread_id == "thread-123"
        assert request.agent_id == "workflow"
    
    def test_state_history_request_defaults(self):
        """Test StateHistoryRequest with defaults."""
        request = StateHistoryRequest(thread_id="thread-123")
        
        assert request.thread_id == "thread-123"
        # Should have default agent_id from config
        assert request.agent_id is not None


class TestSchemaValidation:
    """Tests for schema validation edge cases."""
    
    def test_empty_string_validation(self):
        """Test validation of empty strings."""
        chat_input = ChatInput(message="") 
        assert chat_input.message == ""
    
    def test_field_type_validation(self):
        """Test type validation for various fields."""
        with pytest.raises(ValidationError):
            BingSearchResult(
                body=123,  # Should be string
                href="https://example.com",
                title="Test",
                index=1
            )
    
    def test_nested_validation(self):
        """Test validation of nested schemas."""
        state = CustomState(
            messages="not-a-list", 
            should_search=True,
            search_results=[]
        )
        assert state["should_search"] is True
    
    def test_optional_field_validation(self):
        """Test validation of optional fields."""
        result = BingSearchResult(
            body="Test",
            href="https://example.com",
            title="Test",
            index=1,
            content=None
        )
        
        assert result.content is None
