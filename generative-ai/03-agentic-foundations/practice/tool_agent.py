# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""A key-free tool-calling agent for notes/02: the loop, dispatch and error handling are real, only the model is scripted.

Run from this folder (under a second, standard library only, no API key):
    uv run tool_agent.py

The stub speaks the shape of the Messages API: content blocks, `tool_use`, `tool_result` and `stop_reason`. It also
checks what a real API rejects, so a loop that drops a result or sends a wrong ID fails here too. Each scripted turn is
a function of the conversation, so a model "fixing" its call depends on what your error message really said. The
tools, the stock data and the scripted decisions are invented for this lab. The sizes printed are characters re-sent
in this run, a stand-in for input tokens, not a measurement of any model.
"""
# %%
import json
from dataclasses import dataclass
from types import SimpleNamespace as NS

STOCK = {"itemA": {"on_hand": 500, "peak_weekly": 90, "weeks_to_deliver": 2},
         "itemB": {"on_hand": 100, "peak_weekly": 90, "weeks_to_deliver": 2}}
MAX_STEPS = 6


# %% Tools: a registry with a schema for each, so dispatch can check arguments before anything runs
class TransientError(Exception):
    pass


class Warehouse:
    """Tool state for one run. `down_for` makes the first calls to get_stock fail, as a flaky service would."""

    def __init__(self, down_for=0):
        self.down_for, self.orders = down_for, []

    def get_stock(self, item):
        if self.down_for > 0:
            self.down_for -= 1
            raise TransientError("warehouse service timed out")
        if item not in STOCK:
            raise KeyError(item)
        return STOCK[item]

    def place_order(self, item, quantity):
        if item not in STOCK:
            raise KeyError(item)
        self.orders.append((item, quantity))
        return {"ordered": quantity, "item": item}


SCHEMAS = {
    "get_stock": {"required": {"item": str}},
    "place_order": {"required": {"item": str, "quantity": int}},
}


def check_args(name, args):
    """Return a problem with the arguments, or None. Runs before the tool does."""
    schema = SCHEMAS[name]["required"]
    if missing := sorted(set(schema) - set(args)):
        return f"missing {missing}"
    if extra := sorted(set(args) - set(schema)):
        return f"unexpected {extra}"
    for key, kind in schema.items():
        if not isinstance(args[key], kind) or isinstance(args[key], bool):
            return f"{key} must be {kind.__name__}, got {args[key]!r}"
    if args.get("quantity", 1) <= 0:
        return f"quantity must be positive, got {args['quantity']}"
    return None


def dispatch(warehouse, name, args, vague=False):
    """Run one call. Every failure comes back as a result the model can read, and the loop keeps going."""
    def fail(message):
        return ("Error" if vague else f"Error: {message}"), True

    if name not in SCHEMAS:
        return fail(f"unknown tool {name}. Tools: {sorted(SCHEMAS)}")
    if problem := check_args(name, args):
        return fail(f"bad arguments for {name}: {problem}")
    try:
        return json.dumps(getattr(warehouse, name)(**args)), False
    except KeyError:
        return fail(f"no item {args['item']!r}. Known items: {sorted(STOCK)}")
    except TransientError as e:
        return fail(f"{e}. This may be temporary, so retry once.")


# %% The stub model: checks the protocol as an API would, then plays the next scripted turn
class ProtocolError(Exception):
    pass


def check_protocol(messages):
    """Every tool_use must be answered by a tool_result with its ID in the very next user message."""
    for i, m in enumerate(messages):
        if m["role"] != "assistant":
            continue
        asked = {b.id for b in m["content"] if b.type == "tool_use"}
        if not asked:
            continue
        follow = messages[i + 1]["content"] if i + 1 < len(messages) else []
        got = {r["tool_use_id"] for r in follow if isinstance(r, dict) and r.get("type") == "tool_result"}
        if asked != got:
            raise ProtocolError(f"tool_use ids {sorted(asked)} answered by {sorted(got)}")


class StubClient:
    def __init__(self, turn):
        self.turn, self.sizes = turn, []
        self.messages = self

    def create(self, messages, **_):
        check_protocol(messages)
        self.sizes.append(sum(len(str(m["content"])) for m in messages))
        return self.turn(messages, len(self.sizes))


def call(id_, name, **args):
    return NS(type="tool_use", id=id_, name=name, input=args)


def tools(*blocks):
    return NS(stop_reason="tool_use", content=list(blocks))


def say(text):
    return NS(stop_reason="end_turn", content=[NS(type="text", text=text)])


def last_results(messages):
    return [r["content"] for r in messages[-1]["content"]] if isinstance(messages[-1]["content"], list) else []


# %% The loop
@dataclass
class Run:
    stop: str
    answer: str
    calls: int
    errors: int
    sent: list
    orders: list


def run_agent(turn, prompt, warehouse=None, vague=False, max_steps=MAX_STEPS, repeat_limit=2):
    warehouse = warehouse or Warehouse()
    client, seen = StubClient(turn), {}
    messages = [{"role": "user", "content": prompt}]
    calls = errors = 0
    for _ in range(max_steps):
        response = client.messages.create(model="stub", max_tokens=1000, tools=sorted(SCHEMAS), messages=messages)
        if response.stop_reason != "tool_use":
            text = next(b.text for b in response.content if b.type == "text")
            return Run(response.stop_reason, text, calls, errors, client.sizes, warehouse.orders)
        messages.append({"role": "assistant", "content": response.content})    # the call goes in before its result
        results = []
        for block in response.content:                                         # one turn can hold several calls
            if block.type != "tool_use":
                continue
            calls += 1
            key = (block.name, json.dumps(block.input, sort_keys=True))
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > repeat_limit:
                output, failed = f"Error: {block.name} already failed or ran {repeat_limit} times with these arguments. Stop and report.", True
            else:
                output, failed = dispatch(warehouse, block.name, block.input, vague)
            errors += failed
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": failed})
        messages.append({"role": "user", "content": results})
    return Run("step cap", "I couldn't finish; here is where I got to.", calls, errors, client.sizes, warehouse.orders)


# %% Scripted turns, each a function of what the tools really returned
def happy(messages, n):
    if n == 1:
        return tools(call("t1", "get_stock", item="itemB"))
    return say("itemB runs out before delivery. Reorder.")


def corrects_from_error(messages, n):
    """Starts with a wrong ID. Moves on only if the error names a valid one, and otherwise repeats itself."""
    if n == 1:
        return tools(call("t1", "get_stock", item="item-B"))
    result = last_results(messages)[0] if last_results(messages) else ""
    if "Known items" in result:
        return tools(call(f"t{n}", "get_stock", item="itemB"))
    if result.startswith("Error"):
        return tools(call(f"t{n}", "get_stock", item="item-B"))
    return say("itemB runs out before delivery. Reorder.")


def wrong_arguments(messages, n):
    if n == 1:
        return tools(call("t1", "place_order", item="itemB", quantity="ninety"))
    if "must be int" in last_results(messages)[0]:
        return tools(call("t2", "place_order", item="itemB", quantity=90))
    return say("Ordered 90 of itemB.")


def invented_tool(messages, n):
    if n == 1:
        return tools(call("t1", "check_inventory", item="itemB"))
    if "Tools:" in last_results(messages)[0]:
        if n == 2:
            return tools(call("t2", "get_stock", item="itemB"))
    return say("itemB runs out before delivery. Reorder.")


def flaky_tool(messages, n):
    if n >= 2 and not last_results(messages)[0].startswith("Error"):
        return say("itemB runs out before delivery. Reorder.")
    return tools(call(f"t{n}", "get_stock", item="itemB"))


def parallel(messages, n):
    if n == 1:
        return tools(call("a", "get_stock", item="itemA"), call("b", "get_stock", item="item-B"))
    if n == 2:
        return tools(call("c", "get_stock", item="itemB"))
    return say("itemA is fine. itemB needs reordering.")


def never_stops(messages, n):
    """Each call differs, so only the step cap can stop it."""
    return tools(call(f"t{n}", "get_stock", item=f"item{n}"))


def buggy_loop_demo():
    """A loop that forgets the second result. The stub rejects the next call, as an API would."""
    client = StubClient(parallel)
    messages = [{"role": "user", "content": "Check both."}]
    first = client.messages.create(messages=messages)
    messages.append({"role": "assistant", "content": first.content})
    messages.append({"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "a", "content": "{}"}]})         # result for "b" is missing
    try:
        client.messages.create(messages=messages)
    except ProtocolError as e:
        return f"rejected: {e}"
    return "accepted"


# %% Report
SCENARIOS = [
    ("happy path", happy, {}),
    ("wrong ID, helpful error", corrects_from_error, {}),
    ("wrong ID, error says only 'Error'", corrects_from_error, {"vague": True}),
    ("wrong argument type", wrong_arguments, {}),
    ("invented tool name", invented_tool, {}),
    ("tool fails once, then recovers", flaky_tool, {"warehouse": Warehouse(down_for=1)}),
    ("two calls in one turn, one fails", parallel, {}),
    ("model never stops", never_stops, {}),
]

if __name__ == "__main__":
    print(f"{'scenario':36}{'stop':10}{'calls':>6}{'errors':>7}{'chars re-sent per call':>32}  orders")
    for name, turn, kwargs in SCENARIOS:
        r = run_agent(turn, "Should we reorder itemB?", **kwargs)
        print(f"{name:36}{r.stop:10}{r.calls:>6}{r.errors:>7}{str(r.sent):>32}  {r.orders or '-'}")
    print("\nforgetting one result in a parallel turn:", buggy_loop_demo())
