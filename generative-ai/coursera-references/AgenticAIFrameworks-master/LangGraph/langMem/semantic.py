from langmem import create_memory_manager
from pydantic import BaseModel, Field

# Define a schema for semantic memory: storing user preferences or facts.
class UserPreference(BaseModel):
    fact: str = Field(..., description="Key fact or preference")
    detail: str | None = Field(None, description="Additional context")
# Create a memory manager for semantic memory extraction.
semantic_manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    schemas=[UserPreference],
    instructions="Extract key facts and preferences from the conversation.",
    enable_inserts=True
)
# Sample conversation that contains semantic facts.
conversation = [
    {"role": "user", "content": "I really enjoy using dark mode on my devices."},
    {"role": "assistant", "content": "Got it!"},
    {"role": "user", "content": "Also, I work as a data scientist at Acme Corp."},
]
# Extract semantic memories.
semantic_memories = semantic_manager.invoke({"messages": conversation})
# Display the extracted semantic facts.
for mem in semantic_memories:
    print(mem)