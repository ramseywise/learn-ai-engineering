# Pillar 2 — LLM Fundamentals (transformers → training → prompting)

How large language models actually work: tokens, attention, the training pipeline
(pretraining → SFT → preference alignment), and how to talk to them. This is the pillar
where you build a tiny GPT with your own hands — after that, nothing about LLMs is magic.

## Learning path

1. **Build it from scratch** — `generative-ai/nn-zero-to-hero/` (Karpathy's nanogpt):
   backprop → bigrams → attention → a working GPT. The single highest-value exercise in
   this repo.
2. **Read the two founding papers** — *Attention Is All You Need* + BERT (`ai-engineering/readings/general/`)
   once the code has made the diagrams familiar.
3. **The training story** — InstructGPT (RLHF), DPO, Constitutional AI papers
   (`generative-ai/01-llm-fundamentals/readings/`); for RL depth: the *Reinforcement Learning* book chapters +
   Sutton & Barto (`RLbook2020.pdf`, same folder).
4. **Prompting as engineering** — *Prompt Engineering for Generative AI* chapters
   (`generative-ai/01-llm-fundamentals/readings/`): principles, LangChain techniques, agents-with-tools.
5. **Reasoning patterns** — CoT, ReAct, Reflexion, Tree of Thoughts papers
   (`generative-ai/01-llm-fundamentals/readings/` + `ai-engineering/readings/general/`) — these bridge into the agents pillar.
6. **NLP context** — `generative-ai/intro-to-nlp/` for the pre-transformer lineage
   (word2vec `1301.3781`, Bengio's neural LM in `ai-engineering/readings/general/`).

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| nn-zero-to-hero (nanogpt) | code | `generative-ai/nn-zero-to-hero/` | transformers from scratch |
| intro-to-nlp | code | `generative-ai/intro-to-nlp/` | embeddings, classic NLP |
| Attention Is All You Need · BERT · LLaMA · GPT-4 report · LLM survey (2303.18223) | pdf | `ai-engineering/readings/general/` | architecture + scaling canon |
| ALiBi (2108.12409) | pdf | `ai-engineering/readings/general/` | positional encoding for long context |
| InstructGPT (2203.02155) · DPO (2305.18290) · Constitutional AI (2212.08073) · preference RL (1706.03741) | pdf | `generative-ai/01-llm-fundamentals/readings/` | the alignment pipeline |
| *Reinforcement Learning* (book chs 1–11) + Sutton & Barto | pdf | `generative-ai/01-llm-fundamentals/readings/` | MDPs → DQN (1312.5602) → policy gradients (PPO 1707.06347) |
| CoT (2201.11903) · ReAct · Reflexion · Tree of Thoughts | pdf | `generative-ai/01-llm-fundamentals/readings/` | reasoning/agent patterns |
| *Prompt Engineering for Generative AI* (chs 1–10) | pdf | `generative-ai/01-llm-fundamentals/readings/` | prompting principles → AI-powered apps |
| *LLM from Scratch* · *LLM Handbook* | pdf | `generative-ai/01-llm-fundamentals/llm from scratch/`, `generative-ai/01-llm-fundamentals/llm handbook/` | book-length builds/reference |
| DPO · Chain of Thought · Self-Learning Agents | wiki | librarian | compiled distillations |
| rl.md · agents-self-training.md | note | [../../notes/](../../notes/) | RL/MARL + Agent-Lightning (confidence: low/medium) |

## Test yourself
[interview-guide.md](interview-guide.md) · rounds:
[technical-questions](../../rounds/technical-questions/README.md) (this pillar is its core).
