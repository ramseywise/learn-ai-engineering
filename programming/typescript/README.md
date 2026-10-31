# TypeScript

> From "JavaScript for Python developers" to typed LLM apps, in nine modules. Each module is a
> short note plus exercises that are checked by the type checker, by `node --test`, or by both.
> Jump to: [Syllabus](#syllabus) · [Layout](#layout) · [Setup](#setup) · [How exercises are checked](#how-exercises-are-checked) · [Rules of thumb](#rules-of-thumb) · [Sources](#sources)

---

## Syllabus

| # | Note | You can… | Exercises |
|---|---|---|---|
| 01 | [JavaScript for Python developers](notes/01-js-for-python-devs.md) | Map Python idioms to JS and avoid `==`, `sort()` and truthiness traps | [01-js-basics](practice/exercises/01-js-basics.ts) |
| 02 | [Everyday types](notes/02-everyday-types.md) | Annotate boundaries, choose `interface` vs `type`, use `unknown` not `any` | [ts-ex 01](practice/typescript-exercises/01/index.ts) |
| 03 | [Unions and narrowing](notes/03-unions-and-narrowing.md) | Model discriminated unions with an exhaustive `switch`, write type predicates | [ts-ex 02](practice/typescript-exercises/02/index.ts) · [03](practice/typescript-exercises/03/index.ts) · [04](practice/typescript-exercises/04/index.ts) |
| 04 | [Generics](notes/04-generics.md) | Write constrained generics, `keyof`/`T[K]`, overloads | [ts-ex 06](practice/typescript-exercises/06/index.ts) · [07](practice/typescript-exercises/07/index.ts) · [09](practice/typescript-exercises/09/index.ts) · 12 easy challenges |
| 05 | [Building types from types](notes/05-type-transformations.md) | Use utility, mapped, conditional and template-literal types | [ts-ex 05](practice/typescript-exercises/05/index.ts) · [08](practice/typescript-exercises/08/index.ts) · [14](practice/typescript-exercises/14/index.ts) · [15](practice/typescript-exercises/15/index.ts) · 14 medium challenges |
| 06 | [Async](notes/06-async.md) | Run work in parallel vs sequentially, add timeouts, retries, concurrency limits | [06-async](practice/exercises/06-async.ts) · [ts-ex 10](practice/typescript-exercises/10/index.ts) |
| 07 | [Modules, `tsconfig` and tooling](notes/07-modules-and-tooling.md) | Set up ESM + strict config, write `.d.ts` files, augment modules | [ts-ex 11](practice/typescript-exercises/11/index.ts) · [12](practice/typescript-exercises/12/index.ts) · [13](practice/typescript-exercises/13/index.ts) |
| 08 | [Runtime validation with Zod](notes/08-runtime-validation-zod.md) | Parse env, JSON and LLM output into typed values at the boundary | [08-zod](practice/exercises/08-zod.ts) |
| 09 | [TypeScript for AI apps](notes/09-typescript-for-ai-apps.md) | Narrow content blocks, drive a tool loop from `stop_reason`, stream, get structured output | [09-ai-helpers](practice/exercises/09-ai-helpers.ts) · [live example](practice/examples/claude.ts) |

The type challenges are in [`practice/type-challenges/challenges/`](practice/type-challenges/challenges/).
Solutions sit next to each vendored exercise (`index.solution.ts`), in
[`practice/type-challenges/solutions/`](practice/type-challenges/solutions/) and in
[`practice/solutions/`](practice/solutions/). Try each exercise before you open them.

---

## Layout

```
typescript/
├── README.md
├── notes/                        01–09
└── practice/                     one npm project: package.json, tsconfig.json, .gitignore (node_modules/)
    ├── check.ts                  one tsc run with the errors grouped by exercise; --solutions swaps the solutions in
    ├── exercises/                own runtime exercises 01, 06, 08, 09
    ├── solutions/                same names, worked
    ├── tests/                    node --test, one file per runtime exercise
    ├── examples/claude.ts        live Anthropic SDK example
    ├── typescript-exercises/     vendored 01–15 (index.ts, index.solution.ts, test.ts), LICENSE, NOTICE.md
    └── type-challenges/          challenges/ vendored with its LICENSE; solutions/ written here
```

---

## Setup

```bash
cd programming/typescript/practice
npm install                 # TypeScript 7, zod, the Anthropic SDK, @types/node
npm run typecheck           # ok / FAIL for every type exercise (unsolved ones fail; that's expected)
node check.ts exercises/03/ # just one exercise; `node check.ts easy` for the easy challenges
npm test                    # runtime tests for 01, 06, 08, 09
npm run check               # swaps every solution in: must be 45/45 typecheck + all tests green
```

Node 22.18+ runs `.ts` files directly by stripping the types, so there is no build step. Only
`examples/claude.ts` needs `ANTHROPIC_API_KEY`. It exits cleanly without one.

---

## How exercises are checked

| Kind | Where | Passes when |
|---|---|---|
| Type exercises (vendored) | `typescript-exercises/NN/index.ts` (+ `test.ts`) | `tsc` reports no errors in that folder |
| Type challenges | `type-challenges/challenges/*.ts` | The `Expect<Equal<…>>` test cases at the bottom compile |
| Runtime exercises (own) | `exercises/*.ts` + `tests/*.test.ts` | `npm test` is green. The stubs throw `TODO` until you implement them |

`check.ts` runs one `tsc -p .` over the project and groups the errors by exercise. With
`--solutions` it copies the project to a temp dir and swaps every solution in first.

---

## Rules of thumb

- Types are erased. `as` checks nothing, so parse anything from outside the program with a schema.
- Annotate function signatures and exports. Let inference handle the rest.
- Use `unknown` instead of `any`, and narrow before you use it.
- Model "one of these" as a discriminated union and end the `switch` with a `never` check.
- Always `await` or return a promise. Use `Promise.all` for independent work and a limit for large fan-outs.
- Turn on `strict` from day one. Turning it on later is painful.

---

## Sources

| Source | License | Used for |
|---|---|---|
| [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) | CC-BY 4.0 | Structure and content of notes 02–05 and 07 (paraphrased) |
| [typescript-exercises](https://github.com/typescript-exercises/typescript-exercises) (Marat Dulin) | MIT | 15 vendored exercises with solutions. TS 7 patches are in [`NOTICE.md`](practice/typescript-exercises/NOTICE.md) |
| [type-challenges](https://github.com/type-challenges/type-challenges) (Anthony Fu) | MIT | 26 easy and medium challenges with test cases. The solutions are written for this repo |
| [Zod](https://zod.dev) | MIT | Note 08 |
| [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript) | MIT | Note 09 and the live example |
| [Total TypeScript](https://www.totaltypescript.com/) (Matt Pocock), [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/) (Basarat) | Proprietary / read online | Further reading, link only |

Timed and interview-style problems in TypeScript are in [sisyphus `drills/`](https://github.com/ramseywise/sisyphus/blob/main/drills/README.md).
