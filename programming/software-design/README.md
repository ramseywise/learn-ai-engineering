# Software design

> How to keep code cheap to change: reading it, refactoring it, testing it, debugging it, and working on it with other people. The rest of the course teaches you to build systems; this track is about still being able to change them a year later.
> Jump to: [Reading order](#reading-order) · [Builds on and feeds into](#builds-on-and-feeds-into) · [Rules of thumb](#rules-of-thumb) · [Layout](#layout) · [Setup](#setup) · [Primary texts](#primary-texts)

---

## What this is

Most of the cost of software comes after the first version: every later change has to understand what's there, alter it without breaking the rest, and show that it worked. Design is the set of decisions that makes those steps cheaper or more expensive. This track treats it as a matter of trade-offs and evidence, not rules. Each abstraction here comes with what it costs, and the arguments against popular advice, SOLID included, get a fair hearing.

It sits between the [Python track](../python/README.md), which teaches the language, and the systems in the data and AI subjects, which are where this code gets written. It inherits the weakness of its field: there's little strong evidence for most design advice, a lot of it is expert opinion from one kind of system, and the empirical studies cited here are small or narrow. When a chapter's claim is one person's judgement or a single worked example, it says so.

The mental model has three questions. What will have to change? What must a person hold in their head to change it? How would you know if the change broke something? Readable code and sound design answer the first two, tests and debugging tools the third, and the team practices in chapter 7 keep the answers from getting lost.

## Reading order

The notes follow the [full chapter standard](../../.claude/skills/pillar/references/pillar-layout.md), not the shorter format of the Python modules.

**Writing code that can change**

| # | Note | You can… |
|---|---|---|
| 01 | [Readable code and code smells](notes/01-readable-code-and-smells.md) | Name what's wrong with a function, and read complexity numbers without worshipping them |
| 02 | [Refactoring](notes/02-refactoring.md) | Pin behaviour with characterization tests, change structure in small safe moves, migrate an interface others use |
| 03 | [Design principles and their critics](notes/03-design-principles.md) | Apply information hiding and deep modules, and argue both sides of SOLID, DRY and clean code |
| 04 | [Patterns worth knowing](notes/04-patterns-worth-knowing.md) | Use the patterns Python still needs, skip those it makes unnecessary, and price the indirection |

**Knowing that it works**

| # | Note | You can… |
|---|---|---|
| 05 | [Testing strategy](notes/05-testing-strategy.md) | Choose test sizes and doubles, write contract and property tests, and tell coverage from mutation score |
| 06 | [Debugging and profiling](notes/06-debugging-and-profiling.md) | Debug by hypothesis, use `pdb` post-mortem, read `cProfile` and flame graphs, and diagnose a hung process |

**Working with other people**

| # | Note | You can… |
|---|---|---|
| 07 | [Git, code review and design docs](notes/07-git-code-review-and-design-docs.md) | Reason from Git's object model, recover with the reflog, bisect a regression, review for design, and write a design doc or ADR when it's worth it |

**Lab:** [take a smelly module through refactoring under tests](practice/README.md). Do it after chapter 2, and come back after chapter 5 for the mutation test.

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
| [Evals in CI](../../generative-ai/08-eval/notes/10-evals-in-ci.md) | Evals take over where chapter 5's deterministic tests stop |
| [Tracing and observability](../../generative-ai/08-eval/notes/08-tracing-and-observability.md) | Traces are the production evidence chapter 6's method starts from |
| [Durable execution and interrupts](../../ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts.md) | Keeping state explicit, from chapters 3 and 4, on a real agent runtime |

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

## Layout

```
software-design/
├── README.md
├── references.md
├── notes/                         01–07
└── practice/
    ├── README.md                  the lab: what to do and what it measured
    ├── check.sh                   runs the lab's tests (solutions by default)
    ├── mutate.py                  a tiny mutation tester, used from chapter 5
    ├── exercises/usage_report_lab/   the module and its characterization tests
    └── solutions/usage_report_lab/   every refactoring step, and tests over all of them
```

## Setup

You need Python 3.14 and [uv](https://docs.astral.sh/uv/) for the lab, and Git for chapter 7. The notes' code blocks are standalone: copy one into a file and run it. Chapter 5's use Hypothesis and coverage, so run those with `uv run --with hypothesis --with coverage python block.py`. Everything in this track was run on Python 3.14.7 and Git 2.55.0.

Chapter 7's blocks create throwaway Git repositories under a temporary directory. Don't change them to point at a real one.

## Primary texts

- Google, [*Software Engineering at Google*](https://abseil.io/resources/swe-book), free online edition: chapters 9 and 11 to 14
- Google, [Engineering Practices: code review](https://google.github.io/eng-practices/review/)
- Martin Fowler, [bliki and articles](https://martinfowler.com/) on refactoring and testing
- Ousterhout and Martin, [*A Philosophy of Software Design* vs *Clean Code*](https://github.com/johnousterhout/aposd-vs-clean-code), a debate
- Brandon Rhodes, [Python Design Patterns](https://python-patterns.guide/)
- Chacon and Straub, [*Pro Git*](https://git-scm.com/book/en/v2), and the [Python 3.14 documentation](https://docs.python.org/3.14/)

The well-known books behind some of these (Fowler's *Refactoring*, Ousterhout's *A Philosophy of Software Design*, the Gang of Four's *Design Patterns*) were not accessed for this track, and no claim here rests on their contents. Everything else: [references.md](references.md).
