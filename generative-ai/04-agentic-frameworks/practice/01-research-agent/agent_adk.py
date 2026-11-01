"""Note 04: the same research agent on Google ADK, with a custom BaseLlm stub."""
import asyncio
from itertools import count

from google.adk.agents import LlmAgent
from google.adk.models import BaseLlm, LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from research_lab import SYSTEM_PROMPT, Final, Observation, count_tokens, decide, parse_known, publish_report, read_source, search

_ids = count(1)


class StubLlm(BaseLlm):
    """ADK sends LlmRequest here instead of to Gemini. Same brain as the LangGraph stub."""
    model: str = "research-stub"
    behavior: str = "normal"

    async def generate_content_async(self, llm_request, stream=False):
        question, asked, observations = None, {}, []
        for content in llm_request.contents:
            for part in content.parts or []:
                if part.text and content.role == "user" and question is None:
                    question = part.text
                if part.function_call:
                    asked[part.function_call.id] = part.function_call
                if part.function_response:
                    call = asked[part.function_response.id]
                    observations.append(Observation(call.name, dict(call.args),
                                                    str(part.function_response.response.get("result", part.function_response.response))))
        system = str(llm_request.config.system_instruction or "")
        step = decide(question, observations, self.behavior, parse_known(system))
        if isinstance(step, Final):
            parts = [types.Part(text=step.text)]
        else:
            call = types.FunctionCall(id=f"adk_{next(_ids)}", name=step.name, args=step.args)
            parts = [types.Part(text=step.thought), types.Part(function_call=call)]
        prompt = count_tokens(system + str(llm_request.contents))
        completion = sum(count_tokens(p.text) for p in parts if p.text)
        yield LlmResponse(
            content=types.Content(role="model", parts=parts),
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=prompt, candidates_token_count=completion,
                total_token_count=prompt + completion),
        )


def build_agent(model=None, tools=(search, read_source, publish_report), **kwargs):
    return LlmAgent(name="research_agent", model=model or StubLlm(), instruction=SYSTEM_PROMPT,
                    tools=list(tools), **kwargs)


async def ask(agent, question, session_service=None, session_id="s1", run_config=None, plugins=None):
    """Run one user turn and return every event ADK emitted."""
    session_service = session_service or InMemorySessionService()
    if not await session_service.get_session(app_name="lab", user_id="u1", session_id=session_id):
        await session_service.create_session(app_name="lab", user_id="u1", session_id=session_id)
    runner = Runner(app_name="lab", agent=agent, session_service=session_service, plugins=plugins)
    message = types.Content(role="user", parts=[types.Part(text=question)])
    return [event async for event in runner.run_async(user_id="u1", session_id=session_id,
                                                      new_message=message, run_config=run_config)]


def show(events) -> None:
    """Print a run one part per line, the same shape as the LangGraph printout."""
    for event in events:
        for part in (event.content.parts if event.content else None) or []:
            if part.function_call:
                print(f"model  -> {part.function_call.name}({dict(part.function_call.args)})")
            elif part.function_response:
                result = str(part.function_response.response.get("result", part.function_response.response))
                print(f"tool   <- {result[:70].replace(chr(10), ' ; ')}")
            elif part.text and event.is_final_response():
                print(f"model  => {part.text}")


if __name__ == "__main__":
    from research_lab import QUESTION
    show(asyncio.run(ask(build_agent(), QUESTION)))
