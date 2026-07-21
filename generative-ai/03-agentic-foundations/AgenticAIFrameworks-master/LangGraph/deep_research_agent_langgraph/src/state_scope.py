
"""State Definitions and Pydantic Schemas for Research Scoping.

This defines the state objects and structured schemas used for
the research agent scoping workflow, including researcher state management and output schemas.
"""



import operator
from typing_extensions import Optional, Annotated, List, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

# state definitions

class AgentInputState (MessagesState):

    ''' input state for the full agent, contains message only '''
    pass

class AgentState (MessagesState):

    '''
    Main state for the full multi-agent research system.
        
    Extends MessagesState with additional fields for research coordination. '''

    # research brief generated from user conversation history
    research_breif: Optional[str]
        
    # messages exchanged with the supervisor agent for coordination
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages ]

    # Raw unprocessed research notes collected during the research phase
    raw_notes: Annotated[List[str], operator.add] = []

    # Processed and structured notes ready for report generation
    notes: Annotated[list[str], operator.add] = []

    # Final formatted research report
    final_report: str


# structured output schemas

class ClarifyWithUser (BaseModel):

    '''Schema for clarifying questions to the user.'''

    need_clarification: bool = Field(
        ..., description="Whether a clarifying question is needed."
    )
    question: str = Field(
        "", description="The clarifying question to ask the user, if needed."
    )
    verification: str = Field(
        "", description="Verification message if no clarification is needed."
    )

