import os
import time
from dotenv import load_dotenv

load_dotenv()
import autogen
from autogen import AssistantAgent, UserProxyAgent
from pathlib import Path
from autogen.coding import LocalCommandLineCodeExecutor

llm_config = [{

    "model": "mistral-large-latest",
    "api_key": os.environ.get("MISTRAL_API_KEY"),
    "api_type": "mistral"
}]

workdir = Path("coding")
workdir.mkdir(exist_ok=True)

# function for making a move in chess

import random
import chess
import chess.svg
from IPython.display import display, SVG
from typing_extensions import Annotated

board = chess.Board()

def make_move() -> Annotated[str, 'A move in UCI format']:

    moves = list(board.legal_moves)
    move = random.choice(moves)
    board.push(move)

    # display the board
    svg_board = chess.svg.board(board=board, size=400)
    display(SVG(svg_board))

    return str(move)

# chess library is used above to make a move

from autogen import ConversableAgent, register_function

player_white = ConversableAgent(
    name='player_white',
    system_message='You are playing as white. Always call make_move() function to make a move.',
    llm_config={"config_list": llm_config, 'cache_seed': True}
)

player_black = ConversableAgent(
    name='player_black',
    system_message='You are playing as black. Always call make_move() function to make a move.',
    llm_config={"config_list": llm_config, 'cache_seed': True}
)

board_proxy = ConversableAgent(
    name="Board Proxy",
    llm_config=False,
    is_termination_msg=lambda msg: "tool_calls" not in msg,
)

# register tools for the agents
register_function(
    make_move,
    caller=player_white,
    name='make_move',
    executor=board_proxy,
    description='Make a move in chess',
)

register_function(
    make_move,
    caller=player_black,
    name='make_move',
    executor=board_proxy,
    description='Make a move in chess',
)

# Nested chats allows each player agent to chat with the board proxy agent to make a move,
# before communicating with the other player agent.

player_white.register_nested_chats(
    trigger=player_black,
    chat_queue=[{
        "sender": board_proxy,
        "recipient": player_white,
    }],
)

player_black.register_nested_chats(
    trigger=player_white,
    chat_queue=[{
        "sender": board_proxy,
        "recipient": player_black,
    }],
)

# clearing the board and starting the chess game

board = chess.Board()

# initiating the chat between the players

for _ in range(5):
    chat_result = player_white.initiate_chat(
        player_black,
        message='Lets play Chess! Your move:',
        max_turns=1,
    )
    time.sleep(5)  # Add delay to avoid rate limit
