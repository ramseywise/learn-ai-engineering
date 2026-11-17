# Running the TypeScript exercises

How the track's exercises are laid out, run and checked. What to do after which note is in the [syllabus](../README.md#syllabus).

## Layout

```
typescript/
├── README.md
├── notes/                        01–09
├── slides/                       deck.yaml and the built study deck; `make slides PILLAR=programming/typescript`
└── practice/                     one npm project: package.json, tsconfig.json, .gitignore (node_modules/)
    ├── check.ts                  one tsc run with the errors grouped by exercise; --solutions swaps the solutions in
    ├── exercises/                own runtime exercises 01, 06, 08, 09
    ├── solutions/                same names, worked
    ├── tests/                    node --test, one file per runtime exercise
    ├── examples/claude.ts        live Anthropic SDK example
    ├── typescript-exercises/     vendored 01–15 (index.ts, index.solution.ts, test.ts), LICENSE, NOTICE.md
    └── type-challenges/          challenges/ vendored with its LICENSE; solutions/ written here
```

## Run it

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

## How exercises are checked

| Kind | Where | Passes when |
|---|---|---|
| Type exercises (vendored) | `typescript-exercises/NN/index.ts` (+ `test.ts`) | `tsc` reports no errors in that folder |
| Type challenges | `type-challenges/challenges/*.ts` | The `Expect<Equal<…>>` test cases at the bottom compile |
| Runtime exercises (own) | `exercises/*.ts` + `tests/*.test.ts` | `npm test` is green. The stubs throw `TODO` until you implement them |

`check.ts` runs one `tsc -p .` over the project and groups the errors by exercise. With
`--solutions` it copies the project to a temp dir and swaps every solution in first.

## Drills

Timed and interview-style problems in TypeScript are in [`programming/drills/`](../../drills/README.md): the [typed `groupBy`](../../drills/typescript/types/group-by.md) drill goes with step 2 of the syllabus and the [ESLint](../../drills/typescript/eslint.md) drill with step 3.
