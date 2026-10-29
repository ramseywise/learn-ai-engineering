/*
  00533 · Concat
  https://github.com/type-challenges/type-challenges/blob/main/questions/00533-easy-concat/README.md

  Implement the JavaScript `Array.concat` function in the type system. A type takes the two arguments. The output should be a new array that includes inputs in ltr order

  For example:

  ```ts
  type Result = Concat<[1], [2]> // expected to be [1, 2]
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Solution _____________ */

type Concat<T extends readonly unknown[], U extends readonly unknown[]> = [...T, ...U]

/* _____________ Test cases _____________ */

const tuple = [1] as const

type cases = [
  Expect<Equal<Concat<[], []>, []>>,
  Expect<Equal<Concat<[], [1]>, [1]>>,
  Expect<Equal<Concat<typeof tuple, typeof tuple>, [1, 1]>>,
  Expect<Equal<Concat<[1, 2], [3, 4]>, [1, 2, 3, 4]>>,
  Expect<Equal<Concat<['1', 2, '3'], [false, boolean, '4']>, ['1', 2, '3', false, boolean, '4']>>,
]

// @ts-expect-error
type error = Concat<null, undefined>
