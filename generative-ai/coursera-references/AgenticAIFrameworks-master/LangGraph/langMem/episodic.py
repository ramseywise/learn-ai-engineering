from langmem import create_memory_manager
from pydantic import BaseModel, Field

# Define an Episode schema to capture full interaction details.
class Episode(BaseModel):
    observation: str = Field(..., description="Context or situation")
    thoughts: str = Field(..., description="Internal reasoning process")
    action: str = Field(..., description="Action taken by the agent")
    result: str = Field(..., description="Outcome of the action")
# Create a memory manager for episodic memory.
episodic_manager = create_memory_manager(
    "anthropic:claude-3-5-sonnet-latest",
    schemas=[Episode],
    instructions="Extract a detailed episode from the conversation including context, reasoning, action, and result.",
    enable_inserts=True
)
# Sample conversation that provides context for an episodic memory.
conversation = [
    {"role": "user", "content": "What is a binary tree? I work with family trees, so maybe you can relate."},
    {"role": "assistant", "content": (
        "A binary tree is like a family tree, but each parent has at most 2 children. "
        "For example, think of Bob as the parent, with Amy and Carl as the children."
    )},
    {"role": "user", "content": "Oh, that makes sense! I see the analogy now."},
]
# Extract episodic memory.
episodes = episodic_manager.invoke({"messages": conversation})
# Display the extracted episode.
for ep in episodes:
    print(ep)