---
origin: curated
sources:
  - "Zod documentation — https://zod.dev (MIT)"
  - "Alexis King, Parse, don't validate — https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/"
concepts: [runtime-validation, zod, schema-inference, parse-dont-validate, env-config]
cleaned: 2026-10-29
---
# 8 — Runtime Validation with Zod

> Types are erased at runtime, so any data from outside the program (JSON bodies, env vars, files, LLM output) is really `unknown`. Parse it into a typed value at the boundary, once, and trust it everywhere after that.

---

## The problem

```ts
const user = (await res.json()) as User;   // compiles. Checks nothing.
user.email.toLowerCase();                  // crashes at runtime if the API sent { mail: … }
```

`as` is an assertion: "trust me". The fix is a schema that validates at runtime **and** produces the static type, so the two can't drift apart. It is the TS equivalent of Pydantic.

## Zod basics (v4)

```ts
import { z } from 'zod';

const User = z.object({
  id: z.number().int().positive(),
  email: z.email(),
  name: z.string().min(1),
  role: z.enum(['user', 'admin']).default('user'),
  tags: z.array(z.string()).optional(),
});
type User = z.infer<typeof User>;   // the static type is derived from the schema

User.parse(data);                    // returns a User or throws ZodError
const r = User.safeParse(data);      // { success: true, data } | { success: false, error }
if (!r.success) console.log(r.error.issues);   // [{ path: ['email'], message: … }, …]
```

| Need | Zod |
|---|---|
| Optional / nullable | `.optional()`, `.nullable()`, `.nullish()` |
| Defaults | `.default(v)` (the input may omit the field. The output always has it) |
| Strings to numbers or booleans | `z.coerce.number()`. For env flags, prefer `z.enum(['true','false'])` because `coerce.boolean()` treats `"false"` as `true` |
| Clean up while parsing | `.trim()`, `.toLowerCase()`, `.transform(fn)` |
| Custom rules | `.refine((v) => …, 'message')` |
| Tagged unions | `z.discriminatedUnion('type', [A, B])` |
| Reject unknown keys | `z.strictObject({…})` |
| Partial for updates | `User.partial()`, `User.pick({…})`, `User.omit({…})` |

## Where to parse

**Parse, don't validate.** Turn `unknown` into a precise type at the edge, then pass the typed value around. Don't keep re-checking it deep inside the code.

| Boundary | Example |
|---|---|
| Config | `const config = Config.parse(process.env)` at startup, so a bad deploy fails fast |
| HTTP | Parse request bodies in the handler, and parse API responses in the client |
| Files | `Schema.parse(JSON.parse(text))` |
| LLM output | Use structured output so the model is constrained to the schema, and still parse the result ([note 09](09-typescript-for-ai-apps.md)) |
| Tool inputs | Parse model-supplied tool arguments before running anything |

## One schema, many uses

A zod schema can also produce JSON Schema (`z.toJSONSchema(User)`). That is how SDKs turn a zod object into an LLM tool definition or a structured-output format. You write the shape once, and you get the type, the validation and the schema the model sees.

## Alternatives

Valibot (tiny bundles), ArkType (TS-like syntax, fast) and TypeBox (JSON Schema first) all solve the same problem. Pick one per codebase. Zod has the largest ecosystem, and the Anthropic SDK has zod helpers.

---

## Exercises

[`practice/exercises/08-zod.ts`](../practice/exercises/08-zod.ts): env config with defaults, chat messages, error reporting with `safeParse`, and parsing an LLM's fenced JSON. From `practice/`, check with `npm test`.
