# Lab 3 — Self-modification triggered by failure trajectories

> Adapted from Bojie Li, *AI Agents in Depth*, Experiment 8-5 ([upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter8/self-modifying-agent), Apache-2.0). The README has been translated to English. Concepts: [note 08 — Self-modification as a release process](../../notes/08-self-improving-loops.md#self-modification-as-a-release-process).

Suppose production trajectories show an agent calling the same tool again and again after a `retryable=false` error. The system should fix the agent's retry and circuit-breaker code. Adding "don't repeat the call" to the prompt is the wrong layer: the constraint can be enforced deterministically, so it belongs in code.

## Run

```bash
python demo.py
python -m unittest -v test_evolution.py
```

`python demo.py` uses a deterministic patch generator, so you can inspect the release protocol offline. To try a real LLM coding agent:

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key_here
python demo.py --generator llm --model gpt-5.6
```

LLM mode uses the OpenAI Responses API. The model reads the failure diagnosis and the stable source, then returns a complete candidate module. Its output can only be written to `output/candidate/`. Everything else is done by code outside the model: static compilation, failure replay, old-task regression, the release decision and the rollback version. If the LLM produces a plausible patch that breaks the old retry behaviour, the command returns `reject_candidate`.

## How it works

1. **Diagnose.** Repeated faults are aggregated from `failure_trajectories.json`. A modification request is created only when the same pattern is supported by several trajectories. The root cause is located in `stable/retry_policy.py`.
2. **Generate.** The candidate generator produces a minimal diff from the stable source. It writes only to `output/candidate/` and never overwrites the running stable version.
3. **Validate.** The candidate is compiled, and the original failure trajectories are replayed: a non-retryable error must stop at once and open the circuit breaker. Transient timeouts are then retested, so the original retry behaviour and thresholds must not regress.
4. **Decide.** Only if every check passes does the run emit `release_to_canary`. Otherwise it emits `reject_candidate`. `release_manifest.json` records:
   - the source cases;
   - the target file;
   - the code diff;
   - the check results;
   - the candidate version and the rollback version.

The deterministic generator keeps the lab reproducible offline. In production you can swap in a coding agent. But the patch-generating model must not be able to bypass the candidate branch, failure replay, old-task regression, canary and rollback steps. The stable code, the audit log and the validators that approve a release are the **trusted root**, outside ordinary self-modification permissions.
