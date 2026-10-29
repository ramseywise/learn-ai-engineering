// Tests import your exercises by default; `npm run test:solutions` (TARGET=solutions) imports the solutions.
export const target = (name: string): string =>
  `../${process.env.TARGET === 'solutions' ? 'solutions' : 'exercises'}/${name}.ts`;
