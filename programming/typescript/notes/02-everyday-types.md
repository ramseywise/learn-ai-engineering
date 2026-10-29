---
origin: curated
sources:
  - "TypeScript Handbook — https://www.typescriptlang.org/docs/handbook/ (CC-BY 4.0; paraphrased, not copied)"
  - "typescript-exercises by Marat Dulin — https://github.com/typescript-exercises/typescript-exercises (MIT; vendored in practice/)"
concepts: [ts-primitives, ts-interfaces, ts-type-aliases, ts-arrays-tuples, ts-inference, ts-any-unknown]
cleaned: 2026-10-29
---
# 2 — Everyday Types

> Annotate the boundaries (function parameters, return types, exported data) and let inference handle everything inside.

---

## The basics

```ts
let id: number = 1;          // usually leave it out: `let id = 1` infers number
const name = 'Ada';          // const infers the literal type 'Ada'
let tags: string[] = [];     // also written Array<string>
let pair: [string, number] = ['a', 1];   // tuple: a fixed length, with a type per position
```

| Type | Meaning |
|---|---|
| `string`, `number`, `boolean`, `bigint`, `symbol` | Primitives (always lowercase. `String` is the wrapper object) |
| `null`, `undefined` | Separate types under `strict`. A `string` can't be `null` unless you write `string \| null` |
| `unknown` | "Could be anything. You must narrow before using it." The safe top type |
| `any` | "Turn the checker off." It spreads to everything it touches. Avoid it |
| `never` | A value that can't exist: the return type of a function that always throws, or an exhausted union |
| `void` | A function that returns nothing useful |

## Object shapes: `interface` vs `type`

```ts
interface User {
  id: number;
  name: string;
  email?: string;                // optional: string | undefined
  readonly createdAt: Date;      // can't be reassigned after creation
}

type Point = { x: number; y: number };
type ID = number | string;       // only `type` can name unions, tuples and primitives
```

Use `interface` for object shapes, especially ones you'll extend (`interface Admin extends User`). Use `type` for everything else. Both are erased at runtime.

**Structural typing.** TS checks *shape*, not name. Any object with `x: number` and `y: number` *is* a `Point`, much like a Python `Protocol`. As one exception, an object **literal** with extra properties is an error ("excess property check"), because that is usually a typo.

## Functions

```ts
function greet(name: string, greeting = 'Hello'): string {
  return `${greeting}, ${name}`;
}
const add = (a: number, b: number): number => a + b;
function log(...parts: unknown[]): void { console.log(...parts); }
type Handler = (event: string) => void;   // a function type
```

Annotate return types on exported functions. A function's signature is its contract, and the annotation catches accidental changes.

## Literal types and `as const`

```ts
let dir: 'up' | 'down' = 'up';
const config = { mode: 'dev', port: 3000 } as const;   // readonly { mode: 'dev'; port: 3000 }
```

## `strict` mode

Always turn on `"strict": true`. It enables `strictNullChecks` (the big one), `noImplicitAny` and stricter function checks. Without it, TS lets `null` flow anywhere and catches far less. Consider also enabling `noUncheckedIndexedAccess`, which makes `xs[i]` have type `T | undefined`.

---

## Exercises

[`practice/typescript-exercises/01`](../practice/typescript-exercises/01/index.ts): define `User` from the data. From `practice/`, check with `node check.ts exercises/01/`.
