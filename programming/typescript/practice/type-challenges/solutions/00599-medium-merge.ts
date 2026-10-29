/*
  00599 · Merge
  https://github.com/type-challenges/type-challenges/blob/main/questions/00599-medium-merge/README.md

  Merge two types into a new type. Keys of the second type overrides keys of the first type.

  For example

  ```ts
  type foo = {
    name: string
    age: string
  }
  type coo = {
    age: number
    sex: string
  }

  type Result = Merge<foo, coo> // expected to be {name: string, age: number, sex: string}
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Solution _____________ */

type Merge<F, S> = { [K in keyof F | keyof S]: K extends keyof S ? S[K] : K extends keyof F ? F[K] : never }

/* _____________ Test cases _____________ */

type Foo = {
  a: number
  b: string
}
type Bar = {
  b: number
  c: boolean
}

type cases = [
  Expect<Equal<Merge<Foo, Bar>, {
    a: number
    b: number
    c: boolean
  }>>,
]
