---
origin: curated
sources:
  - "TypeScript Handbook — https://www.typescriptlang.org/docs/handbook/ (CC-BY 4.0; paraphrased, not copied)"
  - "MDN JavaScript Guide — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide (CC-BY-SA 2.5; read, not copied)"
concepts: [javascript-basics, ts-runtime, equality, truthiness, arrays-objects, maps-sets]
cleaned: 2026-10-29
---
# 1 — JavaScript for Python Developers

> TypeScript is JavaScript with a type checker in front. The checker runs and then disappears. What actually executes is JavaScript, so learn the runtime first.

---

## How TS runs

| Step | What happens |
|---|---|
| `tsc --noEmit` | Type-checks only. Nothing runs |
| `node file.ts` | Node 22.18+ **strips** the types and runs the rest. No checking at all |
| `tsc` / bundler | Emits `.js` files for production |

There are no runtime types. `x as User` checks nothing, and an `interface` produces no code. Data from outside the program has to be validated ([note 08](08-runtime-validation-zod.md)).

## Python → JavaScript

| Python | JavaScript / TypeScript | Watch out |
|---|---|---|
| `x = 1` | `const x = 1` (or `let` if you reassign it) | Never use `var` |
| `None` | `null` **and** `undefined` | `x == null` catches both. Otherwise always use `===` |
| `f"{a} b"` | `` `${a} b` `` | Template literals use backticks |
| `list` | `Array`: `push`, `slice`, `map`, `filter`, `reduce` | `sort()` **sorts in place and compares as strings** by default. Use `sort((a, b) => a - b)` |
| `dict` with arbitrary keys | `Map` | A plain object's keys are always strings, and it inherits prototype keys |
| `set` | `Set` | It compares objects by reference |
| `len(xs)` | `xs.length`, `map.size` | |
| `for x in xs` | `for (const x of xs)` | `for…in` iterates **keys**. Don't use it on arrays |
| `enumerate` | `xs.entries()` or `xs.forEach((x, i) => …)` | |
| `[f(x) for x in xs if p(x)]` | `xs.filter(p).map(f)` | |
| `a, *rest = xs` | `const [a, ...rest] = xs` | Objects destructure too: `const { id, ...others } = user` |
| `d.get(k, 0)` | `d.get(k) ?? 0` | `??` treats only `null`/`undefined` as missing. `||` also replaces `0` and `""` |
| `a and a.b` | `a?.b` | Optional chaining |
| `lambda x: x * 2` | `(x) => x * 2` | Arrow functions don't rebind `this` |
| `raise` / `try/except` | `throw` / `try/catch` | The caught value is `unknown`. Narrow it with `instanceof Error` |
| `import x from y` | `import { x } from './y.ts'` | ES modules ([note 07](07-modules-and-tooling.md)) |

## Truthiness and equality

- Falsy values: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. **`[]` and `{}` are truthy**, the opposite of Python.
- `==` coerces types (`"1" == 1` is true). Always use `===`. The one useful exception is `x == null`.
- `===` compares objects and arrays **by reference**: `[1] === [1]` is false. Write a comparison yourself or use `assert.deepEqual` in tests.
- Numbers are 64-bit floats: `0.1 + 0.2 !== 0.3`, and integers are exact only up to 2^53. Use `bigint` (`10n`) beyond that.

## Objects, references and copies

```ts
const a = { tags: ['x'] };
const b = { ...a };              // shallow copy, like dict(a)
b.tags.push('y');                // a.tags changes too: the inner array is shared
const c = structuredClone(a);    // deep copy, like copy.deepcopy
```

`const` stops the variable from being **reassigned**. It does not stop the value from being **mutated**. For that, use `readonly` types ([note 05](05-type-transformations.md)) or `Object.freeze`.

## Classes (briefly)

```ts
class Counter {
  #count = 0;                         // truly private (runtime), unlike Python's _name
  constructor(private readonly step = 1) {}   // parameter property: declares and assigns
  inc(): number { return (this.#count += this.step); }
}
```

Most TS code uses plain objects, functions and union types more than class hierarchies.

---

## Exercises

[`practice/exercises/01-js-basics.ts`](../practice/exercises/01-js-basics.ts): Counter, `most_common`, chunk, zip and more, in idiomatic TS. From `practice/`, check with `npm test`.
