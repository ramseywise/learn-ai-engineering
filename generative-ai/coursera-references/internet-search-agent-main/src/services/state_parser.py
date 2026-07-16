
from datetime import datetime
from typing import Any

from src.models.state_schemas import Message, MessageType, ParsedStateHistory, SearchResult, StepInfo


class StateHistoryParser:
    
    @staticmethod
    def parse_state_history(raw_history: list[Any]) -> ParsedStateHistory:
        """Parse raw LangGraph state history into structured format"""
        if not raw_history:
            return ParsedStateHistory(thread_id="", total_steps=0, steps=[])
        
        steps = []
        thread_id = ""
        
        # Process each state entry (reverse order since history is newest first)
        for i, state_entry in enumerate(reversed(raw_history)):
            try:
                step_info = StateHistoryParser._parse_single_step(state_entry, i)
                if step_info:
                    steps.append(step_info)
                    if not thread_id and hasattr(state_entry[2], 'get'):
                        thread_id = state_entry[2].get('configurable', {}).get('thread_id', '')
            except Exception as e:
                print(f"Error parsing step {i}: {e}")
                continue
        
        return ParsedStateHistory(
            thread_id=thread_id,
            total_steps=len(steps),
            steps=steps
        )
    
    @staticmethod
    def _parse_single_step(state_entry: list[Any], step_index: int) -> StepInfo | None:
        """Parse a single step from the state history"""
        if len(state_entry) < 6:
            return None
        
        state_data = state_entry[0]
        next_nodes = state_entry[1] if len(state_entry) > 1 else []
        # config = state_entry[2] if len(state_entry) > 2 else {}
        metadata = state_entry[3] if len(state_entry) > 3 else {}
        timestamp_str = state_entry[4] if len(state_entry) > 4 else None
        
        # Parse timestamp
        timestamp = datetime.now()
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Determine node name and description
        node_name = StateHistoryParser._get_node_name(next_nodes, metadata)
        description = StateHistoryParser._get_step_description(node_name, state_data, metadata)
        
        # Parse messages
        messages = StateHistoryParser._parse_messages(state_data)
        
        # Parse search results
        search_results = StateHistoryParser._parse_search_results(state_data)
        
        # Get should_search flag
        should_search = state_data.get('should_search') if isinstance(state_data, dict) else None
        
        # Parse workflow-specific fields
        outline = state_data.get('outline') if isinstance(state_data, dict) else None
        current_idx = state_data.get('current_idx') if isinstance(state_data, dict) else None
        section_drafts = state_data.get('section_drafts') if isinstance(state_data, dict) else None
        
        return StepInfo(
            step_number=step_index,
            node_name=node_name,
            timestamp=timestamp,
            description=description,
            messages=messages,
            search_results=search_results,
            should_search=should_search,
            outline=outline,
            current_idx=current_idx,
            section_drafts=section_drafts
        )
    
    @staticmethod
    def _get_node_name(next_nodes: list[str], metadata: dict[str, Any]) -> str:
        """Extract the current node name"""
        if next_nodes and len(next_nodes) > 0:
            return next_nodes[0]
        
        if metadata and 'writes' in metadata:
            writes = metadata['writes']
            if writes and isinstance(writes, dict):
                return list(writes.keys())[0]
        
        return "unknown"
    
    @staticmethod
    def _get_step_description(node_name: str, state_data: dict[str, Any], metadata: dict[str, Any]) -> str:
        """Generate human-readable description for each step"""
        descriptions = {
            # Simple agent nodes
            "__start__": "🚀 Starting conversation with user query",
            "decide_search": "🤔 Analyzing if web search is needed",
            "run_search": "🔍 Searching the web for relevant information",
            "generate_answer": "💭 Generating response based on available information",
            
            # Workflow agent nodes
            "plan_outline": "📋 Creating outline for comprehensive report",
            "search_section": "🔍 Searching for section-specific information",
            "draft_section": "✍️ Drafting report section",
            "advance_index": "➡️ Moving to next section",
            "compile_report": "📄 Compiling final report"
        }
        
        base_description = descriptions.get(node_name, f"Processing {node_name}")
        
        # Add context based on state data
        if node_name == "run_search" and isinstance(state_data, dict):
            search_results = state_data.get('search_results', [])
            if search_results:
                base_description += f" (Found {len(search_results)} results)"
        
        elif node_name == "search_section" and isinstance(state_data, dict):
            search_results = state_data.get('search_results', [])
            current_idx = state_data.get('current_idx', 0)
            outline = state_data.get('outline', [])
            if outline and current_idx < len(outline):
                section_title = outline[current_idx]
                base_description += f" for: {section_title}"
            if search_results:
                base_description += f" (Found {len(search_results)} results)"
        
        elif node_name == "decide_search" and isinstance(state_data, dict):
            should_search = state_data.get('should_search')
            if should_search is not None:
                base_description += f" (Decision: {'Search' if should_search else 'No search'})"
        
        elif node_name == "plan_outline" and isinstance(state_data, dict):
            outline = state_data.get('outline', [])
            if outline:
                base_description += f" ({len(outline)} sections planned)"
        
        elif node_name == "draft_section" and isinstance(state_data, dict):
            current_idx = state_data.get('current_idx', 0)
            outline = state_data.get('outline', [])
            if outline and current_idx < len(outline):
                section_title = outline[current_idx]
                base_description += f" for: {section_title}"
        
        elif node_name == "advance_index" and isinstance(state_data, dict):
            current_idx = state_data.get('current_idx', 0)
            outline = state_data.get('outline', [])
            if outline:
                base_description += f" (Section {current_idx + 1}/{len(outline)} completed)"
        
        elif node_name == "compile_report" and isinstance(state_data, dict):
            section_drafts = state_data.get('section_drafts', [])
            if section_drafts:
                base_description += f" ({len(section_drafts)} sections compiled)"
        
        elif node_name == "generate_answer" and isinstance(state_data, dict):
            messages = state_data.get('messages', [])
            ai_messages = [m for m in messages if isinstance(m, dict) and m.get('type') == 'ai']
            if ai_messages:
                base_description += " (Response generated)"
        
        return base_description
    
    @staticmethod
    def _parse_messages(state_data: dict[str, Any]) -> list[Message]:
        """Extract and parse messages from state data"""
        if not isinstance(state_data, dict):
            return []
        
        messages = state_data.get('messages', [])
        parsed_messages = []
        
        for msg in messages:
            if isinstance(msg, dict):
                try:
                    parsed_messages.append(Message(
                        content=msg.get('content', ''),
                        type=MessageType(msg.get('type', 'human')),
                        id=msg.get('id', ''),
                        name=msg.get('name')
                    ))
                except ValueError:
                    # Handle unknown message types
                    continue
        
        return parsed_messages
    
    @staticmethod
    def _parse_search_results(state_data: dict[str, Any]) -> list[SearchResult]:
        """Extract and parse search results from state data"""
        if not isinstance(state_data, dict):
            return []
        
        search_results = state_data.get('search_results', [])
        parsed_results = []
        
        for result in search_results:
            if isinstance(result, dict):
                try:
                    parsed_results.append(SearchResult(
                        body=result.get('body', ''),
                        href=result.get('href', ''),
                        title=result.get('title', ''),
                        index=result.get('index', 0),
                        content=result.get('content')  # For workflow agent's crawled content
                    ))
                except Exception:
                    continue
        
        return parsed_results