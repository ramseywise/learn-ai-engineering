from agents import Agent, Runner
import os
from dotenv import load_dotenv
import config as _config
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

agent = Agent (name = 'Assistant' , instructions= 'You are a helpful assistant.', model= 'gpt-3.5-turbo' )

result = Runner.run_sync (agent, 'Write code for fibonannci series in c++.')

print (result)