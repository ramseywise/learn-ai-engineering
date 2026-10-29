/*
  03057 · Push
  https://github.com/type-challenges/type-challenges/blob/main/questions/03057-easy-push/README.md

  Implement the generic version of ```Array.push```

  For example:

  ```typescript
  type Result = Push<[1, 2], '3'> // [1, 2, '3']
  ```
*/

import type { Equal, Expect } from '@type-challenges/utils'

/* _____________ Solution _____________ */

type Push<T extends unknown[], U> = [...T, U]

/* _____________ Test cases _____________ */

type cases = [
  Expect<Equal<Push<[], 1>, [1]>>,
  Expect<Equal<Push<[1, 2], '3'>, [1, 2, '3']>>,
  Expect<Equal<Push<['1', 2, '3'], boolean>, ['1', 2, '3', boolean]>>,
]

type errors = [
  // @ts-expect-error
  Expect<Equal<Push<number[], string>, string[]>>,
  // @ts-expect-error
  Expect<Equal<Push<string[], number>, [string, number]>>,
]
