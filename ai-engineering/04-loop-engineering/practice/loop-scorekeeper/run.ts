import { runLoop, type Limits, type Result } from "./loop.ts";
import { chooseModel } from "./model.ts";
import { gamer, honest, overfit, stuck } from "./stub.ts";

const limits: Limits = { maxIterations: 6, maxTokens: 4000, patience: 2 };

function report(name: string, r: Result) {
  console.log(`\n--- ${name}: stop=${r.stop}, ${r.iterations.length} iterations, ${r.tokens} tokens, shippable=${r.best !== null}`);
  for (const i of r.iterations) console.log(`  #${i.n}  visible ${i.visible.passed}/${i.visible.total}   held-out ${i.heldOut.passed}/${i.heldOut.total}`);
}

if (process.env.MODEL) {
  const { name, complete } = await chooseModel(honest);
  report(name, await runLoop(complete, { ...limits, maxTokens: 60000 }));
} else {
  report("honest maker", await runLoop(honest, limits));
  report("maker memorises the visible checks", await runLoop(gamer, limits));
  report("ordinary overfit", await runLoop(overfit, limits));
  report("stuck maker", await runLoop(stuck, limits));
  report("expensive maker", await runLoop(honest, { ...limits, maxTokens: 150 }));
}
