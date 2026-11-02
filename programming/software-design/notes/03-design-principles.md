---
origin: synthesis
sources:
  - "D. L. Parnas, On the Criteria To Be Used in Decomposing Systems into Modules, CACM 15(12), 1972 — https://doi.org/10.1145/361598.361623"
  - "John Ousterhout and Robert C. Martin, A Philosophy of Software Design vs Clean Code (2024-25) — https://github.com/johnousterhout/aposd-vs-clean-code"
  - "Robert C. Martin, The Single Responsibility Principle (2014) — https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html"
  - "Robert C. Martin, Solid Relevance (2020) — https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html"
  - "Barbara Liskov and Jeannette Wing, A Behavioral Notion of Subtyping, TOPLAS 16(6), 1994 — https://doi.org/10.1145/197320.197383"
  - "Dan North, CUPID: for joyful coding (2022) — https://dannorth.net/blog/cupid-for-joyful-coding/"
  - "Sandi Metz, The Wrong Abstraction (2016) — https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction"
  - "Dan Abramov, Goodbye, Clean Code (2020) — https://overreacted.io/goodbye-clean-code/"
  - "Casey Muratori, 'Clean' Code, Horrible Performance (2023) — https://www.computerenhance.com/p/clean-code-horrible-performance"
  - "Martin Fowler, Yagni (2015) and BeckDesignRules (2015) — https://martinfowler.com/bliki/Yagni.html , https://martinfowler.com/bliki/BeckDesignRules.html"
  - "Fred Brooks, No Silver Bullet (1986) — https://doi.org/10.1109/MC.1987.1663532"
  - "Ben Moseley and Peter Marks, Out of the Tar Pit (2006) — https://curtclifton.net/papers/MoseleyMarks06a.pdf"
concepts: [coupling, cohesion, information-hiding, deep-modules, wrong-abstraction, yagni, simple-design, solid, liskov-substitution, dependency-inversion, cupid, essential-complexity]
confidence: high
cleaned: 2026-11-02
---
# 3 — Design principles

> Design principles are compressed arguments about what makes change expensive. This chapter starts with the oldest and strongest, Parnas's information hiding, then goes through deep modules, duplication, YAGNI and SOLID. SOLID gets a fair hearing from both directions, because its critics have good points and so do its defenders, and in the end you need to know what each one is afraid of. There's a measurement too: Muratori's "clean code is slow" result re-run in Python, where the answer comes out differently. Code ran on CPython 3.14.7.

---

## Information hiding: decide what each module keeps secret

The question of how to divide a system into modules has a 1972 answer that still holds. [Parnas](https://doi.org/10.1145/361598.361623) compares two decompositions of the same small program. The first makes each major processing step a module; "one makes a flowchart", he says. In the second, each module is characterised by its knowledge of a design decision it hides from all the others, and its interface is chosen to reveal as little as possible about how it works. They may run the same way, but they respond differently to change: in the flowchart version, changing a storage format touches every module that shares it.

Here's the same contrast for an embedding store, when you need to change how vectors are stored:

```python
import array
import math

# Flowchart decomposition: every step knows the store is a list of (id, list[float]).
def load_step(rows):
    return [(row_id, list(vector)) for row_id, vector in rows]

def norm_step(store):
    return [(row_id, [x / math.hypot(*v) for x in v]) for row_id, v in store]

def search_step(store, query):
    return max(store, key=lambda item: sum(a * b for a, b in zip(item[1], query)))[0]

# Information hiding: one class knows the layout; callers know add and nearest.
class VectorStore:
    """Layout is private. It's flat array('f') today; it could be a file tomorrow."""

    def __init__(self, dim: int):
        self._dim = dim
        self._ids: list[str] = []
        self._flat = array.array("f")

    def add(self, row_id: str, vector: list[float]) -> None:
        length = math.hypot(*vector)
        self._ids.append(row_id)
        self._flat.extend(x / length for x in vector)

    def nearest(self, query: list[float]) -> str:
        def score(i: int) -> float:
            start = i * self._dim
            return sum(a * b for a, b in zip(self._flat[start:start + self._dim], query))
        return self._ids[max(range(len(self._ids)), key=score)]

rows = [("refunds", [1.0, 0.0]), ("shipping", [0.6, 0.8])]
print(search_step(norm_step(load_step(rows)), [0.0, 1.0]))
store = VectorStore(dim=2)
for row_id, vector in rows:
    store.add(row_id, vector)
print(store.nearest([0.0, 1.0]))
```

```text
shipping
shipping
```

Moving from lists to a flat `array` changes three functions in the first version and one class in the second. So ask of any module: what does it know that nothing else does? If the answer is "nothing", it's a step in a flowchart with a `def` around it.

Parnas even marks down his own good design. His circular-shift module promised an order for its output that callers didn't need, which he calls a design error because it ruled out some systems. That lesson is what a Python interface should keep: every promise you make, including accidental ones such as "the result happens to be sorted", is a thing you can't change later. He also notes that this decomposition, implemented naively as subroutine calls, will often be less efficient. Then and now, hiding has a cost.

**Coupling and cohesion** are the words people use for the result. [Martin](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) gives a working definition that doesn't depend on OO: raise cohesion between things that change for the same reasons, and lower coupling between things that change for different reasons. A useful test is to look at your commit history. Files that keep changing together are coupled, whatever the import graph says.

## Deep modules

Ousterhout's contribution is a way to judge an interface: compare what it costs to learn with what it hides. Here I'm relying on what he says in [the debate with Martin](https://github.com/johnousterhout/aposd-vs-clean-code) and his [Stanford page](https://web.stanford.edu/~ouster/cgi-bin/aposd.php); I haven't read *A Philosophy of Software Design* itself. A deep method has a simple interface over a lot of functionality. A shallow one's interface is about as complicated as its body, so it doesn't reduce what the programmer needs to know.

```python
# Shallow: the name restates the body, and the caller still knows everything.
def get_model_name(config: dict) -> str:
    return config["model"]["name"]

# Deep: one line to call, and the caller never learns about any of what's inside.
def fit_to_budget(messages: list[dict], token_budget: int, chars_per_token: int = 4) -> list[dict]:
    """Keep the system message and as many recent turns as fit, in original order."""
    system = [m for m in messages if m["role"] == "system"]
    cost = lambda m: len(m["content"]) // chars_per_token
    remaining = token_budget - sum(cost(m) for m in system)
    kept = []
    for message in reversed([m for m in messages if m["role"] != "system"]):
        if cost(message) > remaining:
            break
        kept.append(message)
        remaining -= cost(message)
    return system + kept[::-1]

config = {"model": {"name": "atlas-small"}}
chat = [{"role": "system", "content": "s" * 40}, {"role": "user", "content": "a" * 400},
        {"role": "assistant", "content": "b" * 40}, {"role": "user", "content": "c" * 40}]
print(get_model_name(config))
print([m["role"] for m in fit_to_budget(chat, token_budget=40)])
```

```text
atlas-small
['system', 'assistant', 'user']
```

Depth is an argument against a lot of "just wrap it" code. It's also a judgement, not a measure: Martin's side of the debate is the old One Thing rule: if he can meaningfully extract one method from another, the original did more than one thing. He adds that he'd rather err towards decomposing, since decompositions can always be inlined later. Depth is most useful for a public interface, where you're stuck with the decision. It matters less for private helpers you can redo in a minute.

## Duplication and the wrong abstraction

DRY is the most-followed principle here, and the most over-applied. Kent Beck's version, [as Fowler relays it](https://martinfowler.com/bliki/BeckDesignRules.html), says everything should be said once and only once, and Fowler calls removing duplication a powerful way to drive out good designs. Against that, [Sandi Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) makes a claim that has become a proverb, "duplication is far cheaper than the wrong abstraction", and describes how it happens: someone extracts a shared thing, a new requirement almost fits, someone adds a parameter and a conditional, and it repeats until nobody can read the result.

```python
# Three requirements later, one "shared" function.
def format_record(record: dict, for_eval=False, for_prompt=False, redact=False, max_chars=None) -> str:
    text = record["text"]
    if redact:
        text = text.replace(record.get("email", "\0"), "[email]")
    if for_prompt:
        text = f"[{record['id']}] {text}"
    if max_chars is not None:
        text = text[:max_chars]
    if for_eval:
        return f"{record['id']}\t{text}"
    return text

record = {"id": "doc-7", "text": "Contact ada@example.com for refunds.", "email": "ada@example.com"}
print(format_record(record, for_prompt=True, redact=True, max_chars=30))

# Metz's way out: inline into each caller, delete what that caller doesn't use.
def prompt_line(record: dict) -> str:
    text = record["text"].replace(record["email"], "[email]")
    return f"[{record['id']}] {text}"[:30]

def eval_line(record: dict) -> str:
    return f"{record['id']}\t{record['text']}"

print(prompt_line(record))
print(eval_line(record))
```

```text
[doc-7] Contact [email] for re
[doc-7] Contact [email] for re
doc-7	Contact ada@example.com for refunds.
```

Each caller ended up running a small subset of the code, which Metz says is common. Her warning sign is exact: if you find yourself passing parameters and adding conditional paths through shared code, the abstraction is wrong, even if it was once right. Her remedy is to go back, re-introduce the duplication, and only then look for a better abstraction, without letting sunk cost get in the way. [Dan Abramov](https://overreacted.io/goodbye-clean-code/) tells a similar story against himself. He deduplicated a colleague's resize handlers and was asked to revert it. His abstraction traded the ability to change requirements for less duplication, and later special cases would have made it far more convoluted. He also rewrote a teammate's code without talking to them, which he counts as the other failure.

Who is right? They're not really opposed. Beck's rule is about duplicated *knowledge*: the same fact stated twice. Metz and Abramov are warning about *coincidental* similarity: code that looks alike today and changes for different reasons. The lab's pricing branches repeat one formula for one reason, so a table is right. If two things have different reasons to change, leave them looking similar until they don't.

## YAGNI and simple design

[YAGNI](https://martinfowler.com/bliki/Yagni.html) says not to build a capability you presume you'll need later. Fowler splits the cost into the cost of build, delay and carry, plus the cost of repair for the right feature built wrong, and offers an estimate from Kohavi et al. that odds of being wrong are at least 2 in 3, since only a third of the features they analysed at Microsoft improved the metrics they were designed to improve. Two limits are often missed. YAGNI applies to presumptive features, not to making code easier to change, so refactoring doesn't violate it: "Yagni requires (and enables) malleable code". And it applies only when you add complexity now; a future-friendly choice that adds none is fine.

Fowler also concedes that sometimes YAGNI causes an expensive later change, though he thinks those cases are rare and that availability bias makes them memorable. A pragmatic exception, and this is my view rather than his: decisions with a very high cost of change, such as a public API, a wire format or anything you've persisted, deserve more thought up front, not because you'll need more features but because you can't easily take this one back. Ask whether you can undo it.

Kent Beck's [four rules of simple design](https://martinfowler.com/bliki/BeckDesignRules.html), in Fowler's wording and priority order, are a compact checklist you can apply now: passes the tests, reveals intention, no duplication, fewest elements. The last means anything that doesn't serve the first three should go. Beck told Fowler that when duplication and intention do conflict, usually in tests, "empathy wins over some strictly technical metric."

## SOLID and its critics

SOLID is five principles associated with Robert Martin. They're widely taught and widely argued about, and it's a common interview topic. Here's each in Python with what it's protecting against, what it costs and who objects. Python changes some of the answers, as Martin himself concedes for one of them.

### S: single responsibility

Martin's [own explanation](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) is often misquoted as "a class should do one thing". He means a module should answer to one group of people: "This principle is about people". His example puts pay calculation (the CFO's concern), reporting of hours (the COO's) and persistence (the CTO's) on one class, so a change requested by one breaks something another relies on.

[Dan North's objection](https://dannorth.net/blog/cupid-for-joyful-coding/) is about where it leads. He says the textbook split of a report's content from its format creates artificial seams, since the most common change, a new field, touches both together. In his view "does one thing well" is an outside-in property of a component's purpose, and SRP is an inside-out statement about how code is organised. Frameworks that take it to mean separate view and controller files can spread one product change across the code base, adding cognitive load.

```python
# Pricing answers to finance and rendering answers to whoever reads the report.
# Do they change for different reasons? Pricing: yes, separately. A new field: no.
from dataclasses import dataclass

@dataclass(frozen=True)
class Line:
    model: str
    tokens: int
    cost: float

def price(model: str, tokens: int, per_1k: dict[str, float]) -> Line:
    return Line(model, tokens, tokens / 1000 * per_1k[model])

def render(line: Line) -> str:
    return f"{line.model:<12} {line.tokens:>7} {line.cost:>8.4f}"

print(render(price("atlas-small", 5000, {"atlas-small": 0.0008})))
```

```text
atlas-small     5000   0.0040
```

Both are right about this example. A price-sheet update never touches `render`. Adding a cached-token column touches both. So look at the actual history of changes, then split along what changes separately. Martin's wording, "reasons to change", is sound when you take it seriously, since it's an empirical question.

### O: open for extension, closed for modification

[Martin's summary](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html): a module should be extendable without being modified, as with device independence, where a program needn't care whether it writes to a file or a pipe. North's slides reportedly answer "write simple code", as Martin quotes them (I've read North's CUPID article and Martin's reply, not the slides). In Python, this is typically a registry or a function argument:

```python
import json
from typing import Callable

Exporter = Callable[[dict], str]
EXPORTERS: dict[str, Exporter] = {"json": json.dumps}

def export(result: dict, fmt: str) -> str:
    return EXPORTERS[fmt](result)

# A new format needs no edit to export().
EXPORTERS["tsv"] = lambda result: "\t".join(str(value) for value in result.values())

print(export({"model": "atlas-small", "score": 0.91}, "tsv"))
```

```text
atlas-small	0.91
```

The cost: you've opened the extension point you predicted, and it will be the wrong one sometimes. Fowler's YAGNI article quotes Jeremy Miller: an extensibility point that's never used isn't just wasted effort, it's likely to get in your way. For code you own and can edit, editing is usually fine. OCP matters most at a boundary where you can't edit the callers or the plugins.

### L: Liskov substitution

The one principle here with formal roots. [Liskov and Wing (1994)](https://doi.org/10.1145/197320.197383) state the requirement: a property provable about objects of type T should hold for objects of a subtype S. Their position is that subtyping is a question of *behaviour*, and it's about specifications, not just method signatures. Martin [says the same](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html) and owns up to a past mistake: it's not about inheritance, "all duck-types are subtypes of an implied interface". That makes it the most useful of the five for Python, where nothing checks it.

```python
from typing import Protocol

class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        """One vector per text, in order. Never drops input."""
        ...

class RemoteEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t)), 1.0] for t in texts]

class DedupingEmbedder:
    """Passes a type checker. Breaks the promise: duplicates vanish."""
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t)), 1.0] for t in dict.fromkeys(texts)]

def index(chunks: list[str], embedder: Embedder) -> dict[str, list[float]]:
    return dict(zip(chunks, embedder.embed(chunks)))

def aligned(embedder: Embedder, chunks: list[str]) -> bool:
    return len(embedder.embed(chunks)) == len(chunks)

chunks = ["same", "same", "different one"]
print("remote aligned:", aligned(RemoteEmbedder(), chunks))
print("deduping aligned:", aligned(DedupingEmbedder(), chunks))
print(index(["a", "a", "bb"], DedupingEmbedder()))
```

```text
remote aligned: True
deduping aligned: False
{'a': [2.0, 1.0]}
```

The signature matches, so `mypy` passes it, and `zip` silently truncates so there's no exception either. The result: vectors silently attached to the wrong chunks. The fix in practice is a shared contract test run against every implementation, which [the testing chapter](05-testing-strategy.md) covers, plus `zip(..., strict=True)`.

### I: interface segregation

"Keep interfaces small so that users don't end up depending on things they don't need." [Martin's own reasoning](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html) leans on recompilation and redeployment, and he says dynamically typed languages are affected "much less". So Python mostly loses the original motive. What survives is that a function should ask for only what it uses, which makes it easier to test and to reuse. `typing.Protocol` lets the *caller* declare that need:

```python
from typing import Protocol

class HasTextAndId(Protocol):
    id: str
    text: str

class FullDocument:
    def __init__(self):
        self.id, self.text, self.owner, self.acl = "d1", "Refund policy", "ops", ["all"]
    def delete(self) -> None: raise RuntimeError("not from here")

class Stub:
    id, text = "t1", "short"

def to_context_line(doc: HasTextAndId) -> str:
    return f"[{doc.id}] {doc.text}"

print(to_context_line(FullDocument()))
print(to_context_line(Stub()))     # no delete, owner or acl needed
```

```text
[d1] Refund policy
[t1] short
```

### D: dependency inversion

Martin: "Depend in the direction of abstraction. High level modules should not depend upon low level details." The motive is sound: your evaluation logic shouldn't import a vendor SDK. In Python you rarely need a container or a framework for it. Pass the thing in:

```python
from typing import Callable

Complete = Callable[[str], str]

def grade_answer(question: str, answer: str, complete: Complete) -> bool:
    verdict = complete(f"Q: {question}\nA: {answer}\nReply PASS or FAIL.")
    return verdict.strip().upper().startswith("PASS")

# Production wires in the real client at the edge. A test passes a function.
print(grade_answer("2+2?", "4", complete=lambda prompt: " pass "))
print(grade_answer("2+2?", "5", complete=lambda prompt: "FAIL: wrong"))
```

```text
True
False
```

The cost is one more thing to read when you try to follow what actually runs, plus a wiring place. A single-implementation interface added for its own sake is the shallow case Ousterhout warns about. A function parameter has almost no such cost, which is why it's the default here.

### The arguments, side by side

| | What they object to | Fair reply |
|---|---|---|
| [North](https://dannorth.net/blog/cupid-for-joyful-coding/) | Principles as rules you pass or fail; offers properties to move towards: composable, Unix philosophy, predictable, idiomatic, domain-based | [Martin](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html): "The best way to make a complicated mess is to tell everyone to 'just be simple' and give them no further guidance" |
| [Ousterhout](https://github.com/johnousterhout/aposd-vs-clean-code) | Tiny single-purpose pieces become shallow and entangled | Martin concedes over-decomposition is possible and more balanced advice is needed; he still errs towards decomposing |
| [Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction), [Abramov](https://overreacted.io/goodbye-clean-code/) | Abstraction made too early is costlier than the duplication it removed | Beck's rule still holds for knowledge that is truly one fact |
| [Muratori](https://www.computerenhance.com/p/clean-code-horrible-performance) | Rules ignore runtime cost by large factors | Next section: much depends on language and where the time actually goes |

## What the indirection costs

[Muratori's essay](https://www.computerenhance.com/p/clean-code-horrible-performance) measures it in C++, on shapes with an area function: about 35 cycles per shape with virtual calls, 24 with a switch (1.5x) and 3.0 to 3.5 with a table (10x), growing to nearly 15x with one more property, and 20 to 25x with AVX. He says "none of these are hard-core measurements", because the differences are so large. He finds it unacceptable to give up that much hardware for a little programmer convenience. It's a measured argument, though his "rules" are taken from examples in the literature, and it's aimed at a certain segment of the industry, as he says himself.

So what happens to that gap in CPython?

```python
import time
from dataclasses import dataclass

class Square:
    __slots__ = ("side",)
    def __init__(self, side): self.side = side
    def area(self): return self.side * self.side

class Rectangle:
    __slots__ = ("width", "height")
    def __init__(self, width, height): self.width, self.height = width, height
    def area(self): return self.width * self.height

class Triangle:
    __slots__ = ("base", "height")
    def __init__(self, base, height): self.base, self.height = base, height
    def area(self): return 0.5 * self.base * self.height

class Circle:
    __slots__ = ("radius",)
    def __init__(self, radius): self.radius = radius
    def area(self): return 3.141592653589793 * self.radius * self.radius

N = 200_000
objects = [cls(*args) for cls, args in [(Square, (2.0,)), (Rectangle, (2.0, 3.0)), (Triangle, (2.0, 3.0)), (Circle, (2.0,))]] * (N // 4)

SQUARE, RECT, TRI, CIRCLE = 0, 1, 2, 3
tuples = [(SQUARE, 2.0, 2.0), (RECT, 2.0, 3.0), (TRI, 2.0, 3.0), (CIRCLE, 2.0, 2.0)] * (N // 4)
COEFF = (1.0, 1.0, 0.5, 3.141592653589793)

def virtual():
    return sum(shape.area() for shape in objects)

def branching():
    total = 0.0
    for kind, width, height in tuples:
        if kind == SQUARE or kind == RECT:
            total += width * height
        elif kind == TRI:
            total += 0.5 * width * height
        else:
            total += 3.141592653589793 * width * height
    return total

def table():
    total = 0.0
    for kind, width, height in tuples:
        total += COEFF[kind] * width * height
    return total

def best(fn, runs=7):
    result, times = None, []
    for _ in range(runs):
        start = time.perf_counter()
        result = fn()
        times.append(time.perf_counter() - start)
    return min(times) / N * 1e9, result

base = None
for fn in (virtual, branching, table):
    ns, result = best(fn)
    base = base or ns
    print(f"{fn.__name__:<10} {ns:6.1f} ns/shape   {base / ns:4.2f}x   total={result:.1f}")
```

```text
virtual      42.8 ns/shape   1.00x   total=1278318.5
branching    24.6 ns/shape   1.75x   total=1278318.5
table        22.9 ns/shape   1.87x   total=1278318.5
```

The direction is the same but the magnitude isn't anything like C++: in this run the table is roughly twice as fast as virtual dispatch, nowhere near 10x, because in an interpreter every path pays for bytecode dispatch and boxed floats. The real speedup is leaving the interpreter, and [NumPy-style vectorising](../../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md) over flat data sits in Muratori's camp: it requires knowing the data layout, not hiding it. That's Parnas's cost note from 1972 turning up again.

For an LLM system, where work is dominated by waiting for a model, a few hundred nanoseconds of dispatch won't show on any profile. For an inner loop over a hundred million rows, it may be your whole budget. So measure with [a profiler](06-debugging-and-profiling.md) and don't argue from either side's slogan. Muratori's fair point stands: cost is real and the people recommending an abstraction rarely quantify it.

## Essential and accidental complexity

[Brooks (1986)](https://doi.org/10.1109/MC.1987.1663532) separates the essential difficulty of a software task, fashioning its conceptual structures, from accidental difficulty in representing them. Unless accidental work is more than 9/10 of all effort, he argues, removing all of it won't give an order-of-magnitude improvement. [Moseley and Marks (2006)](https://curtclifton.net/papers/MoseleyMarks06a.pdf) take it further: complexity causes more problems in large systems than anything else, and it can be tamed only by avoiding it where possible and separating it where not; they propose splitting a system into essential state, essential logic and accidental state and control.

You won't adopt their full architecture, but a Python version of the idea is everywhere in this course: keep state in few places and logic in pure functions. The [lab](../practice/README.md)'s second call returning zero calls is a pure example of accidental state. Step 3 removes it with a small edit, and that fixes two of the three pinned bugs; the third, retried calls going uncounted, was a misplaced status check.

## Pitfalls

- **Principles as a review weapon.** Symptom: "this violates SRP" with no change scenario attached. Ask what change it will make harder.
- **Abstraction before the second use.** Symptom: a `BaseLLMClient` with one implementation and a config for vendors you don't use. Start with a function.
- **DRY on coincidence.** Symptom: a shared helper gains a mode flag per caller. Inline it back; [Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) has the steps.
- **Believing a type check proves substitution.** Symptom: every implementation type-checks, and one silently drops rows. Write contract tests.
- **Ignoring runtime cost,** or assuming it. Symptom: confident claims either way with no measurement.
- **Citing the slogan, not the author.** Symptom: "SRP means classes do one thing". Martin says that's not it. "SOLID is obsolete" is similarly not what North's article argues in detail, since he says it's a matter of trade-offs and context.
- **Using YAGNI to skip thinking about irreversible choices.** Symptom: a public API or persisted format chosen in five minutes. Keep the implementation small and spend the thinking on the contract.

## Try it

1. For the `VectorStore` above, write down what its interface still reveals that Parnas would say it needn't. Then change the storage to a `list[array.array]` without changing any caller.
2. Take `format_record` and give it a fourth caller who needs both redaction and tab-separated output. Do it first in the shared function, then with Metz's inline-back approach. Compare what a reader needs to know.
3. Run the timing block above, adding NumPy if you have it, and a fourth version that calls a `dict` of functions. Where does it land? Is the result stable across runs?
4. Pick the principle you trust most from this chapter and argue against it, using a real example from your work. Then pick the critic you agree with least and state their best case, so they'd accept your summary.

<details>
<summary>Answers</summary>

1. It reveals the dimension and that `nearest` returns exactly one id, and normalising is a hidden choice callers might depend on (scores are cosines). Changing the layout means only `add` and `score` change; `nearest`'s callers don't.
2. The shared version adds a third condition combination to test. Inlined, the new caller is three lines. The shared version's cost grows with every combination, and Metz's version repeats the replace call.
3. A dict of functions adds a lookup and a Python call per shape, so expect it to be near or slower than virtual dispatch. Timings vary by a few percent between runs, so take the best of several, and don't trust small differences.
4. Personal. A useful test: if your summary of the critic contains the word "just", it probably isn't their best case.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What is information hiding? | Parnas: each module hides a design decision from the others, with an interface revealing as little as possible. Don't decompose by flowchart step. |
| Coupling vs cohesion? | Cohesion: things in a module belong together, changing for the same reasons. Coupling: how much a change in one thing forces change in another. |
| What's a deep module? | Ousterhout: a simple interface over lots of functionality. Shallow ones add interface without hiding anything. |
| Is duplication always bad? | No. Duplicated knowledge is bad. Coincidental similarity is cheap, and "duplication is far cheaper than the wrong abstraction" (Metz). |
| What does YAGNI not cover? | Refactoring and malleability, and future-friendly choices that add no complexity. It's about presumptive features. |
| What are Beck's four rules? | Passes the tests, reveals intention, no duplication, fewest elements, in that order (Fowler's wording). |
| Explain SRP. | Martin: a module has one reason to change, meaning one group of people asking. It isn't "does one thing". North's critique: it can create artificial seams when content and format change together. |
| Explain LSP in Python terms. | A duck type or protocol implementation must keep the behaviour callers rely on, not only the signature. Liskov and Wing: provable properties of the supertype hold for the subtype. Type checkers can't verify it, so use contract tests. |
| Does ISP apply in Python? | Weakly: Martin says dynamic languages are less affected. It survives as "ask for only what you use", via `Protocol`. |
| How do you do dependency inversion in Python? | Pass a function or protocol object into high-level logic and wire the real one at the edge. No framework needed. |
| What's the best critique of SOLID? | Pick one and state it fairly: North on rules vs properties, Ousterhout on shallow pieces, Metz on premature abstraction, Muratori on measured runtime cost. Then give the reply. |
| Is polymorphism slow? | Muratori measured 1.5x to about 15x in C++. In CPython my run shows a much smaller gap, since the interpreter dominates. Measure in your own context. |
| Essential vs accidental complexity? | Brooks: inherent difficulty versus representation difficulty. Moseley and Marks: avoid or separate accidental state and control. |

## Next

[4 — Patterns worth knowing](04-patterns-worth-knowing.md): the handful of patterns that earn their keep in Python, and what the language does for you.
