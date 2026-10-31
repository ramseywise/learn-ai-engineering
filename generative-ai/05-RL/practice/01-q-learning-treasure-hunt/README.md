# Lab 1 — Q-learning on a treasure hunt

> Adapted from Bojie Li, *AI Agents in Depth*, Experiment 7-1 ([upstream](https://github.com/bojieli/ai-agent-book/tree/main/chapter1/learning-from-experience), Apache-2.0). This lab keeps only the game environment, the tabular Q-learning agent and its training script. The upstream LLM agent (Experiment 7-2) needs an API key and is left out. Concepts: [post-training for agents](../../notes/05-post-training-for-agents.md#classic-rl-vs-llm-rl-why-priors-win).

A text adventure with hidden rules. The agent has to learn several things nobody tells it:

- The red key opens the locked hallway door.
- The rusty sword plus the magic crystal crafts a silver sword.
- Only the silver sword beats the strong guard and the dragon.

The optimal path is 11 moves. Rewards are sparse: −0.5 per move, small bonuses for picking up key items or crafting, and +100 for the treasure.

| File | What it holds |
|---|---|
| `game_environment.py` | `TreasureHuntGame`: rooms, items, locked exits, guards, crafting. `stochastic=True` adds reward noise, a 3% fumble chance, combat crits and misses, and crafting failures |
| `rl_agent.py` | `QLearningAgent`: a state hash of room, inventory, room items, locks and guard; ε-greedy action choice; the update `Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') − Q(s,a)]`. `DQNAgent` is only a stub |
| `test_rl_learning.py` | Trains a fresh agent for each episode count, then evaluates it greedily over 100 games and prints a winning trajectory |

## Run

Needs `numpy` only. No network.

```bash
pip install numpy                                   # or: uv run --no-project --with numpy python ...
python test_rl_learning.py --episodes 1000 10000    # ~10 s
python test_rl_learning.py --stochastic --episodes 10000
```

Expected (deterministic): **0/100 wins after 1,000 episodes, 100/100 after 10,000**, with about 144 states in the Q-table and the 11-move solution printed.

## What to notice

The agent needs about 10,000 full games to learn a puzzle that an LLM agent solves on its first try in about 18 moves (book Exp 7-2, where Kimi K3 kept a 50-entry experience buffer). To Q-learning, "door", "key" and "sword" are opaque symbols. The LLM brings priors from pretraining. Ten seconds of simulation is cheap here, but 10,000 trials are not affordable when every trial is a real phone call or browser session. That gap is why the field reordered its priorities to **prior > environment > algorithm**.

## Exercises

1. **Watch value propagate.** Run with `--episodes 1000 3000 5000 7000 8000 10000`. Win rate stays near zero, then jumps. The +100 at the end has to back up through 11 steps of `max Q(s', a')` before early moves look good.
2. **Make the reward sparser.** In `game_environment.py`, set the item-pickup bonuses in `_take_item` (5 / 3 / 2) and the crafting bonus (10) to 0, leaving only −0.5 per move and +100 for the treasure. How many more episodes does it take? This is the sparse-reward problem in miniature.
3. **Discount factor.** Change `discount_factor` from 0.99 to 0.9, then 0.5. With γ = 0.5, the +100 is worth about 0.1 eleven steps back. Does the agent still learn the full path?
4. **Exploration schedule.** Change `epsilon_decay` to 0.999 (fast) and 0.99995 (slow). Too fast, and the agent exploits before it has ever reached the treasure. Too slow, and it wastes episodes.
5. **Stochastic mode.** Run `--stochastic`. Which of the noise sources (reward jitter, fumbles, combat variance, crafting failure) hurts most, and why does a tabular agent with no model of the environment suffer from it?
6. **Change the rules.** Swap the crafting recipe or which key opens which door. A trained Q-table is useless and must be retrained from scratch. This is the "knowledge doesn't transfer" limit of MDP agents.
