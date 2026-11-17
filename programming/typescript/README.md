# TypeScript

Go from "JavaScript for Python developers" to typed LLM applications. Three steps and nine short notes, each with exercises that are checked by the type checker, by `node --test`, or by both.

**What you should already know.** [Python 03 Language for engineers](../python/README.md): TypeScript starts after it, so types and asynchronous work already have context. The [async](notes/06-async.md) note compares promises with the asyncio model from [Python 03 · 07 concurrency](../python/03-language-for-engineers/notes/07-concurrency.md).

## Lecture

Start with the overview deck, [TypeScript](slides/typescript.pptx) ([PDF](slides/typescript.pdf)), on the same examples as the notes. Librarian turns each slide into a flashcard: the title is the question and the takeaway is the rule that answers it.

## The core

TypeScript's types exist only while the code is being checked. They are erased before the program runs, so a type is a claim about a value and not a check on it. The question this track keeps asking is: **what does the type checker know here, and what does the running program actually have?** Inside your own code the two agree if you let the checker do its work. At every boundary (JSON, environment variables, a model's output) they agree only if you parse.

There are three steps: JavaScript itself and the types you write every day, then types computed from other types, then the places where a program meets the outside world. The notes are written for someone who knows Python and name the Python equivalent wherever there is one.

## Syllabus

One row per step. **Core concepts** are the ideas the step turns on, **Study** is what to read, **Labs** is what to do afterwards (the track's own exercises first, then the drills on the same topic), and **Sources** is where to read more. How to run the labs and how each kind is checked: [practice/README.md](practice/README.md).

| Submodule | Core concepts | Study | Labs | Sources |
|---|---|---|---|---|
| **1. JavaScript and core types:** the language you already half know | JavaScript is not Python with braces: `===` always, `sort()` compares strings by default, and truthiness differs. Annotate signatures and exports, and let inference do the rest. `unknown` instead of `any`. "One of these" is a discriminated union whose `switch` ends in a `never` check. | [1 JavaScript for Python developers](notes/01-js-for-python-devs.md) · [2 Everyday types](notes/02-everyday-types.md) · [3 Unions and narrowing](notes/03-unions-and-narrowing.md) | [01-js-basics](practice/exercises/01-js-basics.ts) · ts-ex [01](practice/typescript-exercises/01/index.ts) · [02](practice/typescript-exercises/02/index.ts) · [03](practice/typescript-exercises/03/index.ts) · [04](practice/typescript-exercises/04/index.ts) | [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) · [typescript-exercises](https://github.com/typescript-exercises/typescript-exercises) |
| **2. Type-level design:** types computed from types | A generic is a function over types, and a constraint says what it may assume. `keyof` and `T[K]` tie a key to its value's type. Utility, mapped and conditional types derive one type from another, so a change in the source type reaches every use. | [4 Generics](notes/04-generics.md) · [5 Building types from types](notes/05-type-transformations.md) | ts-ex [06](practice/typescript-exercises/06/index.ts) · [07](practice/typescript-exercises/07/index.ts) · [09](practice/typescript-exercises/09/index.ts) · [05](practice/typescript-exercises/05/index.ts) · [08](practice/typescript-exercises/08/index.ts) · stretch: [14](practice/typescript-exercises/14/index.ts) · [15](practice/typescript-exercises/15/index.ts) · [type challenges](practice/type-challenges/challenges/), 12 easy and 14 medium · drill: [a typed `groupBy`](../drills/typescript/types/group-by.md) | [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) · [type-challenges](https://github.com/type-challenges/type-challenges) · [Total TypeScript](https://www.totaltypescript.com/): further reading |
| **3. Production boundaries:** async, modules and the outside world | Always `await` or return a promise. `Promise.all` is for independent work, and a large fan-out needs a limit. `strict` is on from day one. Types are erased and `as` checks nothing, so parse anything from outside with a schema. A tool loop is driven by `stop_reason`. | [6 Async](notes/06-async.md) · [7 Modules, `tsconfig` and tooling](notes/07-modules-and-tooling.md) · [8 Runtime validation with Zod](notes/08-runtime-validation-zod.md) · [9 TypeScript for AI apps](notes/09-typescript-for-ai-apps.md) | [06-async](practice/exercises/06-async.ts) · ts-ex [10](practice/typescript-exercises/10/index.ts) · [11](practice/typescript-exercises/11/index.ts) · [12](practice/typescript-exercises/12/index.ts) · [13](practice/typescript-exercises/13/index.ts) · [08-zod](practice/exercises/08-zod.ts) · [09-ai-helpers](practice/exercises/09-ai-helpers.ts) · [live example](practice/examples/claude.ts) · drill: [ESLint](../drills/typescript/eslint.md) | [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) · [Zod](https://zod.dev) · [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript) |

Solutions sit next to each vendored exercise (`index.solution.ts`), in [`practice/type-challenges/solutions/`](practice/type-challenges/solutions/) and in [`practice/solutions/`](practice/solutions/). Try each exercise before you open them. Timed problems in TypeScript are in [`programming/drills/`](../drills/README.md).

## Rules of thumb

- Types are erased. `as` checks nothing, so parse anything from outside the program with a schema.
- Annotate function signatures and exports. Let inference handle the rest.
- Use `unknown` instead of `any`, and narrow before you use it.
- Model "one of these" as a discriminated union and end the `switch` with a `never` check.
- Always `await` or return a promise. Use `Promise.all` for independent work and a limit for large fan-outs.
- Turn on `strict` from day one. Turning it on later is painful.

## Builds on and feeds into

**Builds on**

| Chapter | Why |
|---|---|
| [Python 03 Language for engineers](../python/README.md) | TypeScript starts after it; types and asynchronous work have context by then |
| [Python 03/07 Concurrency](../python/03-language-for-engineers/notes/07-concurrency.md) | The asyncio model that [async](notes/06-async.md) compares with promises |

**Feeds into**

| Chapter | Why |
|---|---|
| [Frontend and UX](../frontend-and-ux/README.md) | Starts after this track; React and AI interfaces use its async and streaming |
| [DA 05/06 Dashboard stacks](../../data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend.md) | The TypeScript end of a dashboard stack |
| [AI Engineering](../../ai-engineering/README.md) | Labs come in TypeScript and Python side by side |

## Primary texts

- TypeScript Handbook
- *typescript-exercises*
- *type-challenges*
- Zod documentation

Licences and what each source was used for:

| Source | License | Used for |
|---|---|---|
| [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) | CC-BY 4.0 | Structure and content of notes 02–05 and 07 (paraphrased) |
| [typescript-exercises](https://github.com/typescript-exercises/typescript-exercises) (Marat Dulin) | MIT | 15 vendored exercises with solutions. TS 7 patches are in [`NOTICE.md`](practice/typescript-exercises/NOTICE.md) |
| [type-challenges](https://github.com/type-challenges/type-challenges) (Anthony Fu) | MIT | 26 easy and medium challenges with test cases. The solutions are written for this repo |
| [Zod](https://zod.dev) | MIT | Note 08 |
| [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript) | MIT | Note 09 and the live example |
| [Total TypeScript](https://www.totaltypescript.com/) (Matt Pocock), [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/) (Basarat) | Proprietary / read online | Further reading, link only |

Everything else: [references.md](../references.md). The deck is built from [`slides/deck.yaml`](slides/deck.yaml) with `make slides PILLAR=programming/typescript`.

## Next

Start with step 1, **JavaScript and core types**: read [1 JavaScript for Python developers](notes/01-js-for-python-devs.md), then do its exercise from the syllabus row.

After step 3 you can write a typed program that stays correct at its edges. Putting one in front of a person is the next track, [frontend and UX](../frontend-and-ux/README.md).
