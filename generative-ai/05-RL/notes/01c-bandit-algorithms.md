---
origin: curated  # split from 01-rl-foundations.md and 01b-algorithm-families-td-and-dqn.md (2026-11-08) so each part stays under the chapter length cap
confidence: medium
sources:
  - "Lattimore & Szepesvári, \"Bandit Algorithms\" (Cambridge University Press, 2020), ch. 1, 4, 6–13, 15–23"
  - "Sutton & Barto, \"Reinforcement Learning: An Introduction\" (2nd ed., MIT Press, 2018), ch. 2"
  - https://arxiv.org/abs/2412.05265 (Murphy, RL overview, 2024 preprint, ch. 7)
  - https://doi.org/10.1137/s0097539701398375 (Auer et al., Exp3, SIAM J. Comput. 2002)
  - https://arxiv.org/abs/1003.0146
  - https://arxiv.org/abs/1802.09127
  - https://arxiv.org/abs/1508.03326
cleaned: 2026-11-08
---

# 1c — Bandits: regret, confidence bounds and Exp3

A bandit is the one-state case of the problem in [01](01-rl-foundations.md): no transitions, only a choice of arm and a reward. It isolates exploration, which [01](01-rl-foundations.md#exploration-vs-exploitation) treats in a paragraph, and it is where regret, the cost of not knowing, is best understood. This note holds the guarantees: the testbed numbers, regret for explore-then-commit, UCB and its variants, Exp3 for adversarial rewards, the lower bounds, and contextual and linear bandits. Thompson sampling with no context is in [DA 04/03](../../../data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits.md#bayesian-bandits-thompson-sampling).

## Stochastic bandits and regret

- **Measured on the 10-armed testbed** (2,000 random problems, rewards N(q*, 1), 1,000 steps): greedy gets about 1 reward per step against 1.54 possible; ε = 0.1 never exceeds 91% optimal actions; optimistic initial values (Q₁ = +5, α = 0.1) start worse than ε-greedy and end better, but only help stationary problems; UCB with c = 2 beats ε = 0.1 after the first k steps (`A = argmax[Q(a) + c·√(ln t / N(a))]`); a gradient bandit with a baseline is unaffected when every mean shifts by +4, and without the baseline degrades. The gradient bandit's expected update equals the gradient of expected reward, so it is stochastic gradient ascent and the direct ancestor of [REINFORCE](01-rl-foundations.md#policy-gradients-from-reinforce-to-the-ppo-clip), with the baseline only reducing variance. Across a parameter sweep from 1/128 to 4, every method traces an inverted U, and UCB comes out best on this problem (*RL: An Introduction*, ch. 2). Exact Bayesian lookahead over 1,000 two-action steps has 2^2000 leaves, which is why Thompson sampling is used instead.
- **Regret and the noisy TV (Murphy, ch. 7).** Regret measures return lost against the best policy in hindsight. For a tabular episodic MDP with horizon H, S states, A actions and T steps, the optimal minimax regret is O(√(HSAT)) (*RL: A Comprehensive Overview*, ch. 7, Sec. 7.1). Exact Bayes-optimal planning merges identical belief states, yet a bandit with n arms and horizon h still has O(h^2n) of them (about 10^12 for the two-arm, 1,000-step case above), and Gittins indices solve only the infinite-horizon discounted, context-free case (Sec. 7.2.1). Posterior sampling is the cheap alternative: sample one model from the posterior each episode and act greedily on it. Prompting an LLM to do this worked on 3-state RiverSwim and failed at 4 states (as reported, Sec. 7.2.2). Rewarding raw prediction error as intrinsic motivation invites the *noisy TV* problem, an agent that stares at unpredictable noise, while information gain, ICM or a KL reward avoid it (Sec. 7.4).
- **Regret guarantees (Lattimore & Szepesvári).** Regret is R_n = nμ* − E[ΣX_t], which equals Σ_i Δ_i·E[T_i(n)], the gap times the expected pull count of each arm (*Bandit Algorithms*, ch. 4, Lemma 4.5). Bounds below assume k arms, horizon n and 1-subgaussian rewards unless stated.
  - *Explore-then-commit* on two arms with gap Δ, tuned to Δ: R_n ≤ min{nΔ, Δ + (4/Δ)(1 + max{0, log(nΔ²/4)})}. A commit time chosen from n alone gives only O(n^(2/3)) (ch. 6, Eq. 6.6, Exercise 6.5).
  - *UCB* with confidence δ = 1/n²: R_n ≤ 3ΣΔ_i + Σ 16 log n/Δ_i, and gap-free 8√(nk log n) + 3ΣΔ_i. It needs n in advance (ch. 7). The anytime variant: limsup R_n/log n ≤ Σ 2/Δ_i (ch. 8). MOSS drops the log factor, 39√(kn) + ΣΔ_i (ch. 9, Thm 9.1). For Bernoulli rewards KL-UCB has limsup R_n/log n ≤ ΣΔ_i/d(μ_i, μ*) and is never worse than UCB, since d ≥ 2Δ² (ch. 10, Thm 10.6).
  - *Adversarial rewards in [0,1]:* Exp3 with η = √(2 log k/(nk)) gets R_n ≤ √(2nk log k) in expectation, yet its regret is heavy-tailed: some bandit has P(regret ≥ n/4) > 1/131 (ch. 11, Thm 11.2, Note 1). Exp3-IX biases the estimator upward, so with probability 1−δ the regret is O(√(nk log(k/δ))) (ch. 12). In the book's k = 5, n = 10⁴ run its *expected* regret is higher than Exp3's (Fig. 12.1).
  - *Floors.* Any policy has some Gaussian instance with R_n ≥ (1/27)√((k−1)n) once n ≥ k−1 (ch. 15, Thm 15.2, sketched in ch. 13). A policy consistent on an unstructured class has liminf R_n/log n ≥ Σ Δ_i/d_inf; for unit-variance Gaussians that is Σ 2/Δ_i, so the UCB asymptotics above are tight (ch. 16, Thm 16.2 and Table 16.1; the 2/Δ form is our substitution). Beating that line on one instance costs regret elsewhere (Fig. 16.1). Expected regret ≤ B√((k−1)n) also forces a tail: some Gaussian instance has regret ≥ ¼·min{n, (1/B)·√((k−1)n)·log(1/(4δ))} with probability ≥ δ (ch. 17, Thm 17.1).

![Regret against difficulty for several policies. A horizontal line marks the minimax floor of order √n, and a rising line marks the instance-optimal floor. An over-specialised policy sits at n almost everywhere and dips far below the instance line on one instance.](../sources/images/bandit-algorithms-fig16-1.png)
*Image Source: Lattimore & Szepesvári, *Bandit Algorithms* (Cambridge University Press, 2020), Fig. 16.1. Schematic.*

![Regret of Exp3 (dotted) and Exp3-IX (solid) against the gap Δ on a 5-armed Bernoulli bandit with n = 10,000. Both curves peak near Δ = 0.1, at about 258 for Exp3 and 302 for Exp3-IX, and fall to about 215 and 221 at Δ = 0.5.](../sources/images/bandit-algorithms-fig12-1.png)
*Image Source: Lattimore & Szepesvári, *Bandit Algorithms* (Cambridge University Press, 2020), Fig. 12.1.*

## Adversarial bandits and Exp3

The UCB and Thompson rules above assume each arm pays from a fixed distribution. **Exp3** ([Auer, Cesa-Bianchi, Freund & Schapire, SIAM J. Comput. 2002](https://doi.org/10.1137/s0097539701398375), from a FOCS 1995 abstract) drops that assumption: rewards in [0, 1] may be chosen by an adversary in advance, and the goal is to lose little against the best single arm in hindsight (*weak regret*). The paper has no experiments, only proofs.

![Pseudo-code box for Exp3: initialise every weight to 1; each round set each arm's probability to a mix of its normalised weight and gamma over K, draw an arm, observe a reward in [0,1], set the estimate to the reward over the arm's probability for the pulled arm and zero otherwise, then multiply each weight by exp of gamma times its estimate over K.](../sources/images/auer-2002-exp3-fig1.png)
*Image Source: Auer et al., [The Nonstochastic Multiarmed Bandit Problem](https://doi.org/10.1137/s0097539701398375) (SIAM J. Comput., 2002), Fig. 1*

The estimator is the importance weighting from [the Monte Carlo section](01b-algorithm-families-td-and-dqn.md#monte-carlo-control-and-importance-sampling). Only the pulled arm's reward is seen, so it is divided by the probability of having pulled it, which makes the estimate unbiased for every arm, pulled or not. The γ/K of uniform exploration keeps every probability above γ/K, which bounds the estimate by K/γ and stops an early run of low rewards from freezing an arm out.

- **Bound.** For any γ in (0, 1] and any horizon, G_max − E[G_Exp3] ≤ (e − 1)·γ·G_max + K ln K/γ (Thm 3.1). With a known g ≥ G_max and γ = min{1, √(K ln K/((e − 1)g))} the regret is at most 2.63·√(g·K ln K) (Cor. 3.2); with g = T, that is O(√(T·K ln K)). The adversary is oblivious, and the extension to adaptive adversaries is asserted and left to the reader (Sec. 9). The regret guarantees above state the textbook form of the same bound, in an η parameterisation.
- **Floor.** For any algorithm there is a reward distribution (one random arm pays Bernoulli(1/2 + ε), the rest Bernoulli(1/2), ε = ¼·min{√(K/T), 1}) with expected weak regret at least (1/20)·min{√(KT), T} (Thm 5.1). The √(ln K) gap to the upper bound is left open. It does not contradict the O(ln T) rates of stochastic bandits, because there the distributions stay fixed as T grows and here they depend on K and T.
- **Variants.** Plain Exp3 needs g or T. Exp3.1 restarts it in epochs of growing g and needs neither, at 8√(e − 1)·√(G_max·K ln K) + 8(e − 1)K + 2K ln K (Thm 4.1). The paper gives no high-probability bound for Exp3 itself, since the estimate's variance can reach 1/p, and argues informally that its regret could be as large as T^(3/4). Exp3.P adds a confidence bonus to each estimate and then holds with probability ≥ 1 − δ, but only for a known T (Thm 6.3). Exp4 takes advice from N experts and pays K ln N/γ, so the cost is logarithmic in N (Thm 7.1). Exp3.S shares weight among arms to track a sequence with H − 1 switches, at about H·√(KT ln(KT)) (Cor. 8.2).

## Contextual and linear bandits

**Contextual bandits** are the one-step case: observe a context, pick an action, get a
reward, with no state carried forward. It is the right model for recommendation, routing and
prompt or model selection. See [Bayesian bandits](../../../data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits.md#bayesian-bandits-thompson-sampling) in data
analytics for the case with no context, and for Thompson sampling. Two results anchor it:

- **LinUCB** ([arXiv:1003.0146](https://arxiv.org/abs/1003.0146), Li et al., 2010) fits a
  ridge regression per arm and picks the arm with the highest upper confidence bound. On over
  33M events from the Yahoo! front-page news module it got a 12.5% click lift over a
  context-free bandit. The paper's other lasting contribution is **replay evaluation**: a
  bandit policy can be scored offline, without bias, on logs collected under a uniformly
  random policy.
- **Thompson sampling with neural nets** ([arXiv:1802.09127](https://arxiv.org/abs/1802.09127),
  Riquelme et al., 2018) benchmarked approximate Bayesian deep nets as posteriors. Many methods
  that work in supervised learning did poorly here because their uncertainty estimates converge
  too slowly for online decisions. The robust choice was **NeuralLinear**: a network learns a
  representation, and an exact Bayesian linear regression on its last layer supplies the
  uncertainty.

- **Linear and expert-advised bandits (Lattimore & Szepesvári).** With a known feature map and 1-subgaussian noise, LinUCB keeps a ridge estimate and a confidence ellipsoid. If θ* stays inside it with probability 1−δ, the regret is at most √(8·n·β_n·log(det V_n/det V_0)) (ch. 19, Thm 19.2), which is O(d√n·log(nL)) for δ = 1/n (Cor. 19.3). In the book's d = 5, n = 5,000 sphere run LinUCB's regret stays under 500 as the arm count k grows to 1,000, while UCB's climbs to about 4,000 (Fig. 19.1). For adversarial contexts, Exp4 over M experts gets √(2nk log M), with oblivious experts and known n. A finite policy class Φ gives √(2nk log|Φ|), against 2√(nk|C|log k) for one Exp3 per context (ch. 18, Thm 18.1).

![Expected regret of UCB (solid) and LinUCB (dotted). Left: a 2-armed Gaussian bandit, n = 1,000, against the gap, where UCB is lower. Right: a linear bandit with d = 5, n = 5,000 against the number of arms k, where LinUCB stays under 500 and UCB climbs to about 4,000.](../sources/images/bandit-algorithms-fig19-1.png)
*Image Source: Lattimore & Szepesvári, *Bandit Algorithms* (Cambridge University Press, 2020), Fig. 19.1.*

Zhou's survey ([arXiv:1508.03326](https://arxiv.org/abs/1508.03326)) covers the wider family:
stochastic vs adversarial rewards, and UCB vs Thompson variants.

### Confidence sets, designs and sparsity for linear bandits

- **The confidence ellipsoid, and what it costs.** LinUCB's set comes from penalised least squares, θ̂_t = V_t(λ)⁻¹ΣA_sX_s with V_t(λ) = λI + ΣA_sA_sᵀ. A covering argument works for a fixed design (radius of order √(d log 6 + log 1/δ)) but fails in a bandit, where V_t is random. The method of mixtures replaces the covering with a Gaussian integral, and gives a set that holds for all t at once: with probability ≥ 1−δ, ‖θ̂_t − θ*‖_{V_t(λ)} < √λ‖θ*‖₂ + √(2 log(1/δ) + log(det V_t(λ)/λ^d)). With λ = 1 and ‖A_t‖ ≤ L the radius is m₂ + √(2 log(1/δ) + d log(1 + nL²/d)), the fixed-design rate up to a √(log n) factor. The √d is unavoidable, and the book advises using the log-determinant form inside an algorithm and the trace form only to state bounds. Its method of mixtures is said to improve a lot on covering in practice (*Bandit Algorithms*, ch. 20, Thm 20.5, Notes 1–3; the proof is theory only, with no experiment).
- **Designing the exploration.** For a fixed action set, choose a distribution π on the arms that minimises g(π) = max_a ‖a‖²_{V(π)⁻¹}. The Kiefer–Wolfowitz theorem says the minimum is d, equal to the log-det maximiser, with a support of at most d(d+1)/2 arms. Playing each arm n_a = 2π(a)g(π)·log(1/δ)/ε² times makes every confidence width at most ε with probability 1−δ, in about 2d·log(1/δ)/ε² rounds. An approximate design with g ≤ (1+ε)g* costs only a (1+ε)^½ factor in regret, and Frank–Wolfe, which moves weight toward argmax_a ‖a‖²_{V(π_k)⁻¹}, finds one in O(d log log|A| + d/ε) steps from a uniform start (*Bandit Algorithms*, ch. 21, Thm 21.1 and Eq. 21.3). The geometry is John's ellipsoid: the support sits on the boundary of the smallest centred ellipsoid containing the arms.
- **Phased elimination for k arms (Algorithm 12).** In phase ℓ set ε_ℓ = 2^(−ℓ), play each surviving arm T_ℓ(a) = (2dπ_ℓ(a)/ε_ℓ²)·log(kℓ(ℓ+1)/δ) times with π_ℓ the design on the survivors, compute θ̂_ℓ from that phase's data only, and keep the arms with max_b⟨θ̂_ℓ, b−a⟩ ≤ 2ε_ℓ. Because each phase's actions depend only on earlier phases, the fixed-design bound applies, and the regret is O(√(dn log(nk))), a factor √d better than LinUCB for moderate k. It needs a fixed finite action set, tolerates a misspecification of size ε at an extra nε√d·log n, and the book calls the changing-set variants (SupLinUCB) less practical than LinUCB or Thompson sampling (ch. 22, Thm 22.1 and Notes 2–3).
- **Sparsity.** If θ has few non-zeros, the ambient d need not enter. On the hypercube [−1,1]^d, selective explore-then-commit stops exploring each coordinate once its interval excludes zero and gets R_n ≤ 3‖θ‖₁ + C·Σ_{i:θ_i≠0} log n/|θ_i|, and in the worst case 3‖θ‖₁ + C′‖θ‖₀·√(n log n), without knowing ‖θ‖₀ (ch. 23, Thm 23.2; it needs n in advance). For general action sets, OLR-UCB converts any online sparse regression regret bound into a confidence set, with expected regret of about √(d·n·m₀) up to log factors for ‖θ‖₀ ≤ m₀. The sparse predictor behind it is not computationally efficient, m₀ must be known, and the dependence on d remains (Thm 23.6, Note 1; the exact final bound is garbled in our copy of the text, so the form is ours). Even a 2-sparse problem cannot beat √(dn), since a d-armed bandit is a linear bandit on the unit vectors.

## Pitfalls

- **Quoting a regret rate without its setup.** The bounds above assume k arms, horizon n and 1-subgaussian rewards; a rate for one reward class says nothing about another.

## Try it

1. A 2-armed Gaussian bandit has gap Δ = 0.2 and n = 10,000. Evaluate the explore-then-commit bound with the commit time tuned to Δ, and compare with nΔ.

<details><summary>Answers</summary>

1. Δ + (4/Δ)(1 + log(nΔ²/4)) = 0.2 + 20·(1 + log 100) = 0.2 + 20·5.605 = 112.3, against nΔ = 2,000.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| What is regret? | The reward lost against always pulling the best arm, which equals the sum over arms of the gap times the expected pull count. |

---

## Next

[01](01-rl-foundations.md#policy-gradients-from-reinforce-to-the-ppo-clip) goes on to policy gradients, the actor half of the actor-critic split from [01b](01b-algorithm-families-td-and-dqn.md). [02 — RLHF pipeline](02-rlhf-pipeline.md) applies them to language models.
