"""Note 07: a stub chat model for LCEL, with bind_tools so structured output runs offline."""
import json
from itertools import count
from typing import Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

_ids = count(1)


class RuleModel(BaseChatModel):
    """Replies from a function of the prompt text. Tool-bound copies reply with a tool call."""
    rule: Callable[[str], str]
    bound_tool: str | None = None

    @property
    def _llm_type(self) -> str:
        return "rule-stub"

    def bind_tools(self, tools, tool_choice=None, **kwargs):
        name = tools[0]["function"]["name"] if isinstance(tools[0], dict) else getattr(tools[0], "__name__", tools[0].name)
        return self.model_copy(update={"bound_tool": name})

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        text = self.rule("\n".join(str(m.content) for m in messages))
        if self.bound_tool:
            call = {"name": self.bound_tool, "args": json.loads(text), "id": f"call_{next(_ids)}", "type": "tool_call"}
            message = AIMessage(content="", tool_calls=[call])
        else:
            message = AIMessage(content=text)
        return ChatResult(generations=[ChatGeneration(message=message)])
