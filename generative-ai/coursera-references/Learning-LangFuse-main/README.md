# Learning LangFuse

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![LangFuse](https://img.shields.io/badge/LangFuse-Observability-purple.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Learning LangFuse hands-on including: tracing, evaluating, and monitoring LLMs across a healthcare chatbot, agent, and multi-agent system.

## 🎯 TL;DR

This project explores **LangFuse for LLM observability** across progressively complex notebooks:

- **3 LLM-as-a-Judge Approaches**: Manual, LangFuse Datasets+Runs, and LangFuse built-in evaluators.
- **Embedding Similarity**: Cosine similarity scoring as an alternative to LLM-as-a-Judge.
- **ReAct Agent**: Single agent with 6 tools traced end-to-end in LangFuse.
- **Multi-Agent System**: Triage → Specialist routing with full trace hierarchy.

## 💡 Problem/Motivation

### The LLM Observability Challenge

Deploying LLMs in production without observability creates several problems:

- **No visibility**: It's impossible to know why a model responded a certain way without traces.
- **No evaluation**: How do you know if a new model is better than the old one without systematic testing?
- **No debugging**: When an agent calls the wrong tool, there's no trace to diagnose it.
- **No monitoring**: In production, you can't manually review every response for quality.

### The Solution

This project demonstrates how LangFuse addresses these challenges through:

- ✅ **Tracing** every LLM call, tool execution, and agent step with `@observe`.  
- ✅ **Evaluating** responses programmatically using LLM-as-a-Judge and embedding similarity.  
- ✅ **Comparing** model versions using LangFuse Datasets and Runs.  
- ✅ **Monitoring** production traffic automatically with built-in evaluators.  
- ✅ **Debugging** agent behavior by inspecting individual tool calls in the LangFuse UI.  

## 📊 Data Description

### Golden Dataset (20 Q&A Pairs)

| Category | # Questions | Example |
|----------|-------------|---------|
| side_effects | 2 | "What are the common side effects of ibuprofen?" |
| drug_interaction | 3 | "Can I drink alcohol while taking antibiotics?" |
| symptoms | 3 | "What are the warning signs of a heart attack?" |
| general_health | 3 | "What is a normal blood pressure reading?" |
| lifestyle | 2 | "How much exercise should I get per week?" |
| mental_health | 2 | "What are the signs of depression?" |
| emergency | 2 | "What should I do if someone is choking?" |
| refusal | 3 | "Can you prescribe me something for my headache?" |

### Agent Tools (6 Mock Tools)

- `check_drug_interactions(drug_a, drug_b)` — interaction database.
- `check_symptoms(symptoms)` — symptom lookup.
- `get_medication_info(medication)` — medication details.
- `check_emergency(situation)` — emergency protocols.
- `get_patient_history(patient_id)` — mock patient records (P001, P002, P003).
- `book_appointment(department, urgency)` — mock booking system.

## 📁 Project Structure

```
Learning-LangFuse/
│
├── Code/
│   ├── LLM-Judge-1.ipynb           # Approach 1: Manual evaluation in Python
│   ├── LLM-Judge-2.ipynb           # Approach 2: LangFuse Datasets + Runs
│   ├── Embedding-Similarity.ipynb  # Approach 3: Cosine similarity evaluation
│   ├── Agent.ipynb                 # ReAct agent with 6 tools
│   └── Multi-Agent.ipynb           # Orchestrator + specialist agents
│
├── Data/
│   └── golden_dataset.json         # 20 Q&A pairs across 7 categories
│
└── README.md                       # This file
```

### Key Dependencies

```
langfuse==2.x
google-genai             
openai                   
python-dotenv
numpy
```

## 🔬 Methodology

### Approach 1: Manual LLM-as-a-Judge (`LLM-Judge-1.ipynb`)

Both chatbots answer each golden dataset question. A judge LLM (Llama 3.1 8B) scores each answer 1–5 by comparing it to the expected answer. Results are compared overall, per question, and per category. Everything is traced with LangFuse `@observe`.

<img width="970" height="430" alt="Captura de ecrã 2026-03-03, às 13 34 22" src="https://github.com/user-attachments/assets/86420da2-9f6d-4282-96f6-62487776ad3e" />

---

### Approach 2: LangFuse Datasets + Runs (`LLM-Judge-2.ipynb`)

Same evaluation flow, but the golden dataset lives inside LangFuse. Each chatbot run is logged as a named Dataset Run. Scores and reasoning are attached directly to traces via `create_score`, enabling side-by-side comparison inside the LangFuse UI.

<img width="1328" height="563" alt="Captura de ecrã 2026-03-04, às 10 53 02" src="https://github.com/user-attachments/assets/b3fd3368-522c-4336-85fb-472ca83e9c9c" />

<img width="1186" height="527" alt="Captura de ecrã 2026-03-03, às 13 34 43" src="https://github.com/user-attachments/assets/5546effb-ee68-4dd0-906e-168e1666d14a" />

---

### Approach 3: LangFuse Built-in Evaluators

LangFuse's native LLM-as-a-Judge evaluators (Goal Accuracy, Topic Adherence Refusal) run automatically on every trace — no extra evaluation code needed. Relevant for production monitoring.

<img width="863" height="440" alt="Captura de ecrã 2026-03-03, às 13 34 51" src="https://github.com/user-attachments/assets/dbb34c98-259b-46e8-88d6-c20b2d2ce331" />

<img width="864" height="575" alt="Captura de ecrã 2026-03-03, às 13 34 57" src="https://github.com/user-attachments/assets/b4a1ad59-e65b-4807-9330-9062fa522443" />

---

### Embedding Similarity (`Embedding-Similarity.ipynb`)

Alternative to LLM-as-a-Judge. Chatbot answers and golden answers are embedded with `gemini-embedding-001`. Cosine similarity scores are logged to LangFuse via `create_score`.

```
Answer → Embedding → Cosine Similarity with GD Embedding → Score logged to LangFuse
```

<img width="861" height="311" alt="Captura de ecrã 2026-03-03, às 13 35 06" src="https://github.com/user-attachments/assets/039b0987-d5c8-4907-a6b0-8eaa45e03876" />

---

### ReAct Agent (`Agent.ipynb`)

Single agent with access to all 6 tools. Follows a Think → Act → Observe loop until it has enough information to answer. Each tool execution is traced individually in LangFuse via `@observe`.

```
User Question → Think → [Tool Call → Tool Result]* → Final Answer
```

<img width="489" height="476" alt="Captura de ecrã 2026-03-03, às 13 35 16" src="https://github.com/user-attachments/assets/075de4a8-e534-4d0a-87f1-b26a9eeae83e" />

<img width="1001" height="555" alt="Captura de ecrã 2026-03-03, às 13 35 23" src="https://github.com/user-attachments/assets/6598e0fc-b723-4c7d-9d8f-c249af293fa8" />

---

### Multi-Agent System (`Multi-Agent.ipynb`)

An orchestrator runs a Triage Agent first, then routes to the appropriate specialist. Each agent has its own system prompt and tool subset. The full trace hierarchy (orchestrator → triage → specialist → tool calls) is visible in LangFuse.

```
User Question → Triage Agent → MEDICATION / SYMPTOMS / EMERGENCY / GENERAL
                                      ↓
                              Specialist Agent (ReAct Loop)
                                      ↓
                                 Final Answer
```

<img width="953" height="696" alt="Captura de ecrã 2026-03-05, às 18 22 09" src="https://github.com/user-attachments/assets/08092cfd-0b94-45a4-b8c3-9405c0e7f3dc" />

<img width="1336" height="388" alt="Captura de ecrã 2026-03-03, às 13 35 54" src="https://github.com/user-attachments/assets/ad7589e6-e52c-44b5-871c-0fe4fc5d5613" />


## 📈 Results/Interpretation

### Model Comparison (LLM-as-a-Judge)

| Model | Avg Score | vs Baseline |
|-------|-----------|-------------|
| Llama 3.1 8B (baseline) | 4.25 / 5.00 | — |
| Llama 3.3 70B (new) | 4.35 / 5.00 | +0.10 |

**Per-category highlights**:
- ✅ New model improved on: `drug_interaction` (+0.33), `mental_health` (+0.50), `general_health` (+0.33).
- ❌ New model regressed on: `refusal` (-0.33).
- ➡️ No change on: `emergency`, `side_effects`, `lifestyle`, `symptoms`.

### Embedding Similarity

| Model | Avg Similarity | Min | Max |
|-------|---------------|-----|-----|
| Llama 3.1 8B | 0.880 | 0.828 | 0.931 |
| Llama 3.3 70B | 0.885 | 0.832 | 0.929 |

Both models show high semantic similarity to golden answers (>0.88 average), consistent with the LLM-as-a-Judge scores.

### Agent Behavior

The ReAct agent correctly chains multiple tool calls when needed:

- **Single tool**: "What are the side effects of metformin?" → `get_medication_info` → answer.
- **Multi-tool**: "Is ibuprofen safe for P001?" → `get_patient_history` → `check_drug_interactions` (×2) → answer.
- **Emergency**: "P002 has difficulty breathing" → `check_emergency` → direct answer with emergency guidance.

## 💼 Business Impact

### For ML Engineers

- **Model comparison**: Systematically test whether a new model is better before deploying it.
- **Regression detection**: Catch category-level regressions (e.g., the new model scores worse on `refusal`).
- **Agent debugging**: Inspect exactly which tools were called and why in the LangFuse UI.

### For MLOps Teams

- **Production monitoring**: Built-in evaluators run automatically on every user query — no cron jobs needed.
- **Cost tracking**: LangFuse logs latency and cost per trace, enabling budget monitoring.
- **Dataset versioning**: Golden datasets live inside LangFuse and can be reused across experiments.

### For AI Product Teams

- **Quality gates**: Set score thresholds before deploying model updates.
- **Evaluation strategies**: Three different evaluation approaches (LLM-judge, embedding similarity, built-in) give complementary signals.
- **Reproducibility**: All evaluation runs are logged and comparable in the LangFuse UI.

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/pedroalexleite/Learning-LangFuse.git
cd Learning-LangFuse

# Install dependencies
pip install langfuse google-genai openai python-dotenv numpy
```

### Setup

**1. Start LangFuse (Docker)**:
```bash
cd ~/langfuse
docker compose up -d
# Open http://localhost:3000
```

**2. Create `.env` file**:
```
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=http://localhost:3000
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY_1=your_groq_key
```

### Running the Notebooks

Run in order to build on each concept:

```bash
# 1. Start with evaluation approaches
jupyter notebook LLM-Judge-1.ipynb
jupyter notebook LLM-Judge-2.ipynb
jupyter notebook Embedding-Similarity.ipynb

# 2. Then the agents
jupyter notebook Agent.ipynb
jupyter notebook Multi-Agent.ipynb
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/NewNotebook`).
3. Commit your changes (`git commit -m 'Add new evaluation approach'`).
4. Push to the branch (`git push origin feature/NewNotebook`).
5. Open a Pull Request.
