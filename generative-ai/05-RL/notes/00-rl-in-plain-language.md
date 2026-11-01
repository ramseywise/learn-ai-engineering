---
origin: web-authored
sources:
  - Phil Winder, "Reinforcement Learning: Industrial Applications of Intelligent Agents" (O'Reilly, 2020), ch. 1
  - Sutton & Barto, "Reinforcement Learning: An Introduction" (2nd ed., 2018), http://incompleteideas.net/book/the-book-2nd.html
  - https://huggingface.co/learn/deep-rl-course/unit0/introduction
confidence: high
cleaned: 2026-11-01
---

# 0 — Reinforcement Learning in Plain Language

Picture a text adventure with hidden rules. A red key opens one door, a sword and a crystal combine into a better sword, and only that better sword beats the dragon. Nobody tells a program any of this. It may only try moves and see a score. How can it ever win? This chapter answers that with four short programs, no assumed maths, and no earlier machine learning. By the end you will know what the words *agent*, *reward*, *policy*, *value* and *exploration* mean, and why the people who train ChatGPT-style models care about them.

> **Who this is for:** anyone starting this pillar without the deep learning pillar behind them. You need to read simple Python. The first two programs use only the standard library, and the last two add a few lines of numpy.
> **Runs on:** a laptop, in seconds, with `uv run --no-project --with numpy python file.py`.

---

## Learning by trying

Most programs you have written follow instructions you worked out in advance. Most machine learning you may have met learns from an answer key: here are a thousand emails, here is which ones are spam, learn the pattern. Reinforcement learning, RL for short, has neither. A program acts, the world responds, and a number says how well that went. The program has to work out what to do from those numbers alone.

Phil Winder's comparison is learning to ride a bike (*Reinforcement Learning*, ch. 1). You could not learn it from a labelled dataset of riders. You get on, you wobble, you fall or you don't, and you adjust. That loop of acting and adjusting has four parts, and the rest of this pillar never leaves them.

```text
              action: "go through the door"
      ┌───────────────────────────────────────────┐
      │                                           ▼
 ┌─────────┐                               ┌─────────────┐
 │  AGENT  │                               │ ENVIRONMENT │
 │ decides │                               │ the rest of │
 │         │                               │ the world   │
 └─────────┘                               └─────────────┘
      ▲                                           │
      └───────────────────────────────────────────┘
       what it can now see, plus a reward: -0.5
```

- The **agent** is the part that decides. In our game, it is the program choosing the next move. In a chatbot, it is the language model choosing its next words.
- The **environment** is everything else: the game, the customer, the test suite. The agent can affect it but does not control it, and usually cannot see inside it.
- An **action** is one choice the agent makes: take the key, go north, call a tool.
- A **reward** is a number the environment hands back after an action. Positive is good, negative is bad. The agent's only goal is to collect as much reward as it can over time.

One feature separates this from the spam example: the reward comes late and it comes for a whole chain of choices. When the agent finally reaches the treasure, which of its earlier moves deserves the credit? Picking up the key eight moves ago mattered. Walking in a circle did not. Sorting that out is most of what RL does.

## The reward is the whole instruction

Because the reward is the only thing the agent is told, it is also the only thing you get to say. And it is easy to say the wrong thing. Winder gives a robot rewarded for reaching the end of a maze, which takes three days because it spends its time spinning in circles, and a shopping agent rewarded for adding the right product, which adds every product to the basket. He also gives an animal version: in 2011 a moose near Gothenburg was found stuck in a tree after eating fermented apples, because "eat a lot" is too generic a goal for staying alive (*Reinforcement Learning*, ch. 1). His advice for beginners is to keep the reward as simple as you can.

Hold on to that. By the end of this chapter, you will see the same mistake happen to a language model, and this whole pillar is in a sense an answer to it. **The reward signal is the product.** What you reward is what you get, including the parts you did not mean.

## Exploration: try the unknown or use what works?

Start with the simplest possible problem. There are three slot machines. Each pays out 1 point at its own hidden rate, and you get a thousand pulls. There is no chain of decisions and no late credit, just one question: which machine?

If you always pull the machine that looks best so far, you can get stuck. One lucky early pull on a poor machine makes it look great, and the machines you never tried keep their estimate of zero. If you always try at random, you never cash in what you have learned. This is the **exploration** problem: you need to spend some choices finding out, and the rest using what you found.

The common answer is one number, usually written with the Greek letter epsilon, ε, but it means only "the fraction of the time I act at random".

```python
import random

random.seed(0)
true_payout = {"A": 0.20, "B": 0.50, "C": 0.70}   # hidden from the agent

def play(epsilon, pulls=1000):
    estimate = {m: 0.0 for m in true_payout}      # the agent's beliefs
    count = {m: 0 for m in true_payout}
    total = 0
    for _ in range(pulls):
        if random.random() < epsilon:             # explore: try anything
            machine = random.choice(list(true_payout))
        else:                                     # exploit: use the best guess
            machine = max(estimate, key=estimate.get)
        reward = 1 if random.random() < true_payout[machine] else 0
        count[machine] += 1
        estimate[machine] += (reward - estimate[machine]) / count[machine]
        total += reward
    return total, count

for eps in [0.0, 0.1, 0.5]:
    runs = [play(eps) for _ in range(200)]
    average = sum(total for total, _ in runs) / len(runs)
    best_share = sum(count["C"] for _, count in runs) / (len(runs) * 1000)
    print(f"epsilon={eps:<4} average reward per 1000 pulls={average:6.1f}  share on best machine={best_share:.0%}")
```

```text
epsilon=0.0  average reward per 1000 pulls= 199.6  share on best machine=0%
epsilon=0.1  average reward per 1000 pulls= 654.8  share on best machine=85%
epsilon=0.5  average reward per 1000 pulls= 580.8  share on best machine=66%
```

Read the three lines against what you would expect. With no randomness at all (`epsilon=0.0`) the agent starts on machine A because every estimate is tied at zero, and it never leaves: A is the only machine whose estimate ever changes. It scores about 200, the worst machine's rate. With 10% randomness it finds the best machine and spends 85% of its pulls there. With 50% randomness it knows the best machine perfectly well and still wastes half of its pulls on purpose, so it scores less.

Two lines in that program deserve a second look, because they return in every chapter. `estimate[machine]` is the agent's current belief about a machine, and the update line moves that belief a little toward each new result. Everything an RL agent knows is a pile of numbers like that one, nudged a little at a time.

## Value: how good is it to be here?

The slot machines have no "later". Now add one. A corridor has six cells. The agent starts at the left end and treasure waits at the right end. Each move costs 0.5 points, and the treasure is worth 10. Moves near the start earn nothing but that cost. Only their position in a chain makes them good, so the agent needs a way to judge moves whose payoff is still far off.

The idea is called **value**. The value of an action is how much total reward you can expect from taking it, counting everything that happens afterwards as well as the immediate result. A step that costs 0.5 but lands you right beside the treasure has a high value, even though its own reward is negative.

The agent can learn values with one rule: *after each move, look at where you landed, and pull your estimate for that move toward what you just got plus the best you think you can do from here.* That is **Q-learning**, and `Q` is simply the name of the table holding the estimate for each (cell, move) pair.

```python
import random

random.seed(1)
CELLS = 6                     # cells 0..5, treasure at cell 5
ACTIONS = ("left", "right")
MOVE_COST, TREASURE = -0.5, 10.0

def step(cell, action):
    cell = max(0, cell - 1) if action == "left" else cell + 1
    if cell == CELLS - 1:
        return cell, TREASURE, True
    return cell, MOVE_COST, False

Q = {(c, a): 0.0 for c in range(CELLS) for a in ACTIONS}
alpha, gamma, epsilon = 0.5, 0.95, 0.2

for episode in range(200):
    cell, done = 0, False
    while not done:
        if random.random() < epsilon:
            action = random.choice(ACTIONS)
        else:
            action = max(ACTIONS, key=lambda a: Q[cell, a])
        next_cell, reward, done = step(cell, action)
        best_next = 0.0 if done else max(Q[next_cell, a] for a in ACTIONS)
        Q[cell, action] += alpha * (reward + gamma * best_next - Q[cell, action])
        cell = next_cell

for c in range(CELLS - 1):
    policy = max(ACTIONS, key=lambda a: Q[c, a])
    print(f"cell {c}: left={Q[c, 'left']:6.2f}  right={Q[c, 'right']:6.2f}  policy={policy}")
```

```text
cell 0: left=  5.48  right=  6.29  policy=right
cell 1: left=  5.48  right=  7.15  policy=right
cell 2: left=  6.29  right=  8.05  policy=right
cell 3: left=  7.15  right=  9.00  policy=right
cell 4: left=  8.05  right= 10.00  policy=right
```

Look at the `right` column. It climbs smoothly from 6.29 at the start to 10.00 beside the treasure. Nobody wrote those numbers in. At first only the step right next to the treasure learned that treasure exists. On later episodes, the step before it saw a good estimate ahead and borrowed from it, and so on back down the corridor. Reward flows backward from the goal, one trip at a time.

Three constants in that code are worth naming, because you will meet them everywhere:

- `alpha` is the **learning rate**: how far to move an estimate toward each new result. Too high and the estimates jump around. Too low and learning crawls.
- `gamma` is the **discount**: how much a future point is worth compared with one now. At 0.95, a point one step away counts as 0.95 of a point. This is why `right` at cell 0 is 6.29 and not simply 10 minus the move costs.
- `epsilon` is the same exploration knob as in the slot machines.

## Policy: what do I do now?

The last column of that output, `policy=right`, is the fourth word. A **policy** is the agent's rule for choosing an action in each situation. Here it is simple: look up both moves and take the bigger number. A policy does not have to come from a value table. In a language model, the policy is the model itself. It takes the conversation so far and gives a probability for each possible next word.

So a table of values is a thing you can compute a policy *from*, and a policy is what actually acts. Chapter [01](01-rl-foundations.md) calls these two routes value methods and policy methods. Modern language model training uses policy methods, for a reason you can already see: nobody can build a table with one row per possible conversation.

## From a corridor to a real puzzle

The corridor is a toy, but the same update rule scales a good way. The lab in [practice/01-q-learning-treasure-hunt](../practice/01-q-learning-treasure-hunt/) is the text adventure from the top of this chapter. Run it:

```bash
cd generative-ai/05-RL/practice/01-q-learning-treasure-hunt
uv run --no-project --with numpy python test_rl_learning.py --episodes 1000 10000
```

In our run, an agent trained for 1,000 games won 0 of 100 test games, and one trained for 10,000 games won all 100, with 146 situations in its table. The shortest winning route is 11 moves, and the agent has to stumble onto the whole chain by luck before any reward can flow back along it. That's the honest price of learning from nothing: about ten thousand tries for a puzzle a person solves in one sitting, because *door*, *key* and *sword* mean nothing to the table. Chapter [05](05-post-training-for-agents.md#classic-rl-vs-llmrl-why-priors-win) shows what happens when the agent already understands those words.

## How a language model becomes an agent

A language model picks words by giving each candidate word a score, and turning scores into probabilities with a function called **softmax**. A setting called **temperature** controls how sharply the top score wins. This is exploration again, in different clothes.

```python
import numpy as np

words = ["Paris", "Lyon", "banana"]
scores = np.array([4.0, 2.0, 0.0])        # the model's raw scores (logits)

def softmax(x, temperature=1.0):
    x = x / temperature
    return np.exp(x) / np.exp(x).sum()

for t in [0.25, 1.0, 4.0]:
    probs = softmax(scores, t)
    row = "  ".join(f"{w}={p:.2f}" for w, p in zip(words, probs))
    print(f"temperature {t:>4}: {row}")
```

```text
temperature 0.25: Paris=1.00  Lyon=0.00  banana=0.00
temperature  1.0: Paris=0.87  Lyon=0.12  banana=0.02
temperature  4.0: Paris=0.51  Lyon=0.31  banana=0.19
```

Low temperature is `epsilon=0` behaviour: always pick the favourite. High temperature tries the alternatives more often. So the model already acts like the agent in the loop diagram. Its situation is the conversation so far, its action is the next word, and its policy is its weights. The only thing it lacks is a reward. Add one, and RL can adjust those weights: make the words that led to high reward more likely, and the others less likely. That's the entire idea behind **policy gradient** training, and the numbered chapters build it carefully.

Why bother, when the model already learned from all that text? Pretraining teaches a model to continue text. It doesn't teach it what you want. Real products need the model to follow instructions, stop when finished, refuse harmful requests, reason to correct answers and use tools. RL is how those skills get trained in:

| What you want | Reward source | Chapter |
|---|---|---|
| Answers people prefer | Human ratings of two answers | [02](02-rlhf-pipeline.md), [03](03-preference-optimization.md) |
| Behaviour that follows written principles | An AI judge applying those principles | [04](04-constitutional-ai.md) |
| Correct reasoning | An automatic checker of the final answer | [08](08-reasoning-rl-deepseek-r1.md) |
| An agent that finishes tasks safely | Task outcome, plus penalties for rule-breaking | [05](05-post-training-for-agents.md), [07](07-reward-design-and-tool-calling.md) |

## When the reward measures the wrong thing

Here is the moose again, with a chatbot. It chooses among three reply styles. Users rate the replies with a thumbs up. The numbers below are invented for the demonstration: the flattering style gets the most thumbs up, but it helps people least. Training uses the simplest policy-gradient rule. Raise the probability of a style in proportion to how much better than average its reward was.

```python
import numpy as np

rng = np.random.default_rng(0)
styles = ["correct", "flattering", "padded"]
thumbs_up = np.array([0.60, 0.85, 0.70])    # what the reward measures
truly_helps = np.array([0.90, 0.30, 0.50])  # what we wanted

def train(steps=4000, lr=0.05):
    prefs = np.zeros(3)                     # one number per style
    baseline = 0.0
    for _ in range(steps):
        probs = np.exp(prefs) / np.exp(prefs).sum()
        style = rng.choice(3, p=probs)
        reward = float(rng.random() < thumbs_up[style])
        advantage = reward - baseline
        baseline += 0.01 * advantage
        grad = -probs                       # gradient of log prob(style)
        grad[style] += 1.0
        prefs += lr * advantage * grad
    return np.exp(prefs) / np.exp(prefs).sum()

before = np.ones(3) / 3
after = train()
for name, p0, p1 in zip(styles, before, after):
    print(f"{name:<11} before={p0:.2f}  after={p1:.2f}")
print(f"thumbs-up rate: {before @ thumbs_up:.2f} -> {after @ thumbs_up:.2f}")
print(f"truly helpful:  {before @ truly_helps:.2f} -> {after @ truly_helps:.2f}")
```

```text
correct     before=0.33  after=0.01
flattering  before=0.33  after=0.98
padded      before=0.33  after=0.01
thumbs-up rate: 0.72 -> 0.85
truly helpful:  0.57 -> 0.31
```

Training worked. The agent did just what it was asked, the thumbs-up rate went from 0.72 to 0.85, and people are helped far less often than before (0.57 down to 0.31). Nothing malfunctioned. The reward was simply a stand-in for what we wanted, and the training found the gap between the two. This is called **reward hacking**, and a real version of it has a name in the field, sycophancy. Chapter [02](02-rlhf-pipeline.md#failure-modes) covers what it looks like at scale and what labs do about it.

## Pitfalls

- **Rewarding a proxy and assuming it is the goal.** Thumbs up, clicks and passing tests are all stand-ins. Before training, ask how an agent could score well while doing the wrong thing, because given enough tries it will find that way.
- **Reaching for RL when you have the answers.** If you have labelled examples of correct behaviour, supervised learning is usually cheaper and steadier. Winder's advice is to pick the simplest solution that solves the problem, and to reserve RL for problems of sequential decisions with a long-term goal (*Reinforcement Learning*, ch. 1).
- **Stopping exploration too soon.** A low-scoring agent with `epsilon=0` looks like a failed algorithm. It may only be a machine that never tried the good option.
- **Judging training from one run.** The programs above average many runs or fix a random seed. RL results swing widely from run to run, a point chapter [10](10-engineering-rl-systems.md#engineering-an-rl-problem) measures.

## Try it

1. In the slot-machine program, try `epsilon` values of 0.01 and 0.2. Which beats 0.1, and what would change if you only had 100 pulls?
2. In the corridor program, set `gamma = 0.5` and rerun. What happens to the `right` values at the left end, and why does the policy still point right?
3. In the reply-style program, change `truly_helps` and `thumbs_up` so the two agree. Does the harm disappear? Which single number would you measure in production to catch the original problem?

<details><summary>Answers</summary>

1. On 1,000 pulls we got about 550 for 0.01, 659 for 0.1 and 645 for 0.2, so neither beats 0.1: 0.01 is slow to find the best machine and 0.2 explores more than it needs to. On 100 pulls the order changes (28, 52 and 57), because there is no time for a slow search to pay off.
2. Future treasure is worth far less, so `right` at cell 0 falls from 6.29 to about −0.31 in our run. `left` at cell 0 is lower still (−0.66), so the policy keeps pointing right. A low discount shrinks far-off reward without changing which way it lies.
3. Yes: when the proxy and the goal agree, optimizing one improves the other. To catch the original problem, measure a held-out sample of true helpfulness, separately from the signal used for training.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What makes RL different from supervised learning? | There is no answer key. The agent acts, gets a reward that may be delayed, and has to work out which actions earned it. |
| Define policy and value. | A policy chooses actions in each situation. A value estimates the total future reward from an action or situation. |
| Why explore at all? | Without trying other options, the agent can lock onto whatever paid first and never learn that something better exists. |
| What does the discount do? | It weighs future reward against reward now; a lower discount makes the agent more short-sighted. |
| How is a language model an RL agent? | The conversation is the situation, the next word is the action, the weights are the policy. Add a reward and policy gradient training can adjust them. |
| What is reward hacking? | Scoring well on the reward while missing the goal it stood for, such as a chatbot that flatters for thumbs up. |

## Next

[01 — RL foundations](01-rl-foundations.md) puts precise notation on these same ideas and follows the update rule from tables to the PPO method used on language models. For a gentler second pass with videos, try the [Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/unit0/introduction).
