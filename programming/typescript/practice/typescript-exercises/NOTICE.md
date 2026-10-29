# typescript-exercises (vendored)

Exercises 1–15 from [mdevils/typescript-exercises](https://github.com/mdevils/typescript-exercises)
by Marat Dulin, MIT (see [LICENSE](LICENSE)). Exercise 16 is the closing page and is left out.

Each folder has `index.ts` (yours to fix), `test.ts` (type assertions that must compile) and, where
upstream provides one, `index.solution.ts`. In 11–12 you edit `declarations/<lib>/index.d.ts`; in 13,
`module-augmentations/date-wizard/index.ts`.

Changes from upstream, so the exercises run under a plain `tsc` instead of the upstream web app:

- The fake libraries in `11–13/node_modules/` moved to `vendor/`, and the intros point there.
- The upstream `type-assertions` helper lives in [`type-assertions/index.ts`](type-assertions/index.ts),
  mapped by `paths` in `../tsconfig.json`.
- `06/index.solution.ts`: `getObjectKeys` is constrained to `T extends object` (needed since TS 4.8).
- `13/index.ts`: `import dateWizard from 'date-wizard'` replaces `import * as`, since a namespace
  import of an `export =` function is not callable under `esModuleInterop`.

Exercise 04 already compiles unchanged, because TypeScript 5.5+ infers the type predicates
(`person is Admin`) that the exercise asks you to write. Write them explicitly anyway; inference only
covers simple bodies like these.
