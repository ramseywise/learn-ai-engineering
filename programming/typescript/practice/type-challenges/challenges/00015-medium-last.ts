/*
  00015 · Last of Array
  https://github.com/type-challenges/type-challenges/blob/main/questions/00015-medium-last/README.md

  > TypeScript 4.0 is recommended in this challenge

  Implement a generic `Last<T>` that takes an Array `T` and returns its last element.

  For example

  ```ts
  type arr1 = ['a', 'b', 'c']
  type arr2 = [3, 2, 1]

  type tail1 = Last<arr1> // expected to be 'c'
  type tail2 = Last<arr2> // expected to be 1
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Your code here _____________ */

type Last<T extends any[]> = any

/* _____________ Test cases _____________ */

type cases = [
  Expect<Equal<Last<[]>, never>>,
  Expect<Equal<Last<[2]>, 2>>,
  Expect<Equal<Last<[3, 2, 1]>, 1>>,
  Expect<Equal<Last<[() => 123, { a: string }]>, { a: string }>>,
]
