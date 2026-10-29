/*
  00106 · Trim Left
  https://github.com/type-challenges/type-challenges/blob/main/questions/00106-medium-trimleft/README.md

  Implement `TrimLeft<T>` which takes an exact string type and returns a new string with the whitespace beginning removed.

  For example

  ```ts
  type trimmed = TrimLeft<'  Hello World  '> // expected to be 'Hello World  '
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Your code here _____________ */

type TrimLeft<S extends string> = any

/* _____________ Test cases _____________ */

type cases = [
  Expect<Equal<TrimLeft<'str'>, 'str'>>,
  Expect<Equal<TrimLeft<' str'>, 'str'>>,
  Expect<Equal<TrimLeft<'     str'>, 'str'>>,
  Expect<Equal<TrimLeft<'     str     '>, 'str     '>>,
  Expect<Equal<TrimLeft<'   \n\t foo bar '>, 'foo bar '>>,
  Expect<Equal<TrimLeft<''>, ''>>,
  Expect<Equal<TrimLeft<' \n\t'>, ''>>,
]
