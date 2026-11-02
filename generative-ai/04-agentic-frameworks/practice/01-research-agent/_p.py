import asyncio, logging
logging.disable(logging.CRITICAL)
from itertools import count
import agent_adk, agent_langgraph, agent_scratch
from research_lab import QUESTION
from google.adk.agents.run_config import RunConfig
print('RunConfig default max_llm_calls', RunConfig().max_llm_calls)
class CountingChat(agent_langgraph.StubChatModel):
    pass
n={'lc':0}
orig=agent_langgraph.StubChatModel._generate
def gen(self,*a,**k):
    n['lc']+=1; return orig(self,*a,**k)
agent_langgraph.StubChatModel._generate=gen
g=agent_langgraph.build_agent(agent_langgraph.StubChatModel(behavior='stubborn'))
print(g.config)
import time;t=time.time()
try: g.invoke({'messages':[('user',QUESTION)]})
except Exception as e: print(type(e).__name__, str(e)[:100])
print('lg model calls',n['lc'],time.time()-t)
try:
    print(agent_scratch.query(QUESTION,verbose=False,model=lambda m:agent_scratch.text_model(m,'stubborn')))
except Exception as e: print(e)
n2=[0]
orig2=agent_adk.StubLlm.generate_content_async
async def g2(self,*a,**k):
    n2[0]+=1
    async for x in orig2(self,*a,**k): yield x
agent_adk.StubLlm.generate_content_async=g2
t=time.time()
try: asyncio.run(agent_adk.ask(agent_adk.build_agent(agent_adk.StubLlm(behavior='stubborn')),QUESTION))
except Exception as e: print(type(e).__name__, str(e)[:100])
print('adk calls',n2[0],time.time()-t)
