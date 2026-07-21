from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import List
import uvicorn

# Import LangGraph components and LangMem tools
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool, create_memory_manager
from langchain.chat_models import init_chat_model
# Define a custom Pydantic model for episodic memory
class Episode(BaseModel):
    observation: str = Field(..., description="Context of the interaction")
    thoughts: str = Field(..., description="Agent's internal reasoning")
    action: str = Field(..., description="Action taken by the agent")
    result: str = Field(..., description="Outcome and feedback")
# Initialize FastAPI app
app = FastAPI()
# Set up an in-memory vector store for storing memories
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)
# Create memory tools for managing and searching long-term memories
manage_memory_tool = create_manage_memory_tool(namespace=("memories",))
search_memory_tool = create_search_memory_tool(namespace=("memories",))
# Create a react agent integrated with memory capabilities
agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest",
    tools=[manage_memory_tool, search_memory_tool],
    store=store,
)
# Optionally, set up an episodic memory manager to capture detailed episodes
episode_manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    schemas=[Episode],
    instructions="Extract complete episodes capturing context, reasoning, action, and result.",
    enable_inserts=True,
)
# Pydantic models for API requests
class Message(BaseModel):
    role: str
    content: str
class ChatRequest(BaseModel):
    messages: List[Message]
@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    # Convert messages to dict format
    messages = [msg.dict() for msg in chat_request.messages]
    
    # Invoke the agent to process the conversation.
    # The agent will automatically extract and store relevant memories.
    response = agent.invoke({"messages": messages})
    
    # Additionally, extract detailed episodic memory from this conversation
    episodes = episode_manager.invoke({"messages": messages})
    if episodes:
        print("Extracted Episode Memory:", episodes[0])
    
    return response
# Run the app using uvicorn if this script is executed directly.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)