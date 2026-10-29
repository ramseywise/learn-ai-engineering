// Typecheck every exercise and report ok / FAIL per exercise.
//   node check.ts              your work (unsolved exercises fail; that's expected)
//   node check.ts 07           only exercises whose path contains "07"
//   node check.ts --solutions  swap every solution in and typecheck that copy (must be all ok)
import { execFileSync } from 'node:child_process';
import { cpSync, mkdtempSync, readdirSync, renameSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, relative } from 'node:path';

const here = import.meta.dirname;
const args = process.argv.slice(2);
const solutions = args.includes('--solutions');
const filter = args.find((a) => !a.startsWith('--'));

function units(): string[] {
  const ex = readdirSync(join(here, 'typescript-exercises')).filter((d) => /^\d\d$/.test(d)).map((d) => `typescript-exercises/${d}/`);
  const tc = readdirSync(join(here, 'type-challenges/challenges')).map((f) => `type-challenges/challenges/${f}`);
  const own = readdirSync(join(here, 'exercises')).map((f) => `exercises/${f}`);
  return [...ex, ...tc, ...own].filter((u) => !filter || u.includes(filter));
}

function swapInSolutions(root: string): void {
  for (const entry of readdirSync(join(root, 'typescript-exercises'), { recursive: true, encoding: 'utf8' })) {
    const m = entry.match(/^(.*)\.solution(\.d)?\.ts$/);
    if (m) renameSync(join(root, 'typescript-exercises', entry), join(root, 'typescript-exercises', `${m[1]}${m[2] ?? ''}.ts`));
  }
  cpSync(join(root, 'type-challenges/solutions'), join(root, 'type-challenges/challenges'), { recursive: true });
  cpSync(join(root, 'solutions'), join(root, 'exercises'), { recursive: true });
}

let root = here;
if (solutions) {
  root = mkdtempSync(join(tmpdir(), 'ts-practice-'));
  cpSync(here, root, { recursive: true, filter: (src) => !relative(here, src).startsWith('node_modules') });
  symlinkSync(join(here, 'node_modules'), join(root, 'node_modules'));
  swapInSolutions(root);
}

let output = '';
try {
  execFileSync(join(here, 'node_modules/.bin/tsc'), ['-p', '.'], { cwd: root, encoding: 'utf8' });
} catch (err) {
  output = (err as { stdout: string }).stdout;
}
if (solutions) rmSync(root, { recursive: true, force: true });

const errorLines = output.split('\n').filter((l) => l.includes('error TS'));
let failed = 0;
for (const unit of units()) {
  const errors = errorLines.filter((l) => l.startsWith(unit));
  if (errors.length) failed++;
  console.log(`${errors.length ? 'FAIL' : 'ok  '}  ${unit}${errors.length ? `  (${errors.length} errors)` : ''}`);
}
const stray = errorLines.filter((l) => !units().some((u) => l.startsWith(u)) && !filter);
for (const l of stray) console.log(`FAIL  ${l}`);
console.log(`\n${units().length - failed}/${units().length} passing`);
process.exit(failed || stray.length ? 1 : 0);
