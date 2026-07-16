"""
Tests for graph agents and their functionality.
"""
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.graphs.simple_search_agent import decide_search, generate_answer, run_search
from src.graphs.workflow_agent import (
    WorkflowState,
    advance_index,
    compile_report,
    draft_section,
    plan_outline,
    search_section,
)
from src.graphs.workflow_agent import decide_search as workflow_decide_search
from src.graphs.workflow_agent import generate_answer as workflow_generate_answer
from src.models.schemas import CustomState
from src.models.search_schemas import BingSearchResult, SearchDecision


class TestSimpleSearchAgent:
    """Tests for the simple search agent."""
    
    def test_decide_search_sustainability_query(self, mock_llm):
        """Test decision node with sustainability-related query."""
        state = CustomState(
            messages=[HumanMessage(content="What are the latest sustainability trends?")],
            should_search=False,
            search_results=[]
        )
        
        # Mock the structured output
        mock_decision = SearchDecision(should_search=True)
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_decision
        
        result = decide_search(state)
        
        assert result["should_search"] is True
        mock_llm.with_structured_output.assert_called_once()
    
    def test_decide_search_non_sustainability_query(self, mock_llm):
        """Test decision node with non-sustainability query."""
        state = CustomState(
            messages=[HumanMessage(content="How tall is the Eiffel Tower?")],
            should_search=False,
            search_results=[]
        )
        
        # Mock the structured output
        mock_decision = SearchDecision(should_search=False)
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_decision
        
        result = decide_search(state)
        
        assert result["should_search"] is False
    
    def test_run_search_success(self, mock_llm, mock_bing_search):
        """Test successful search execution."""
        state = CustomState(
            messages=[HumanMessage(content="What are sustainability trends?")],
            should_search=True,
            search_results=[]
        )
        
        # Mock search query generation
        mock_llm.invoke.return_value = AIMessage(content="sustainability trends 2024")
        
        # Mock search results
        mock_bing_search.invoke.return_value = (
            '[{"snippet": "Latest trends include...", "link": "https://example.com", "name": "Sustainability Report"}]'
        )
        
        result = run_search(state)
        
        assert "search_results" in result
        assert len(result["search_results"]) == 1
        assert result["search_results"][0].title == "Sustainability Report"
        assert result["search_results"][0].href == "https://example.com"
    
    def test_run_search_no_results(self, mock_llm, mock_bing_search):
        """Test search with no results."""
        state = CustomState(
            messages=[HumanMessage(content="What are sustainability trends?")],
            should_search=True,
            search_results=[]
        )
        
        mock_llm.invoke.return_value = AIMessage(content="sustainability trends")
        mock_bing_search.invoke.return_value = "[]"
        
        result = run_search(state)
        
        assert "search_results" in result
        assert len(result["search_results"]) == 1
        assert result["search_results"][0].title == "No Results"
    
    def test_generate_answer_with_search_results(self, mock_llm, sample_search_results):
        """Test answer generation with search results."""
        state = CustomState(
            messages=[HumanMessage(content="What are sustainability trends?")],
            should_search=True,
            search_results=sample_search_results
        )
        
        mock_llm.invoke.return_value = AIMessage(content="Based on search results, here are the trends...")
        
        result = generate_answer(state)
        
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0].content == "Based on search results, here are the trends..."
        # Search results should be cleared after use
        assert result["search_results"] == []
    
    def test_generate_answer_without_search_results(self, mock_llm):
        """Test answer generation without search results."""
        state = CustomState(
            messages=[HumanMessage(content="Tell me a joke")],
            should_search=False,
            search_results=[]
        )
        
        mock_llm.invoke.return_value = AIMessage(
            content="My focus is on providing accurate and helpful sustainability insights."
        )
        
        result = generate_answer(state)
        
        assert "messages" in result
        assert "sustainability insights" in result["messages"][0].content


class TestWorkflowAgent:
    """Tests for the workflow agent."""
    
    def test_workflow_decide_search(self, mock_llm):
        """Test workflow agent decision logic."""
        state = WorkflowState(
            messages=[HumanMessage(content="Create a sustainability report")],
            outline=[],
            current_idx=0,
            search_results=[],
            section_drafts=[],
            should_search=False
        )
        
        mock_decision = SearchDecision(should_search=True)
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_decision
        
        result = workflow_decide_search(state)
        
        assert result["should_search"] is True
    
    def test_plan_outline(self):
        """Test outline planning functionality."""
        state = WorkflowState(
            messages=[HumanMessage(content="Sustainability in automotive industry")],
            outline=[],
            current_idx=0,
            search_results=[],
            section_drafts=[],
            should_search=True
        )
        
        # Mock the workflow agent's LLM directly for this test
        with patch("src.graphs.workflow_agent.llm") as mock_llm:
            # Mock structured output for outline - return the dict format that the code expects
            mock_outline_dict = {
                "outline": [
                    "Current State of Automotive Sustainability",
                    "Emerging Technologies and Innovations", 
                    "Future Outlook and Challenges"
                ]
            }
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_outline_dict
            
            result = plan_outline(state)
            
            assert "outline" in result
            assert "current_idx" in result
            assert len(result["outline"]) == 3
            assert result["current_idx"] == 0
    
    def test_search_section(self, mock_llm, mock_bing_search):
        """Test section-specific search."""
        state = WorkflowState(
            messages=[HumanMessage(content="Automotive sustainability report")],
            outline=["Current State", "Future Trends"],
            current_idx=0,
            search_results=[],
            section_drafts=[],
            should_search=True
        )
        
        mock_llm.invoke.return_value = AIMessage(content="automotive sustainability current state 2024")
        mock_bing_search.invoke.return_value = (
            '[{"snippet": "Current automotive sustainability...", "link": "https://auto-sustain.com", "name": "Auto Report"}]'
        )
        
        with patch("src.graphs.workflow_agent._sync_crawl_urls") as mock_crawl:
            mock_crawl.return_value = [
                BingSearchResult(
                    body="Current automotive sustainability...",
                    href="https://auto-sustain.com",
                    title="Auto Report",
                    index=1,
                    content="Detailed content about automotive sustainability"
                )
            ]
            
            result = search_section(state)
            
            assert "search_results" in result
            assert len(result["search_results"]) == 1
    
    def test_search_section_with_retry(self, mock_llm, mock_bing_search):
        """Test search section with retry logic."""
        state = WorkflowState(
            messages=[HumanMessage(content="Test report")],
            outline=["Test Section"],
            current_idx=0,
            search_results=[],
            section_drafts=[],
            should_search=True
        )
        
        # First call returns no results, second call returns results
        mock_bing_search.invoke.side_effect = [
            '{"Results": "No good Bing Search Result was found"}',
            '[{"snippet": "Found on retry", "link": "https://retry.com", "name": "Retry Result"}]'
        ]
        
        mock_llm.invoke.side_effect = [
            AIMessage(content="initial query"),
            AIMessage(content="retry query")
        ]
        
        with patch("src.graphs.workflow_agent._sync_crawl_urls") as mock_crawl:
            mock_crawl.return_value = [
                BingSearchResult(
                    body="Found on retry",
                    href="https://retry.com", 
                    title="Retry Result",
                    index=1,
                    content="Content from retry"
                )
            ]
            
            result = search_section(state)
            
            assert "search_results" in result
            assert result["search_results"][0].title == "Retry Result"
    
    def test_draft_section(self, sample_search_results):
        """Test section drafting with search results."""
        state = WorkflowState(
            messages=[HumanMessage(content="Test report")],
            outline=["Introduction", "Main Content"],
            current_idx=0,
            search_results=sample_search_results,
            section_drafts=[],
            should_search=True
        )
        
        # Mock the workflow agent's LLM directly for this test
        with patch("src.graphs.workflow_agent.llm") as mock_llm:
            mock_llm.invoke.return_value = AIMessage(
                content="This section covers the introduction to sustainability trends [https://example1.com]."
            )
            
            result = draft_section(state)
            
            assert "section_drafts" in result
            assert len(result["section_drafts"]) == 1
            assert "introduction to sustainability" in result["section_drafts"][0].lower()
    
    def test_advance_index(self):
        """Test advancing to next section."""
        state = WorkflowState(
            messages=[],
            outline=["Section 1", "Section 2", "Section 3"],
            current_idx=0,
            search_results=[],
            section_drafts=["Draft 1"],
            should_search=True
        )
        
        result = advance_index(state)
        
        assert result["current_idx"] == 1
        # Search results should be cleared
        assert result["search_results"] == []
    
    def test_compile_report(self):
        """Test report compilation."""
        state = WorkflowState(
            messages=[HumanMessage(content="Create sustainability report")],
            outline=["Introduction", "Analysis", "Conclusion"],
            current_idx=2,
            search_results=[],
            section_drafts=[
                "Introduction content...",
                "Analysis content...", 
                "Conclusion content..."
            ],
            should_search=True
        )
        
        # Mock the workflow agent's LLM to return a compiled report
        with patch("src.graphs.workflow_agent.llm") as mock_llm:
            mock_llm.invoke.return_value = AIMessage(
                content="This comprehensive report covers key sustainability topics.\n\nIntroduction content...\n\nAnalysis content...\n\nConclusion content..."
            )
            
            result = compile_report(state)
            
            assert "messages" in result
            assert len(result["messages"]) == 1
            # Final report should contain all sections
            final_content = result["messages"][0].content
            assert "Introduction content" in final_content
            assert "Analysis content" in final_content
            assert "Conclusion content" in final_content
    
    def test_workflow_generate_answer_no_search(self, mock_llm):
        """Test workflow answer generation without search."""
        state = WorkflowState(
            messages=[HumanMessage(content="Tell me a joke")],
            outline=[],
            current_idx=0,
            search_results=[],
            section_drafts=[],
            should_search=False
        )
        
        mock_llm.invoke.return_value = AIMessage(
            content="My focus is on providing accurate and helpful sustainability insights."
        )
        
        result = workflow_generate_answer(state)
        
        assert "messages" in result
        # State should be cleared
        assert result["search_results"] == []
        assert result["outline"] == []
        assert result["current_idx"] == 0
        assert result["section_drafts"] == []


class TestAgentSelection:
    """Tests for agent selection and management."""
    
    def test_get_agent_simple_search(self):
        """Test getting simple search agent."""
        from src.graphs.get_agents import get_agent
        
        agent = get_agent("simple-search")
        
        assert agent is not None
        # Agent should be a compiled graph
        assert hasattr(agent, 'invoke')
    
    def test_get_agent_workflow(self):
        """Test getting workflow agent."""
        from src.graphs.get_agents import get_agent
        
        agent = get_agent("workflow")
        
        assert agent is not None
        assert hasattr(agent, 'invoke')
    
    def test_get_agent_default(self):
        """Test getting default agent."""
        from src.graphs.get_agents import get_agent
        
        agent = get_agent()  # No agent_id provided
        
        assert agent is not None
    
    def test_get_all_agent_info(self):
        """Test getting all agent information."""
        from src.graphs.get_agents import get_all_agent_info
        
        agents = get_all_agent_info()
        
        assert len(agents) >= 2  # At least simple-search and workflow
        assert all(hasattr(agent, 'key') for agent in agents)
        assert all(hasattr(agent, 'description') for agent in agents)


class TestGraphIntegration:
    """Integration tests for complete graph workflows."""
    
    @pytest.mark.asyncio
    async def test_simple_agent_full_workflow(self, mock_llm, mock_bing_search):
        """Test complete simple agent workflow."""
        from src.graphs.simple_search_agent import graph
        
        # Mock dependencies
        mock_llm.with_structured_output.return_value.invoke.return_value = SearchDecision(should_search=True)
        mock_llm.invoke.side_effect = [
            AIMessage(content="sustainability trends query"),  # For search query generation
            AIMessage(content="Based on search results, here are the trends...")  # For final answer
        ]
        mock_bing_search.invoke.return_value = (
            '[{"snippet": "Latest trends...", "link": "https://example.com", "name": "Trends Report"}]'
        )
        
        initial_state = {
            "messages": [HumanMessage(content="What are the latest sustainability trends?")]
        }
        
        result = await graph.ainvoke(initial_state)
        
        assert "messages" in result
        assert len(result["messages"]) >= 2  # Original message + AI response
        assert result["messages"][-1].content == "Based on search results, here are the trends..."
    
    @pytest.mark.asyncio 
    async def test_workflow_agent_full_workflow(self, mock_llm, mock_bing_search):
        """Test complete workflow agent workflow."""
        from src.graphs.workflow_agent import graph
        from src.models.schemas import OutlinePlan
        
        # Mock all dependencies
        mock_llm.with_structured_output.return_value.invoke.side_effect = [
            SearchDecision(should_search=True),  # decide_search
            OutlinePlan(outline=["Section 1", "Section 2"])  # plan_outline
        ]
        
        mock_llm.invoke.side_effect = [
            AIMessage(content="section 1 query"),  # search_section 1
            AIMessage(content="Section 1 content [https://example.com]"),  # draft_section 1  
            AIMessage(content="section 2 query"),  # search_section 2
            AIMessage(content="Section 2 content [https://example2.com]")  # draft_section 2
        ]
        
        mock_bing_search.invoke.return_value = (
            '[{"snippet": "Test content", "link": "https://example.com", "name": "Test"}]'
        )
        
        with patch("src.graphs.workflow_agent._sync_crawl_urls") as mock_crawl:
            mock_crawl.return_value = [
                BingSearchResult(
                    body="Test content",
                    href="https://example.com",
                    title="Test",
                    index=1,
                    content="Detailed content"
                )
            ]
            
            initial_state = {
                "messages": [HumanMessage(content="Create a sustainability report")]
            }
            
            result = await graph.ainvoke(initial_state)
            
            assert "messages" in result
            # Should have original message + final compiled report
            assert len(result["messages"]) >= 2
