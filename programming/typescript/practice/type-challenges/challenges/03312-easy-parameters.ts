/*
  03312 · Parameters
  https://github.com/type-challenges/type-challenges/blob/main/questions/03312-easy-parameters/README.md

  Implement the built-in Parameters<T> generic without using it.

  For example:

  ```ts
  const foo = (arg1: string, arg2: number): void => {}

  type FunctionParamsType = MyParameters<typeof foo> // [arg1: string, arg2: number]
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Your code here _____________ */

type MyParameters<T extends (...args: any[]) => any> = any

/* _____________ Test cases _____________ */

function foo(arg1: string, arg2: number): void {}
function bar(arg1: boolean, arg2: { a: 'A' }): void {}
function baz(): void {}

type cases = [
  Expect<Equal<MyParameters<typeof foo>, [string, number]>>,
  Expect<Equal<MyParameters<typeof bar>, [boolean, { a: 'A' }]>>,
  Expect<Equal<MyParameters<typeof baz>, []>>,
]
