# Real-Time Multimodal Agents: Voice, Computer Use, Robotics

> **Pillar:** [07-agentic-applications](README.md)
> **Presumes:** [03-agentic-foundations/agent-fundamentals.md](../03-agentic-foundations/agent-fundamentals.md)
> **Source:** Bojie Li, *AI Agents in Depth* (2026), ch. 9 — [book-en/chapter9.md](https://github.com/bojieli/ai-agent-book/blob/main/book-en/chapter9.md) (Apache-2.0)

Static image and document understanding is a solved part of normal agent work. This note covers the three settings where **real-time constraints** make multimodality hard: voice dialogue, GUI operation and robot control. Input arrives continuously and output has a strict time budget. All three are moving the same way: from **serial pipelines** toward **end-to-end models**, and toward a **fast/slow division of labor**. Image and video *generation* is out of scope. It is an ordinary tool call.

---

## Voice: three paradigms

The framing comes from OpenAI's GPT-Live launch (2026). It matches the three generations of ChatGPT Voice. All three coexist in production as trade-offs. A newer one doesn't simply replace an older one. One question separates them: **how far each gets from VAD's assumption that conversation happens in discrete turns.**

| Paradigm | Shape | Turn-taking | Examples |
|---|---|---|---|
| **Cascaded** | VAD → ASR → LLM → TTS, each a separate model | VAD guesses turns from silence | Most commercial assistants, the original ChatGPT Voice |
| **End-to-end omnimodal (Omni)** | One model listens, thinks and speaks | Still turn-based, still VAD-driven | gpt-realtime, Gemini Live, Qwen3-Omni, Step-Audio 2 |
| **Full-duplex / interactive** | Listens and speaks at the same time, deciding many times a second whether to speak, listen, stop, interrupt or call a tool | No turns at all | Moshi (2024), TML Interaction Model, GPT-Live (2026) |

### Paradigm 1: the cascaded pipeline

**The latency budget (fully serial, short reply, no reasoning):**

| Stage | Typical latency | Note |
|---|---|---|
| VAD end-of-speech | 500–800 ms | Silence threshold. Too short cuts users off mid-thought. Too long adds dead air |
| ASR (Whisper, SenseVoice) | 50–200 ms | 200–500 ms on constrained hardware. The LLM sits idle meanwhile |
| LLM TTFT | 100–500 ms | 5–10 s if reasoning is enabled |
| LLM first short segment | 100–300 ms | |
| TTS first segment | 200–500 ms | |
| **Total** | **≈ 0.95–2.3 s** | Above ~2 s, people get restless |

**Queueing makes it worse.** Total latency ≈ idle latency × 1/(1 − utilization). That is 2× at 50% load and 5× at 80%, which is why voice servers can't run hot.

**Full-chain streaming** keeps the modules but makes each one emit early:
- ASR transcribes while the user is still talking.
- The LLM streams and splits text into speech-ready chunks at punctuation.
- TTS synthesizes chunk by chunk.

What actually overlaps is limited. ASR overlaps the user's speech, and the rest of the LLM output overlaps TTS and playback. The three models don't all run at once on the same turn. **Speculative generation** goes further. It starts the LLM on a stable partial transcript, then cancels or corrects if the transcript changes, and holds playback until the turn is confirmed. Frameworks such as LiveKit Agents and Pipecat support it. You still have to implement commit, invalidation and rollback yourself; turning on a `stream` flag doesn't do it. No amount of streaming removes **the turn decision itself**.

### Streaming voice perception: replacing VAD + ASR

VAD + ASR has three built-in problems:
1. **Latency.** VAD can't predict the future. It can only wait for silence.
2. **Information loss.** VAD outputs one bit: voice or silence. Emotion, hesitation, background sound and the difference between "uh-huh" as acknowledgment and "uh-huh" as interruption are all gone.
3. **Accuracy.** Cutting audio into independent segments destroys context. In "john dot smith at gmail dot com", if "smith" lands in its own segment it can come out as "miss". In the book's Exp 9-3, "around two o'clock" became "around midnight".

**What "streaming" means technically:** a **causal or chunked encoder**, which needs only the audio that has already arrived, plus **incremental decoding**. Whisper can't stream. Its decoding is fine. The problem is that its encoder needs a full 30-second window. Streaming ASR itself is old: RNN-T and streaming Conformer power phone captions and keyboard dictation, with no LLM involved.

Two newer paths:
- **LLM-based streaming auditory perception.** An LLM backbone post-trained to consume a continuous audio stream directly. Examples: Ultravox, Qwen2-Audio, Qwen2.5-Omni. It sees the *whole* conversation, not VAD fragments. That enables in-context learning of names and terms, plus world-knowledge priors ("Apple" + "event" → the company). It emits **acoustic event tokens** alongside text: `<speak_start/end>` (a semantic plus acoustic judgment), `<interrupt>`, `<emotion:…>`, `<laugh>`, `<noise>`.
- **Turn detection inside the recognizer.** This is lighter. A LoRA on a small streaming ASR model weighs semantics and silence together. A silence threshold alone is guaranteed to fail both ways, because pauses *within* a turn (reciting a phone number) often run longer than gaps *between* turns. **The wavering came from the labels, not the architecture.** The labels had been annotated with audio from *after* the decision point, which the online model can never see. Re-labeling with only causal information fixed it: data over architecture again. Production versions: Deepgram Flux and AssemblyAI Universal-Streaming.

### Paradigm 2: end-to-end omnimodal (Omni)

**What it buys:**
- One model, so paralinguistics (emotion, prosody, ambient sound) can flow through the latent space instead of being squeezed into text.
- Lower latency.

**What it costs:**
- More training data.
- Worse interpretability and debuggability.

**End-to-end wins on latency, not necessarily on accuracy.** Compare **self-cascade**: the same model transcribes to structured text, then reasons over that. When the answer depends mainly on *what was said*, self-cascade matches or beats end-to-end, especially for models with weak perception. When it depends on *how it was said* (tone, emotion, environmental sound), end-to-end wins. You can **predict the winner from the task**. What matters is what information the bottleneck carries, not whether a bottleneck exists. Upgrade the intermediate text to include paralinguistic markers and the gap narrows.

**The models:**
- **gpt-realtime** is native audio but still uses server-side VAD. It adds barge-in and **asynchronous function calls**, so the model keeps talking while a tool runs.
- **Qwen3-Omni** splits into a Thinker (understanding and reasoning) and a Talker (speech), on MoE.
  - MoE raises **throughput** (less queueing). It does not lower **first-packet latency**.
  - First-packet latency, about 234 ms, comes from the Talker's multi-codebook autoregression plus a causal codec. Speech starts streaming as soon as the Thinker emits text.
- **Step-Audio 2** scores 83% on its own paralinguistic benchmark, against about 44% for GPT-4o Audio and Qwen2.5-Omni.

**The remaining flaw:** Omni still takes turns. A user pauses mid-number and Omni cuts in. Semantic turn detection only patches the turn framework. It doesn't remove it.

### Paradigm 3: full-duplex

Simultaneous interpretation and rhythm games have no turns at all. Full-duplex drops the turn assumption.

- **Moshi** (Kyutai, 2024) models two audio streams, the user's and its own, plus an "inner monologue" text stream. Overlap and interruption need no special logic. About 200 ms end to end.
- **TML Interaction Model** (Thinking Machines Lab, 2026). The argument: interactivity should live *inside* the model, not in a VAD harness around it. It works in **~200 ms micro-turns**, with audio, video and text interleaved. It can speak up unprompted ("that code has a bug"). TML-Interaction-Small is a 276B MoE with 12B active parameters, with a turn-switch latency of about 0.40 s against about 1.18 s for GPT-realtime-2.0. It is a research preview.
- **GPT-Live** (OpenAI, 2026) is full-duplex at 150M-user scale. It waits while the user thinks, backchannels ("mm-hmm") and translates live.

The arc: VAD guesses turns from silence → streaming perception guesses them from meaning → full-duplex has no turns, so barge-in handling largely disappears from the architecture.

---

## Thinking architectures: real-time vs. deep thought

Users want millisecond responses. Hard questions need seconds. Cascaded and end-to-end systems face this equally. Three solutions coexist. **Solutions 1 and 2 use two independent models and can sit on top of a cascade. Only Solution 3 internalizes reasoning.**

| | Fast model | Slow model | Failure |
|---|---|---|---|
| **1. Fast fillers, slow answers** | Says "let me think" or a quick answer within 500 ms | Answers fully after 5–10 s | **Overthinking** (repeats "Wednesday" ten seconds later). **Contradiction**: the fast model says "buy it", the slow one says "wait, it lacks roaming". Two independent minds with no coordination |
| **2. Fast interacts, slow advises** | Owns the conversation | Runs in the background, sees the fast model's output, and sends advice through a text channel such as the [Agent Status Bar](../../ai-engineering/02-context-engineering/notes/02-context-anatomy.md) | The fast model can misread advice ("reconfirm the price" taken as "ask the user"). It can't see the slow model's intermediate reasoning. It **can't think while speaking**: only fillers until the slow model reports |
| **3. Unified (Step-Audio R1)** | One model thinks *while* speaking | — | Must be both the best reasoner and a real-time speaker. Both are moving targets, so it needs repeated retraining |

**Solution 2 is the 2026 mainstream:** GPT-Live delegating to GPT-5.5, TML Interaction Models, Grok Voice "Think Fast" and Pine AI. The reason is pragmatic. Frontier reasoners change every few months, while interaction skills need specialized data. Keep the strongest reasoner intact in the background, train only a light foreground model, and you can always swap in the newest "brain". TML hands the background model the *entire conversation context*, not an isolated query, and streams results back to be woven in when the moment fits.

**Step-Audio R1** combines two mechanisms:
- **MGRD (Modality-Grounded Reasoning Distillation)** fixes **textual surrogate reasoning**. Audio models whose CoT data came from text models reason about transcripts ("the lyrics mention sadness") instead of sound ("minor key, falling pitch contour"). This is why longer CoT made them *worse*. The fix:
  1. Sample several reasoning traces.
  2. Keep only the traces that cite concrete acoustic features ("speech rate 40% faster, pitch sharper").
  3. Run SFT on those traces.
  4. Run RL to stop the model skipping the thinking.
  5. Iterate.
- **MPS (Mind-Paced Speaking)** is a dual brain. A **Formulation Brain** streams reasoning segments, and an **Articulation Brain** turns each segment, plus the reply so far, into speech. First syllable at about 350 ms.

| Config (Exp 9-4) | Spoken-MQA | URO-Bench |
|---|---|---|
| No thinking | 70.6% | 77.4 |
| MPS Speak-First (zero latency) | 92.8% | 82.5 |
| MPS Think-First (~80 tok latency) | 93.9% | 84.8 |
| Full think-before-speak | 93.0% | — |

Speak-First costs almost nothing, because the start of a CoT mostly restates the problem.

### The fast/slow interface: beyond text

Solution 2's channel is text: easy to debug, but narrow. The **Latent Bridge** (Li & Shi 2026, arXiv:2606.24470) freezes a fast reactor and a slow reasoner. It trains only a bridge of a few tens of millions of parameters, which projects the slow model's hidden state into a few **latent tokens** in the fast model's input, the way vision tokens are inserted. On Atari it beats the text channel by +26% to +82% in some games, for about 5 ms per step. **The limit:** fast/slow pays off only when the bottleneck is "can't think of it", not "can't react in time". Gains track how much better the slow model is (r ≈ 0.9). The same question returns for Computer Use and robotics: **when is a slow strategist worth the latency?**

---

## Speech synthesis: imperfection on purpose

Perfectly fluent TTS sounds machine-made. Human pauses and fillers signal thinking and uncertainty. **Let the LLM decide prosody** by emitting control tokens: `[THINKING]` (1–2 s pause plus "um…"), `[SEARCHING]`, `[EMO:happy]`, `[SPEED:0.8x]`, `[SIGH]`, `[LAUGH:small]`, `[BREATH]`. Only the LLM knows whether it is mid-hard-problem, whether the user is impatient, or whether this is small talk. TTS becomes a multimodal generator that takes text plus control tokens and returns audio.

There are two ways to build it:
- **Proprietary TTS** with native control tokens. Most flexible, but needs a dedicated team.
- **Voice cloning plus a reference library.** Takes weeks. Exp 9-5 uses 24 five-second clips covering emotion × speed × style on Fish Audio S1. The control tokens choose a clip, and timbre stays consistent. Compared with no control tokens (robotic) and a single clip (monotone), the multi-reference library sounds close to a human agent.

---

## Computer Use

The **perceive-think-act loop**:
1. Screenshot.
2. A multimodal model reads it and outputs a thought and an action.
3. Execute the action.
4. Wait, then screenshot again.

The design axes are the action space, visual grounding and the model.

**Action space (Anthropic's tools):**
- **`computer`:** mouse move, click, drag, down/up, scroll with modifiers; `type` (12 ms between keys), `key`, `hold_key`; screenshot, `cursor_position`, `wait`.
- **bash:** persistent session, 120 s timeout, completion detected with a sentinel string.
- **`str_replace_editor`:** view, create, replace, insert, undo. Safer than overwriting whole files.

See [03-tool-design](../../ai-engineering/03-harness-engineering/notes/03-tool-design.md). Each action cycle takes 2–5 s, much slower than a human.

**Visual grounding: three routes.**

| Route | How | Use when |
|---|---|---|
| **Set-of-Mark (visual)** | A segmentation model (SAM, SEEM) numbers regions. The model answers "click [7]" | No structure available: native desktop apps, games |
| **Structured element indexing** | Read the DOM or accessibility tree over CDP, number the interactive elements, draw boxes and send an element list (`browser-use`) | **Prefer this whenever structure exists.** Most accurate and stable. Doesn't save tokens |
| **Coordinate prediction** | The model outputs (x, y) directly (SeeClick, Claude computer use) | Canvas or WebGL, models trained for GUI grounding |

Labeling turns fill-in-the-blank into multiple choice. All three routes still struggle with small elements and dense screens.

**Resolution matters for coordinate prediction.** Claude was trained at XGA (1024×768), WXGA (1280×800) and FWXGA (1366×768). Pick the target by **aspect ratio**, scale the screenshot down, then map the coordinates back. Example: a 2560×1440 screen → FWXGA, and (683, 384) → (1280, 720). Squashing 16:9 into 4:3 shifts every prediction.

**Dynamic screens: the observation interface.** Screenshot loops assume a static screen. They miss videos, toasts and meeting audio. The **Agent–Computer Observation Interface** (Li & Shi 2026, arXiv:2606.29472) is middleware that needs no retraining. It has three parts:
1. Keyframe capture, gated by pixel diff and then a small model.
2. Speech transcription, gated by volume.
3. **One-sentence text narration of each captured frame**, which stays in memory after the image is evicted.

The text narration does most of the work, more than frame selection. Across eight models the gain was +17 to +48 points, largest on voice tasks. Too many image tokens hurt some newer models, so **choose components per model**.

**Mobile:**
- The action space is accessibility APIs plus gestures. The same (x, y) can be a tap, a long press or the start of a swipe. Benchmarked on AndroidWorld.
- The real blocker is **ecosystem**. Platforms make money from attention: ads, recommendations, impulse buys. An agent that goes straight to the goal skips all of that. It's a structural conflict of interest, not just CAPTCHAs.

**Efficiency is now the bottleneck.**
- OSWorld success has climbed from about 20% toward human level.
- **OSWorld-Human** shows agents take many more steps than humans. Per-step latency also *grows* as the context grows, so a tweak that takes a human seconds takes an agent minutes.
- There's no systematic fix yet. Agents can't predict their next action while the current one is still executing.

The workaround is **fast/slow decoupling** (Li & Shi, *Talking While Acting*). A fast voice model talks to the user while a slow VLM operates the browser. They share a **plain-text contract**, a rolling status line such as "filling the form, still need your date of birth". **The fast model must never say "done" until the status confirms it.** Voice responses got about 15× faster.

---

## Robotics

**Hardware isn't the bottleneck for vision-guided household tasks; algorithms are.** A sub-$1,000 dual-arm XLeRobot does a wide range of chores under VR teleoperation at 100–200 ms latency. The limit: touch sensing and dexterous hands are still real hardware gaps for force-sensitive work.

**Two layers** (planning vs. control, a different split from MPS's thinking vs. speaking):
- **Long-horizon planning (slow)** answers *what* to do. "Clean the kitchen" → clear the counter, load the dishwasher, wipe. Gemini Robotics-ER 1.5 is tuned for embodied reasoning: 62.8% across 15 spatial benchmarks, against 60.6% for GPT-4o. In Exp 9-9 it drives navigation at 0.5–1 Hz with three tools (forward, left, right). Its spatial reasoning is strong, but it is fragile over many steps.
- **VLA control (fast)** answers *how*. A VLA is a VLM plus action output, trained mainly by behavior cloning.
  - RL-trained VLAs do well on single tasks but generalize poorly. SimpleVLA-RL ([post-training note](../05-RL/post-training-for-agents.md)) trains one model per task.

**Action representations:**
- **Discrete tokens: RT-2 and OpenVLA.** Actions are binned into tokens and decoded like text. OpenVLA is the open version: Llama 2 plus a vision encoder, pretrained on Open X-Embodiment (20+ robots), then fine-tuned for each platform.
- **Continuous trajectories: π₀.** Flow matching denoises a smooth trajectory. Better for dexterous work. "Choosing from a menu vs. sketching the curve."
- **Action chunking (ACT, 2023)** bridges the frequency gap. Control loops run at 50–1000 Hz, and VLA inference at 1–10 Hz; the original OpenVLA ran at 6 Hz and moved jerkily. Generate 25–50 actions (0.5–1 s at 50 Hz) per inference. Replay them while the next chunk computes, like video buffering.
  - The trade-off: longer chunks are smoother but **blind to sudden changes**. The two-layer design relocates the real-time tension. It doesn't remove it.

**Sim2Real.** Domain randomization (see [06-eval environments](../../ai-engineering/06-eval/README.md)) plus two steps you can't skip:
1. **Calibrate the randomization range from measured real data.** Measure friction and motor delay. Too narrow misses reality. Too wide gives a policy that handles everything and masters nothing.
2. **Align visuals.** Match the camera pose between simulation and reality, and splice in real backgrounds (greenscreen).

Exp 9-10 shows the full pipeline: LeRobot + ManiSkill, RGB only, PPO to >90% in simulation, then a zero-shot grasp on a real SO100 arm. Success drops sharply on objects outside the training distribution.

---

## The common thread

| | Serial bottleneck | End-to-end move | Fast/slow split | Still open |
|---|---|---|---|---|
| **Voice** | VAD → ASR → LLM → TTS | Omni → full-duplex | Interaction model + background reasoner | Debuggability of end-to-end |
| **Computer Use** | Screenshot → think → click | — | Voice model + slow GUI agent | Per-step latency, continuous video |
| **Robotics** | Plan → act | VLA | Planner + VLA with action chunking | Cross-task generalization, data |

When the fast path acts before the slow path checks ("correct after misspeaking", "click first, then look", "step, then look"), **irreversible actions need a gate**. See [execution boundaries](../../ai-engineering/03-harness-engineering/notes/04-execution-boundaries.md).

---

## Labs

All ch. 9 labs need API keys, GPUs or hardware, so they are linked upstream, not copied.

| Exp | Lab | Needs |
|---|---|---|
| 9-1 | [live-audio](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/live-audio): cascaded voice chat, Silero VAD, pluggable ASR/LLM/TTS | Node + provider keys + mic |
| 9-2 | [phone-agent](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/phone-agent): ReAct agent with a `make_phone_call` tool over PineClaw Voice | PineClaw + LLM keys |
| 9-3 | [streaming-speech](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/streaming-speech): chunked "simulated streaming" ASR vs. a whole-utterance baseline | ASR API key |
| 9-4 | [end-to-end-speech](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/end-to-end-speech): end-to-end vs. cascade latency and paralinguistic loss (uses `gpt-audio` in place of Step-Audio R1) | OpenAI key |
| 9-5 | [controllable-tts](https://github.com/bojieli/ai-agent-book/tree/main/chapter9/controllable-tts): control-token parser + reference voice library | TTS key |
| 9-6 | [Anthropic computer-use demo](https://github.com/anthropics/claude-quickstarts/tree/main/computer-use-demo) | Docker + Anthropic key |
| 9-7 | [browser-use](https://github.com/browser-use/browser-use) with SoM visualization | Playwright + model key |
| 9-8 – 9-10 | [XLeRobot teleop](https://xlerobot.readthedocs.io/en/latest/software/getting_started/XLeRobot_teleop.html), [LLM agent control](https://xlerobot.readthedocs.io/en/latest/software/getting_started/LLM_agent.html), [LeRobot sim2real](https://github.com/StoneT2000/lerobot-sim2real/blob/main/docs/zero_shot_rgb_sim2real.md) | GPU for sim. Real arm to deploy |

---

## Interview questions

- **Why does a voice agent feel slow even when the LLM is fast?** The serial sum (VAD silence wait + ASR + TTFT + TTS ≈ 1–2 s), multiplied by queueing at load. Fix it with streaming, speculative generation, semantic turn detection or full-duplex.
- **End-to-end or cascade for a support line that must capture order numbers exactly?** Content-determined, so a (self-)cascade with structured transcripts is as accurate and debuggable. Go end-to-end when tone and emotion drive the outcome.
- **How do you add deep reasoning without adding latency?** Use a fast foreground model with a background reasoner on a text or status channel. Hand it the full context, never let the fast model claim completion early, and resolve contradictions in favor of the slow model *before* speaking.
- **How do you observe an end-to-end voice model?** Log the input audio, the event tokens and the inner-monologue or text stream. Run self-cascade replays to localize errors to perception vs. reasoning.
- **DOM indexing or pure vision for Computer Use?** Index when structure exists, fall back to SoM or coordinates on canvas, and keep both paths. Pick the route per model.
- **Action chunking vs. sudden change?** Use shorter chunks near contact, re-plan on visual anomaly triggers, and blend overlapping chunks.

---

## Cross-links

- **Upstream:** [03-agentic-foundations/agent-fundamentals.md](../03-agentic-foundations/agent-fundamentals.md) (the ReAct loop these systems extend), [05-RL/post-training-for-agents.md](../05-RL/post-training-for-agents.md) (voice SFT, SimpleVLA-RL, data > architecture)
- **Lateral:** [harness tool design](../../ai-engineering/03-harness-engineering/notes/03-tool-design.md) (the computer/bash/editor action space), [context anatomy](../../ai-engineering/02-context-engineering/notes/02-context-anatomy.md) (Agent Status Bar as the fast/slow channel), [orchestration](../../ai-engineering/03-harness-engineering/notes/07-orchestration.md) (fast/slow as a two-agent pattern)
- **Downstream:** [ai-engineering/06-eval](../../ai-engineering/06-eval/README.md) (OSWorld, AndroidWorld, simulation environments)
