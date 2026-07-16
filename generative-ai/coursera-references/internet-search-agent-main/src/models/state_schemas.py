from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class StepType(str, Enum):
    INPUT = "input"
    LOOP = "loop"
    
class NodeType(str, Enum):
    START = "__start__"
    DECIDE_SEARCH = "decide_search"
    RUN_SEARCH = "run_search"
    GENERATE_ANSWER = "generate_answer"
    # Workflow agent specific nodes
    PLAN_OUTLINE = "plan_outline"
    SEARCH_SECTION = "search_section"
    DRAFT_SECTION = "draft_section"
    ADVANCE_INDEX = "advance_index"
    COMPILE_REPORT = "compile_report"

class MessageType(str, Enum):
    HUMAN = "human"
    AI = "ai"

class Message(BaseModel):
    content: str
    type: MessageType
    id: str
    name: str | None = None

class SearchResult(BaseModel):
    body: str
    href: str
    title: str
    index: int
    content: str | None = None  # For workflow agent's crawled content

class StepInfo(BaseModel):
    step_number: int
    node_name: str
    timestamp: datetime
    description: str
    messages: list[Message] = []
    search_results: list[SearchResult] = []
    should_search: bool | None = None
    # Workflow agent specific fields
    outline: list[str] | None = None
    current_idx: int | None = None
    section_drafts: list[str] | None = None

class ParsedStateHistory(BaseModel):
    thread_id: str
    total_steps: int
    steps: list[StepInfo]