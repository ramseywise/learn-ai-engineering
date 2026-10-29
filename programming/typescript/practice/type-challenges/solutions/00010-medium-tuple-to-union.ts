/*
  00010 · Tuple to Union
  https://github.com/type-challenges/type-challenges/blob/main/questions/00010-medium-tuple-to-union/README.md

  Implement a generic `TupleToUnion<T>` which covers the values of a tuple to its values union.

  For example

  ```ts
  type Arr = ['1', '2', '3']

  type Test = TupleToUnion<Arr> // expected to be '1' | '2' | '3'
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Solution _____________ */

type TupleToUnion<T> = T extends readonly (infer E)[] ? E : never

/* _____________ Test cases _____________ */

type cases = [
  Expect<Equal<TupleToUnion<[123, '456', true]>, 123 | '456' | true>>,
  Expect<Equal<TupleToUnion<[123]>, 123>>,
]
