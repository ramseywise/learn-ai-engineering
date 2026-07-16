from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel
from smolagents import LiteLLMModel
from smolagents import HfApiModel

model = HfApiModel(
    model_id="deepseek-ai/DeepSeek-R1",
    provider="together",
)

model2 = LiteLLMModel(
    model_id="anthropic/claude-3-5-sonnet-latest",
    temperature=0.2,
    api_key=os.environ["ANTHROPIC_API_KEY"]
)
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

response = agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")


requests_to_search = ["gulf of mexico america", "greenland denmark", "tariffs"]
for request in requests_to_search:
    print(f"Here are the search results for {request}:", web_search(request))

     
print (response)

