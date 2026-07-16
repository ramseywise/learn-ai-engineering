import os 
from typing import Annotated
from dotenv import load_dotenv
load_dotenv()
from tavily import TavilyClient
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, register_function
# from autogen.agentchat.contrib.capabilities import teachability
from autogen.cache import Cache
from autogen.coding import LocalCommandLineCodeExecutor

config_list = [
    {"model": "gemini-1.5-flash", "api_key": os.environ.get("GOOGLE_API_KEY"), "api_type": "google"},
    {"model": "codestral-latest", "api_key": os.environ.get("MISTRAL_API_KEY"), "api_type": "mistral"}
]

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

tavily = TavilyClient (api_key=TAVILY_API_KEY) 

def search_tool (query : Annotated[str , "The search query"]) -> Annotated[str , 'The Search results'] :
    return tavily.get_search_context (query , search_depth='advanced')

#react prompt 

ReAct_prompt = ''' 

Answer the following questions as best as you can. You have access to search tools provided.

Use the following question format:

Question: the input question you must answer
Thought: you should always think about what you do 
Action: the action to take
Action Input: the input to the action
Observation: the result of the action
...( this process can be repeated multiple times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Begin!

Question : {input}

'''

def react_prompt_message (sender, recipient, context): 
    return ReAct_prompt.format (input = context['question'])


# setting up code executor 

os.makedirs ("coding" , exist_ok = True)

code_executor = LocalCommandLineCodeExecutor( work_dir= "coding")

user_proxy = UserProxyAgent (
    name = "User",
    is_termination_msg = lambda x: x.get('content' , '') and x.get('content' , '').rstrip().endswith('TERMINATE'),
    human_input_mode= "ALWAYS",
    max_consecutive_auto_reply=10,
    code_execution_config={"executor": code_executor},
)

assistant = AssistantAgent (
    name = "Assistant",
    llm_config = {"config_list": config_list , "cache_seed" : None} ,
    system_message = "Only use the tools you have access to. Reply TERMINATE when task is done",
)

register_function (
    search_tool,
    caller = assistant,
    executor= user_proxy,
    name = "search_tool",
    description= 'Search the web for a given query',
)

with Cache.disk(cache_seed=43) as cache :
    user_proxy.initiate_chat (
        assistant,
        message= react_prompt_message , 
        question = 'What is the weather and Air quality in New Delhi today?',
        cache = cache,
    )