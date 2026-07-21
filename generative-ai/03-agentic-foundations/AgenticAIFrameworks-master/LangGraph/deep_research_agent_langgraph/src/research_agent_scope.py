

''' user clarification and research breif generation'''

from datetime import datetime
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os
load_dotenv()

from  langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from deep_research_agent_langgraph.src.prompts import clarify_with_user_instructions, transform_messages_into_research_topic_prompt
from deep_research_agent_langgraph.src.state_scope import AgentState, ClarifyWithUser, ResearchQuestion, AgentInputState
from typing_extensions import Literal

google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key
else:
    
    print("Warning: GOOGLE_API_KEY is not set. Continuing without setting the environment variable.")

# utility func
def get_today_str() -> str:
    """Get current date in a human-readable format."""
    
    now = datetime.now()
    return now.strftime("%a %b {}, %Y").format(now.day)

# config
model = init_chat_model ( "gemini-2.5-flash", model_provider="google_genai", temperature=0)

def clarify_with_user (state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:

    ''' Clarify the research topic with the user if needed, else generate a research brief.'''

    # structured output model

    structured_output_model = model.with_structured_output(ClarifyWithUser)

    # invoke model with clarification instructions

    response = structured_output_model.invoke ([
        
        HumanMessage(content=clarify_with_user_instructions.format(
            
            messages = get_buffer_string(messages = state["messages"]),
            date = get_today_str()
            ) ) ])

    
    if response.need_clarification:

        return Command(
            goto=START,
            update = { "messages": [AIMessage (content=response.question)] }
        )

    else: 
        return Command(
            goto="write_research_brief",
            update = { "messages": [AIMessage (content=response.verification)] }
        )


def write_research_brief(state: AgentState):
    """
    Transform the conversation history into a comprehensive research brief.
    
    """
    
    structured_output_model = model.with_structured_output(ResearchQuestion)
    
    #  research brief from conversation history
    response = structured_output_model.invoke([
        HumanMessage(content=transform_messages_into_research_topic_prompt.format(
            messages=get_buffer_string(state.get("messages", [])),
            date=get_today_str()
        ))
    ])
    
    # pass to supervisor
    
    return {
        "research_brief": response.research_brief,
        "supervisor_messages": [HumanMessage(content=f"{response.research_brief}.")]
    }

# graph construction

deep_researcher_builder = StateGraph (AgentState, input_schema = AgentInputState)

#nodes 

deep_researcher_builder.add_node ("clarify_with_user", clarify_with_user )
deep_researcher_builder.add_node ("write_research_brief", write_research_brief )

#edges

deep_researcher_builder.add_edge (START, "clarify_with_user")
deep_researcher_builder.add_edge  ("write_research_brief", END)

# compile
scope_research = deep_researcher_builder.compile()
