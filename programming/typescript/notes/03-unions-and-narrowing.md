---
origin: curated
sources:
  - "TypeScript Handbook, Narrowing — https://www.typescriptlang.org/docs/handbook/2/narrowing.html (CC-BY 4.0; paraphrased)"
  - "typescript-exercises — https://github.com/typescript-exercises/typescript-exercises (MIT; vendored in practice/)"
concepts: [ts-unions, ts-narrowing, ts-discriminated-unions, ts-type-predicates, ts-exhaustiveness]
cleaned: 2026-11-01
---
# 3 — Unions and Narrowing

> A union says "one of these". Narrowing is how you find out which one. Discriminated unions with an exhaustive `switch` are TypeScript's most useful pattern.

---

## Unions

```ts
type ID = number | string;

function show(id: ID): string {
  return id.toUpperCase();   // error: toUpperCase doesn't exist on number
}
```

On a union you can use only what **every** member has. To use more, narrow it first.

## Narrowing

The checker follows your control flow and narrows the type inside each branch:

| Check | Narrows | Example |
|---|---|---|
| `typeof x === 'string'` | Primitives | `if (typeof id === 'string') id.toUpperCase()` |
| `x instanceof Date` | Class instances | `catch (e) { if (e instanceof Error) e.message }` |
| `'role' in x` | Object shapes, by property | `if ('role' in person) person.role` |
| `x === null`, `x == null`, `if (x)` | Nullability | `if (!user) return;` then `user` is non-null |
| `x.kind === 'circle'` | Discriminated unions | see below |
| `Array.isArray(x)` | Arrays | |

Follow one value through a function. Each branch removes members of the union, so what is left at the bottom is the only type it can be:

```ts
function label(x: string | number | null): string {
  if (x === null) return 'none';                     // x: null
  if (typeof x === 'string') return x.toUpperCase(); // x: string
  return x.toFixed(2);                               // x: number
}

console.log(label(null), label('ada'), label(3));    // none ADA 3.00
```

```mermaid
flowchart TD
    A["x: string | number | null"] --> B{"x === null?"}
    B -- yes --> C["x: null, return 'none'"]
    B -- no --> D["x: string | number"]
    D --> E{"typeof x === 'string'?"}
    E -- yes --> F["x: string, safe to call toUpperCase"]
    E -- no --> G["x: number, safe to call toFixed"]
```

Narrowing also happens after an early `return` or `throw`. Guard clauses at the top of a function are the idiomatic way to do it.

## Discriminated unions

Give each member a literal `type` (or `kind`) field. Checking that field narrows to the matching member:

```ts
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rect'; width: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case 'circle':
      return Math.PI * s.radius ** 2;       // s is the circle member here
    case 'rect':
      return s.width * s.height;
    default: {
      const unreachable: never = s;          // compile error if you add a member and forget a case
      throw new Error(`unhandled: ${JSON.stringify(unreachable)}`);
    }
  }
}
```

This is how you model API responses (`{ ok: true; data } | { ok: false; error }`), Redux-style actions and LLM content blocks (`block.type === 'text'`, [note 09](09-typescript-for-ai-apps.md)). In Python you would get the same effect with a `Literal` field and `match`, though nothing there enforces it.

## Type predicates

The snippets below use these types:

```ts
interface User { type: 'user'; name: string; occupation: string }
interface Admin { type: 'admin'; name: string; role: string }
type Person = User | Admin;
declare const people: Person[];
```

Write a function that returns `x is T` to package a check so you can reuse it:

```ts
function isAdmin(p: Person): p is Admin {
  return p.type === 'admin';
}
const admins = people.filter(isAdmin);    // Admin[], not Person[]
```

The predicate is a promise *you* make, and the checker trusts it without verifying. Since TS 5.5, simple arrow functions like `(p) => p.type === 'admin'` are inferred as predicates automatically. That is why vendored exercise 04 already passes on TS 7 (see `practice/typescript-exercises/NOTICE.md`). For that exercise, write the `person is Admin` and `person is User` annotations by hand on `isAdmin` and `isUser`, so you practise the syntax.

## `unknown` at the boundaries

```ts
function parse(json: string): unknown {
  return JSON.parse(json);
}
const v = parse(input);
if (typeof v === 'object' && v !== null && 'name' in v && typeof v.name === 'string') {
  v.name;   // string
}
```

Narrowing `unknown` by hand gets painful quickly. That is the job of a schema library ([note 08](08-runtime-validation-zod.md)).

## Pitfalls

- **Calling a member-only method on a union.** `id.toUpperCase()` on `number | string` is a compile error. Narrow first.
- **Leaving out the `never` branch.** When you add a member, a `switch` in a function that returns nothing skips it silently. `const unreachable: never = s` turns that into a compile error.
- **Writing a wrong type predicate.** The checker trusts `x is T` without verifying it, so a wrong body compiles and fails at runtime.
- **Narrowing `unknown` with `typeof v === 'object'` alone.** `null` passes that test too, and the next line reports "`v` is possibly `null`". Add `v !== null`.
- **Using `if (x)` on a value that can be `0` or `""`.** Both are falsy ([note 01](01-js-for-python-devs.md)), so a real value is treated as missing. Use `x === null` or `x == null`.

---

## Try it

[`practice/typescript-exercises/02`](../practice/typescript-exercises/02/index.ts), [`03`](../practice/typescript-exercises/03/index.ts) and [`04`](../practice/typescript-exercises/04/index.ts): unions of `User | Admin`, narrowing with `in`, and type predicates. From `practice/`, check each with `node check.ts exercises/02/` (and so on).

## Next

[Generics](04-generics.md).
