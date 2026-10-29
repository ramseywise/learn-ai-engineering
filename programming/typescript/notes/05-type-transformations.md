---
origin: curated
sources:
  - "TypeScript Handbook, Type Manipulation — https://www.typescriptlang.org/docs/handbook/2/types-from-types.html (CC-BY 4.0; paraphrased)"
  - "TypeScript Handbook, Utility Types — https://www.typescriptlang.org/docs/handbook/utility-types.html (CC-BY 4.0; paraphrased)"
  - "type-challenges — https://github.com/type-challenges/type-challenges (MIT; vendored in practice/)"
concepts: [ts-utility-types, ts-mapped-types, ts-conditional-types, ts-infer, ts-template-literal-types, ts-intersections]
cleaned: 2026-10-29
---
# 5 — Building Types from Types

> Write a type once and derive the rest. Utility types cover everyday cases; mapped and conditional types are how the utilities themselves are built.

---

## Utility types you'll use weekly

| Utility | Result | Typical use |
|---|---|---|
| `Partial<T>` | Every property optional | Update payloads, filter criteria |
| `Required<T>` | Every property required | After defaults are applied |
| `Readonly<T>` | Every property `readonly` | Config, frozen state |
| `Pick<T, 'a' \| 'b'>` | Only those keys | View models |
| `Omit<T, 'id'>` | Everything except those keys | Create payloads without a server ID |
| `Record<K, V>` | An object with keys `K` and values `V` | Lookup tables: `Record<Status, string>` |
| `Exclude<U, X>` / `Extract<U, X>` | Remove or keep union members | `Exclude<Shape['kind'], 'circle'>` |
| `NonNullable<T>` | Remove `null` and `undefined` | |
| `ReturnType<F>` / `Parameters<F>` | A function's output and input types | Typing wrappers |
| `Awaited<T>` | Unwrap a `Promise` | `Awaited<ReturnType<typeof fetchUser>>` |

## Intersections

```ts
type PowerUser = Omit<User, 'type'> & Omit<Admin, 'type'> & { type: 'powerUser' };
```

`A & B` has every property of both. It is how you combine types without repeating fields.

## Mapped types

Loop over keys to build a new object type:

```ts
type MyReadonly<T> = { readonly [K in keyof T]: T[K] };
type Nullable<T> = { [K in keyof T]: T[K] | null };
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
// Getters<{ name: string }> = { getName: () => string }
```

Modifiers: `readonly` / `?` add, and `-readonly` / `-?` remove (that is how `Required` works). `as` remaps or filters keys. Mapping a key to `never` drops it.

## Conditional types

```ts
type IsString<T> = T extends string ? true : false;
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;   // infer captures a piece
type MyAwaited<T> = T extends PromiseLike<infer V> ? MyAwaited<V> : T;  // recursion is allowed
```

- `infer X` pattern-matches part of a type, like destructuring.
- **Distribution.** When `T` is a bare type parameter and you pass a union, the conditional applies to each member separately: `IsString<string | number>` is `boolean`. Wrap both sides in brackets (`[T] extends [string]`) to turn distribution off.

## Template literal types

```ts
type Event = 'click' | 'focus';
type Handler = `on${Capitalize<Event>}`;          // 'onClick' | 'onFocus'
type TrimLeft<S extends string> = S extends ` ${infer R}` ? TrimLeft<R> : S;
```

## When to stop

Type-level code is real code: it is hard to read and debug, and slow to compile. Use utility types freely, mapped types sometimes, and deep conditional recursion only in libraries. If an application type needs `infer` three levels deep, a simpler runtime design is usually better.

---

## Exercises

- [`practice/typescript-exercises/05`](../practice/typescript-exercises/05/index.ts) (`Partial`/`Omit`), [`08`](../practice/typescript-exercises/08/index.ts) (intersections), [`14`](../practice/typescript-exercises/14/index.ts) (typing curried helpers) and [`15`](../practice/typescript-exercises/15/index.ts) (an object-manipulation library)
- **Medium** type challenges: `*-medium-*.ts` (ReturnType, Omit, DeepReadonly, TupleToUnion, Chainable, Last, PromiseAll, TypeLookup, TrimLeft, Capitalize, Replace, AppendArgument, Merge). From `practice/`, check with `node check.ts medium`.
