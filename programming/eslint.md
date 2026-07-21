# ESLint — Reading & Fixing Findings (TS/React)

Learning note from a real sweep of `nonprofit-success-ai`: 23 problems, but only **3
rules**. Learn the rule, not the 23 lines. Run the linter with:

```bash
npx eslint .            # report only
npx eslint . --fix      # auto-fix what's mechanically safe (formatting, some rules)
```

A finding reads: `line:col  error/warning  <message>  <rule-name>`. The rule-name on the
right is the thing to look up — every rule has docs at `typescript-eslint.io/rules/<name>`
or `react.dev`.

---

## Rule 1 — `@typescript-eslint/no-unused-vars` (dead imports)

> `'AnimatePresence' is defined but never used`

You imported a name and never used it. Almost always a leftover from deleting the code that
used it. Harmless at runtime, but it bloats the bundle and signals drift.

**Why it matters:** an unused import is a lie about what the file depends on. The next reader
assumes it's used.

**Fix:** delete the name from the import. `--fix` will *not* remove these — it can't be sure
you didn't mean to use it — so they're manual, but trivial.

```ts
// before
import { motion, AnimatePresence } from "framer-motion"; // AnimatePresence never used
// after
import { motion } from "framer-motion";
```

**The habit:** when you delete code, delete its imports in the same edit.

---

## Rule 2 — `@typescript-eslint/no-explicit-any` (the one worth learning)

> `Unexpected any. Specify a different type`

`: any` **turns off type-checking** for that value. TypeScript stops helping you — no
autocomplete, no error if you access a field that doesn't exist. It defeats the point of TS.

Every `any` in this codebase had a *correct* type we were skipping:

```ts
// src/types.ts — these are Firestore Timestamps, not `any`
submittedAt: any;   // → import { Timestamp } from "firebase/firestore";  submittedAt: Timestamp;
createdAt: any;     // → createdAt: Timestamp;
updatedAt: any;     // → updatedAt: Timestamp;

// src/App.tsx — this is a Firebase Auth user
function Navbar({ user }: { user: any, ... })     // → user: User | null  (from "firebase/auth")
const [user, setUser] = useState<any>(null);      // → useState<User | null>(null)

// src/components/business/BusinessPortal.tsx — this is a Lucide icon component
icon: any;   // → import { LucideIcon } from "lucide-react";  icon: LucideIcon;
```

**The three escapes from `any`, in order of preference:**

| Use | When | Behaviour |
|-----|------|-----------|
| a real type / interface | you know the shape (`Timestamp`, `User`, `LucideIcon`) | full checking — best |
| `unknown` | you genuinely don't know yet | forces you to *narrow* (`typeof`, a check) before use — "safe any" |
| generic `<T>` | the type varies by caller | caller supplies the type |

`unknown` is the key idea: it's `any` with the safety on. `any` says "trust me, don't
check"; `unknown` says "I don't know — make me prove it before I use it."

**Types files are highest-leverage.** An `any` in `types.ts` leaks into every file that
imports that type. Fix those first.

---

## Rule 3 — `react-hooks/exhaustive-deps` (React-specific, subtle)

> `React Hook useEffect has missing dependencies: 'isDemo' and 'navigate'`

A `useEffect(() => {...}, [deps])` re-runs whenever something in `[deps]` changes. If you
*use* a value inside the effect but leave it out of the array, the effect keeps running with
the **stale** (first-render) value — a classic React bug.

```tsx
useEffect(() => {
  if (isDemo) navigate("/demo");   // uses isDemo + navigate...
}, []);                            // ...but deps array is empty → stale closure
// fix: }, [isDemo, navigate]);
```

**Why it's a warning, not an error:** sometimes omitting a dep is intentional (you truly
want run-once-on-mount). React can't tell, so it warns instead of failing. If the omission
is deliberate, say so:

```tsx
// eslint-disable-next-line react-hooks/exhaustive-deps
}, []);   // run once on mount — isDemo never changes after first render
```

Don't reflexively silence it. 9 times out of 10 the fix is to add the dep; the disable
comment is for the documented exception.

---

## Cheat sheet

| Rule | Means | Fix |
|------|-------|-----|
| `no-unused-vars` | imported, never used | delete the import (manual) |
| `no-explicit-any` | type-checking off for this value | real type > `unknown` > generic |
| `react-hooks/exhaustive-deps` | effect uses a value not in its deps | add the dep, or disable-comment if intentional |

**Order to fix a sweep:** unused vars first (mechanical, clears the noise) → `any` in
types files (highest leverage) → `any` in components → hook deps (think about each one).
