---
origin: curated
sources:
  - "TypeScript Handbook, Generics — https://www.typescriptlang.org/docs/handbook/2/generics.html (CC-BY 4.0; paraphrased)"
  - "typescript-exercises — https://github.com/typescript-exercises/typescript-exercises (MIT; vendored in practice/)"
  - "type-challenges by Anthony Fu — https://github.com/type-challenges/type-challenges (MIT; vendored in practice/)"
concepts: [ts-generics, ts-constraints, ts-keyof, ts-indexed-access, ts-overloads]
cleaned: 2026-10-29
---
# 4 — Generics

> A generic is a type parameter. It lets one function work for many types *without forgetting which type it was given*.

---

## Why

```ts
function first(xs: any[]): any { return xs[0]; }          // the type is lost
function first<T>(xs: T[]): T | undefined { return xs[0]; } // first([1, 2]) has type number | undefined
```

`T` is inferred from the arguments, so you rarely write `first<number>(…)`. It is Python's `TypeVar`: `def first(xs: list[T]) -> T` (or `first[T]` with 3.12 syntax).

## Constraints

```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
longest('ab', 'abc');       // OK: string has length
longest(10, 20);            // error: number has no length
```

`extends` here means "must be assignable to". It sets a lower bound on what callers may pass.

## `keyof` and indexed access

```ts
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
const user = { id: 1, name: 'Ada' };
get(user, 'name');   // string
get(user, 'nope');   // error: not a key of the object
```

| Syntax | Meaning |
|---|---|
| `keyof T` | Union of `T`'s keys: `'id' \| 'name'` |
| `T[K]` | The type of property `K` on `T` |
| `T[number]` | The element type of an array or tuple type |
| `typeof value` | The type of a *value* (in a type position) |

## Generic types

```ts
interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  error?: string;
}
type Pair<A, B = A> = [A, B];   // with a default
```

Better still, combine generics with a discriminated union so that `data` is present exactly when `status === 'success'`:

```ts
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
```

## Overloads

When the return type depends on an argument *value*, a single generic signature is not enough. Overloads list the call shapes:

```ts
function filterPersons(people: Person[], kind: 'user', criteria: Partial<User>): User[];
function filterPersons(people: Person[], kind: 'admin', criteria: Partial<Admin>): Admin[];
function filterPersons(people: Person[], kind: string, criteria: Partial<Person>): Person[] {
  /* implementation signature: callers never see it */
}
```

## Rules of thumb

- A type parameter should appear **at least twice**, for example linking an input to an output. If `T` is used only once, write the concrete type, or `unknown`, instead.
- Prefer letting `T` be inferred over making callers write it.
- Constrain as loosely as the body allows.

---

## Exercises

- [`practice/typescript-exercises/06`](../practice/typescript-exercises/06/index.ts) (overloads and generics), [`07`](../practice/typescript-exercises/07/index.ts) (a generic `swap`) and [`09`](../practice/typescript-exercises/09/index.ts) (a generic `ApiResponse`)
- **Easy** type challenges in [`practice/type-challenges/challenges/`](../practice/type-challenges/challenges/): `*-easy-*.ts` (Pick, Readonly, First, Length, Exclude, Awaited, If, Concat, Includes, Push, Parameters). From `practice/`, check with `node check.ts easy`.
