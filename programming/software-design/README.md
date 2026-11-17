# Software design

How to keep code cheap to change: reading it, refactoring it, testing it, debugging it, and working on it with other people. Three steps and seven chapters. The rest of the course teaches you to build systems; this track is about still being able to change them a year later.

**What you should already know.** [Python 03 Language for engineers](../python/README.md): the examples are Python, and the track leans on [generators](../python/03-language-for-engineers/notes/02-generators-and-iteration.md), [objects and the MRO](../python/03-language-for-engineers/notes/08-objects-inheritance-and-mro.md) and [memory and the runtime](../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md). Git on your machine for step 3.

## Lecture

Start with the overview deck, [Software design](slides/software-design.pptx) ([PDF](slides/software-design.pdf)), on the same examples as the notes. Librarian turns each slide into a flashcard: the title is the question and the takeaway is the rule that answers it.

## The core

Most of the cost of software comes after the first version: every later change has to understand what's there, alter it without breaking the rest, and show that it worked. Design is the set of decisions that makes those steps cheaper or more expensive. So the track keeps asking three questions of any piece of code: **what will have to change, what must a person hold in their head to change it, and how would you know if the change broke something?**

There are three steps, one per question in practice. Readable code and sound design answer the first two, tests and debugging tools answer the third, and the team practices in the last step keep the answers from getting lost. The track treats design as a matter of trade-offs and evidence, not rules. Each abstraction comes with what it costs, and the arguments against popular advice, SOLID included, get a fair hearing.

It inherits the weakness of its field: there's little strong evidence for most design advice, a lot of it is expert opinion from one kind of system, and the empirical studies cited here are small or narrow. When a chapter's claim is one person's judgement or a single worked example, it says so.

## Syllabus

One row per step. **Core concepts** are the ideas the step turns on, **Study** is what to read, **Labs** is what to do afterwards (the track's own lab first, then the drills on the same topic), and **Sources** is where to read more. How to run the lab: [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. Writing code that can change:** reading, refactoring and design | A smell is a reason to look, not a verdict. Pin behaviour before you change structure, and never do both in one step. Hide what is likely to change behind a deep module. Duplication is cheaper than the wrong abstraction, and a table or a function beats a class hierarchy until a second behaviour exists. | [1 Readable code and code smells](notes/01-readable-code-and-smells.md) · [2 Refactoring](notes/02-refactoring.md) · [3 Design principles and their critics](notes/03-design-principles.md) · [4 Patterns worth knowing](notes/04-patterns-worth-knowing.md) | [Lab](practice/README.md), steps 1 to 4, after chapter 2: take a smelly module through refactoring under tests · drills: [seeded-bug problems](../drills/coding/problems/README.md) · [object-oriented design](../drills/coding/dsa/object_oriented_design/Readme.md) | Ousterhout and Martin, [*A Philosophy of Software Design* vs *Clean Code*](https://github.com/johnousterhout/aposd-vs-clean-code) · Fowler, [bliki and articles](https://martinfowler.com/) · Rhodes, [Python Design Patterns](https://python-patterns.guide/) · Parnas 1972 and the empirical studies: [references.md](references.md) |
| **2. Knowing that it works:** tests and debugging | Test behaviour through public interfaces, and reach for a real object or a fake before a mock. Coverage tells you what ran; only a failing test tells you what is checked. Write your prediction down before you run the experiment, and profile before you optimise. | [5 Testing strategy](notes/05-testing-strategy.md) · [6 Debugging and profiling](notes/06-debugging-and-profiling.md) | [Lab](practice/README.md), step 5, after chapter 5: mutation-test your own tests · drill: [seeded-bug problems](../drills/coding/problems/README.md), found by hypothesis rather than by reading | [*Software Engineering at Google*](https://abseil.io/resources/swe-book), ch. 11 to 14 · Fowler on the test pyramid and test doubles, [martinfowler.com](https://martinfowler.com/) · the SRE book on testing and Gregg on flame graphs: [references.md](references.md) |
| **3. Working with other people:** Git, review and design docs | Git is a graph of immutable objects, and the reflog remembers what you think you lost. Keep a change small enough to review and each commit good enough to bisect. Write a design doc when the answer is ambiguous, and an ADR when someone will later ask why. | [7 Git, code review and design docs](notes/07-git-code-review-and-design-docs.md) | The chapter's own blocks, which build throwaway repositories · drill: [Git](../drills/tooling/git.md) | Chacon and Straub, [*Pro Git*](https://git-scm.com/book/en/v2) · Google, [Engineering Practices: code review](https://google.github.io/eng-practices/review/) · [*Software Engineering at Google*](https://abseil.io/resources/swe-book), ch. 9 |

The notes follow the [full chapter standard](https://github.com/ramseywise/librarian/blob/main/.claude/skills/pillar/references/pillar-layout.md), not the shorter format of the Python modules. Every source and the chapter it maps to: [references.md](references.md).

## Rules of thumb

- Refactor when you're about to change the code, not on a schedule. Otherwise you're guessing what future change to make cheap.
- Pin behaviour before you change structure, and never do both in one step.
- A smell is a reason to look, and a complexity score is a reason to read. Neither one is a verdict.
- Duplication is cheaper than the wrong abstraction. Wait for the second real use.
- Prefer a table or a function to a class hierarchy until a second behaviour exists.
- Test behaviour through public interfaces. Reach for a real object or a fake before a mock.
- Coverage tells you what ran. Only a failing test tells you what's checked.
- Write your prediction down before you run the experiment. Profile before you optimise.
- Keep a change small enough to review and each commit good enough to bisect.
- Write a design doc when the answer is ambiguous, and an ADR when someone will later ask why.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Python 03: Objects, inheritance and the MRO](../python/03-language-for-engineers/notes/08-objects-inheritance-and-mro.md) | Inheritance, composition and `__getattr__`, which chapters 3 and 4 weigh up |
| [Python 03: Generators and iteration](../python/03-language-for-engineers/notes/02-generators-and-iteration.md) | The pipeline pattern in chapter 4 |
| [Python 03: Memory and the runtime](../python/03-language-for-engineers/notes/09-memory-and-the-runtime.md) | Allocation and `tracemalloc`, used in chapter 6 |

**Feeds into**

| Chapter | Why |
|---|---|
| [Backend and system design](../backend-and-system-design/README.md) | Its lab is tested the way chapter 5 describes, and its debugging section starts from chapter 6 |
| [Frontend: the lab](../frontend-and-ux/practice/README.md) | Its planted faults are chapter 5's mutation testing done by hand |
| [Evals in CI](../../generative-ai/08-eval/notes/10-evals-in-ci.md) | Evals take over where chapter 5's deterministic tests stop |
| [Tracing and observability](../../generative-ai/08-eval/notes/08-tracing-and-observability.md) | Traces are the production evidence chapter 6's method starts from |
| [Durable execution and interrupts](../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md) | Keeping state explicit, from chapters 3 and 4, on a real agent runtime |

## Primary texts

- Google, [*Software Engineering at Google*](https://abseil.io/resources/swe-book), free online edition: chapters 9 and 11 to 14
- Google, [Engineering Practices: code review](https://google.github.io/eng-practices/review/)
- Martin Fowler, [bliki and articles](https://martinfowler.com/) on refactoring and testing
- Ousterhout and Martin, [*A Philosophy of Software Design* vs *Clean Code*](https://github.com/johnousterhout/aposd-vs-clean-code), a debate
- Brandon Rhodes, [Python Design Patterns](https://python-patterns.guide/)
- Chacon and Straub, [*Pro Git*](https://git-scm.com/book/en/v2), and the [Python 3.14 documentation](https://docs.python.org/3.14/)

The well-known books behind some of these (Fowler's *Refactoring*, Ousterhout's *A Philosophy of Software Design*, the Gang of Four's *Design Patterns*) were not accessed for this track, and no claim here rests on their contents. Everything else: [references.md](references.md). The deck is built from [`slides/deck.yaml`](slides/deck.yaml) with `make slides PILLAR=programming/software-design`.

## Next

Start with step 1, **Writing code that can change**: read [1 Readable code and code smells](notes/01-readable-code-and-smells.md), and start the lab once you have read chapter 2.

After step 3 you can change code you did not write and show that the change is safe. What the code does once it has real users is [backend and system design](../backend-and-system-design/README.md).
