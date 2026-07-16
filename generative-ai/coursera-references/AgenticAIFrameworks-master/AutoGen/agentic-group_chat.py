import os 

from dotenv import load_dotenv
load_dotenv()
from autogen import ConversableAgent, GroupChat, GroupChatManager


config_list = [
    {"model": "gemini-1.5-flash", "api_key": os.environ.get("GOOGLE_API_KEY"), "api_type": "google"},
]

#agents : 

# The Number Agent always returns the same numbers.
number_agent = ConversableAgent(
    name="Number_Agent",
    system_message="You return me the numbers I give you, one number each line.",
    llm_config = {'config_list' : config_list},
    human_input_mode="NEVER",
)

# The Adder Agent adds 1 to each number it receives.
adder_agent = ConversableAgent(
    name="Adder_Agent",
    system_message="You add 1 to each number I give you and return me the new numbers, one number each line.",
    llm_config = {'config_list' : config_list},
    human_input_mode="NEVER",
)

# The Multiplier Agent multiplies each number it receives by 2.
multiplier_agent = ConversableAgent(
    name="Multiplier_Agent",
    system_message="You multiply each number I give you by 2 and return me the new numbers, one number each line.",
    llm_config = {'config_list' : config_list},
    human_input_mode="NEVER",
)

# The Subtracter Agent subtracts 1 from each number it receives.
subtracter_agent = ConversableAgent(
    name="Subtracter_Agent",
    system_message="You subtract 1 from each number I give you and return me the new numbers, one number each line.",
    llm_config = {'config_list' : config_list},
    human_input_mode="NEVER",
)

# The Divider Agent divides each number it receives by 2.
divider_agent = ConversableAgent(
    name="Divider_Agent",
    system_message="You divide each number I give you by 2 and return me the new numbers, one number each line.",
    llm_config = {'config_list' : config_list},
    human_input_mode="NEVER",
)


group_chat = GroupChat(
    agents= [adder_agent , multiplier_agent , subtracter_agent , divider_agent , number_agent],
    messages=[],
    max_round=10,
)

group_chat_manager = GroupChatManager(
    groupchat= group_chat,
    llm_config = {'config_list' : config_list}
)


chat_result = number_agent.initiate_chat(
    group_chat_manager,
    message="My number is 3, I want to turn it into 13.",
    summary_method="reflection_with_llm",
)