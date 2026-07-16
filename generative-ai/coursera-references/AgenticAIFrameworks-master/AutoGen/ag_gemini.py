import os
from dotenv import load_dotenv

load_dotenv()
import autogen
from autogen import AssistantAgent, UserProxyAgent
from pathlib import Path
from autogen.coding import LocalCommandLineCodeExecutor


llm_config = [ {

    "model" : "gemini-1.5-flash" ,
    "api_key" : os.environ.get("GOOGLE_API_KEY"),
    "api_type": "google"
} ]

workdir = Path("coding")
workdir.mkdir(exist_ok=True)


system_message = """You are a helpful AI assistant who writes code and the user executes it.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) for the user to execute.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
IMPORTANT: Wait for the user to execute your code and then you can reply with the word "FINISH". DO NOT OUTPUT "FINISH" after your code block."""



assistant = AssistantAgent(
    name = "gemini flash assistant", 
    llm_config= {"config_list": llm_config}, 
    system_message= system_message, 
    human_input_mode="NEVER"
    )


user_proxy = UserProxyAgent(
    "user_proxy",
    code_execution_config={"work_dir": "coding", "use_docker": False},
    human_input_mode="NEVER",
    is_termination_msg= lambda msg: "FINISH" in msg.get("content"),
    
)

chat_reult = user_proxy.initiate_chat (

    assistant, message= 'Sort the array with Bubble Sort: [4, 1, 5, 2, 3]',
)



