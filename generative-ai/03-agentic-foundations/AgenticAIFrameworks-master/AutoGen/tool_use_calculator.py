import os 
from typing import Annotated , Literal
from dotenv import load_dotenv
load_dotenv()
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, register_function, ConversableAgent

from autogen.cache import Cache
from autogen.coding import LocalCommandLineCodeExecutor

config_list = [
    {"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")},
    # {"model": "gemini-1.5-flash", "api_key": os.environ.get("GOOGLE_API_KEY"), "api_type": "google"},
#     {"model": "codestral-latest", "api_key": os.environ.get("MISTRAL_API_KEY"), "api_type": "mistral"}
]

operator = Literal["+" , "-" , "*" , "/"]

def calculator (a: int , b:int , operator : Annotated[operator , "operator"]) -> int:
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return int(a / b)
    else:
        raise ValueError("Invalid operator")
    


assistant = ConversableAgent (
    name='assistant' , 
    system_message= 'you are a helpful assistant, please help with simple calculations. Return TERMINATE when task is done',
    llm_config=  { "config_list" :config_list}                           
    )

user_proxy = ConversableAgent (

    name = 'User',
    llm_config=False,
    is_termination_msg= lambda msg: msg.get('content') is not None and 'TERMINATE' in msg['content'],
    human_input_mode="NEVER",
)

assistant.register_for_llm(name='calculator' , description= 'A simple calculator')(calculator)

user_proxy.register_for_execution(name='calculator')(calculator)


register_function(
    calculator,
    caller=assistant,  # The assistant agent can suggest calls to the calculator.
    executor=user_proxy,  # The user proxy agent can execute the calculator calls.
    name="calculator",  # By default, the function name is used as the tool name.
    description="A simple calculator",  # A description of the tool.
)

chat_result = user_proxy.initiate_chat(assistant, message="What is (44232 + 13312 / (232 - 32)) * 5?")