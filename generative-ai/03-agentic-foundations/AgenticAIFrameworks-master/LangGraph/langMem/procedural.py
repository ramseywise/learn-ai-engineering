from langmem import create_prompt_optimizer
# Create a prompt optimizer for procedural memory.
optimizer = create_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest",
    kind="metaprompt",
    config={"max_reflection_steps": 3}
)
# Define the initial system prompt.
initial_prompt = "You are a helpful assistant."
# Simulate a conversation trajectory and feedback.
trajectory = [
    [
        {"role": "user", "content": "Explain inheritance in Python."},
        {"role": "assistant", "content": "Inheritance allows classes to inherit features from other classes."},
        {"role": "user", "content": "Can you give me a concrete code example?"}
    ],
    {"user_score": 0.3, "feedback": "The explanation was too vague and lacked practical detail."}
]
# Optimize the system prompt based on the conversation and feedback.
optimized_prompt = optimizer.invoke({
    "trajectories": [(trajectory[0], trajectory[1])],
    "prompt": initial_prompt
})
print("Optimized Prompt:")
print(optimized_prompt)