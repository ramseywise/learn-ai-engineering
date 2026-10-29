/*
  00191 · Append Argument
  https://github.com/type-challenges/type-challenges/blob/main/questions/00191-medium-append-argument/README.md

  For given function type `Fn`, and any type `A` (any in this context means we don't restrict the type, and I don't have in mind any type 😉) create a generic type which will take `Fn` as the first argument, `A` as the second, and will produce function type `G` which will be the same as `Fn` but with appended argument `A` as a last one.

  For example,

  ```typescript
  type Fn = (a: number, b: string) => number

  type Result = AppendArgument<Fn, boolean>
  // expected be (a: number, b: string, x: boolean) => number
  ```

  > This question is ported from the [original article](https://dev.to/macsikora/advanced-typescript-exercises-question-4-495c) by [@maciejsikora](https://github.com/maciejsikora)
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Solution _____________ */

type AppendArgument<Fn extends (...args: any[]) => any, A> =
  Fn extends (...args: infer P) => infer R ? (...args: [...P, A]) => R : never

/* _____________ Test cases _____________ */

type Case1 = AppendArgument<(a: number, b: string) => number, boolean>
type Result1 = (a: number, b: string, x: boolean) => number

type Case2 = AppendArgument<() => void, undefined>
type Result2 = (x: undefined) => void

type cases = [
  Expect<Equal<Case1, Result1>>,
  Expect<Equal<Case2, Result2>>,
  // @ts-expect-error
  AppendArgument<unknown, undefined>,
]
