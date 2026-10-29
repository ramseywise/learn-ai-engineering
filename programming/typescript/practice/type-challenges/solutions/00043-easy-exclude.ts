/*
  00043 · Exclude
  https://github.com/type-challenges/type-challenges/blob/main/questions/00043-easy-exclude/README.md

  Implement the built-in `Exclude<T, U>`

  > Exclude from `T` those types that are assignable to `U`

  For example:

  ```ts
  type Result = MyExclude<'a' | 'b' | 'c', 'a'> // 'b' | 'c'
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Solution _____________ */

type MyExclude<T, U> = T extends U ? never : T

/* _____________ Test cases _____________ */

type cases = [
  Expect<Equal<MyExclude<'a' | 'b' | 'c', 'a'>, 'b' | 'c'>>,
  Expect<Equal<MyExclude<'a' | 'b' | 'c', 'a' | 'b'>, 'c'>>,
  Expect<Equal<MyExclude<string | number | (() => void), Function>, string | number>>,
]
