# Conecta AI Agent Hallucination Analysis System

## Multi-Agent Evaluation Pipeline for Banking AI Assistant

This system implements a sophisticated **Multi-Agent Specialist Pipeline** to analyze the performance of "Conecta", a banking AI assistant, with a primary focus on detecting hallucinations (made-up information).

---

## 🏗️ Architecture

### **Option 2: Multi-Agent Specialist Pipeline** (Implemented)

```
┌──────────────────────────────────────────────────────────────┐
│                   Orchestrator                               │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬─────────────┐
        │            │            │             │
        ▼            ▼            ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Agent 1    │ │   Agent 2    │ │   Agent 3    │ │   Agent 4    │
│              │ │              │ │              │ │              │
│ Document     │ │ Hallucination│ │ Completeness │ │ Escalation   │
│ Relevance    │ │ Detector ⭐  │ │ Checker      │ │ Validator    │
│              │ │              │ │              │ │              │
│ Gemini Flash │ │ Gemini Pro   │ │ Gemini Flash │ │ Gemini Flash │
└──────────────┘ └──────┬───────┘ └──────────────┘ └──────────────┘
                        │
                        │ If hallucination detected
                        ▼
                 ┌──────────────┐
                 │   Agent 5    │
                 │ Verification │
                 │ (Secondary)  │
                 │ Gemini Pro   │
                 └──────────────┘
```

### Agents

1. **🔍 Document Relevance Agent** (Flash)
   - Checks if retrieved documents are relevant to the question
   - Fast evaluation using Gemini Flash

2. **🚨 Hallucination Detector** (Pro) - **CRITICAL**
   - Detects when Conecta makes up information
   - Identifies: Fabrication, Distortion, Information Mixing, Contradictions
   - Uses powerful Gemini Pro model for accuracy

3. **✅ Completeness Checker** (Flash)
   - Validates if response uses all available document information
   - Detects unnecessary clarification requests

4. **🎯 Escalation Validator** (Flash)
   - Judges if escalation to human expert was appropriate
   - Identifies preventable escalations

5. **🔬 Verification Agent** (Pro)
   - Secondary verification for critical findings
   - Reduces false positives in hallucination detection

---

## 📊 Data Pipeline

### Input Files (4 CSVs)

1. **df_merged_final_oct_v3.csv** (33K rows)
   - Main conversation data
   - User questions and Conecta responses
   - Escalation triggers

2. **df_merged_genesys (1).csv** (738 rows)
   - Expert escalation transcripts
   - Links via `fk_tbl_conversaciones_conecta2`

3. **1758819667267-lf-traces-export-cm38vdgjp005z3hq2htm5f0mx.csv** (975 rows)
   - Langfuse trace data
   - Document IDs used by Conecta
   - Execution metadata, costs

4. **base_conocimiento_ajustada_cargue_produccion_v2 (1).csv** (2.4K rows)
   - Knowledge base with Q&A pairs
   - Document content and keywords

### ETL Process

```python
# Step 1: Load all files
data = load_all_data(data_dir=".")

# Step 2: Process Langfuse JSON
analysis_df = merge_all_datasets(data)

# Step 3: Enrich with document content
enriched_df = enrich_with_documents(analysis_df, data['knowledge_base'])

# Step 4: Create conversation-level summary
conversation_df = create_conversation_summary(enriched_df)
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY='your-api-key-here'

# OR for Vertex AI
export VERTEX_PROJECT_ID='your-project-id'
```

### 2. Run Analysis

```bash
# Open Jupyter notebook
jupyter notebook notebooks/conecta_hallucination_analysis.ipynb
```

### 3. Configure Provider

**Option A: Gemini (Recommended for development)**

```python
from src.config import EvaluatorConfig, ProviderType, ModelType

config = EvaluatorConfig(
    provider=ProviderType.GEMINI,
    gemini_api_key=os.getenv('GEMINI_API_KEY'),
    hallucination_detector_model=ModelType.PRO
)
```

**Option B: Vertex AI (For production)**

```python
config = EvaluatorConfig(
    provider=ProviderType.VERTEX,
    vertex_project_id=os.getenv('VERTEX_PROJECT_ID'),
    hallucination_detector_model=ModelType.PRO
)
```

---

## 💰 Cost Estimate

**Per 1,000 conversations:**
- Document Relevance (Flash): ~$0.50
- **Hallucination Detection (Pro)**: ~$2.00 ⭐
- Completeness (Flash): ~$0.50
- Escalation (Flash): ~$0.30
- Verification (Pro, 15% cases): ~$0.40
- **Total: ~$3.70**

---

## 📁 Project Structure

```
langfuse_use/
├── notebooks/
│   └── conecta_hallucination_analysis.ipynb    # Main analysis notebook
│
├── src/
│   ├── config.py                               # Configuration
│   │
│   ├── data/
│   │   ├── loader.py                           # Load CSV files
│   │   └── __init__.py
│   │
│   ├── etl/
│   │   ├── json_extractor.py                   # Parse Langfuse JSON
│   │   ├── merger.py                           # Merge datasets
│   │   └── __init__.py
│   │
│   ├── evaluators/
│   │   ├── base.py                             # Base classes
│   │   ├── factory.py                          # Provider factory
│   │   │
│   │   ├── providers/
│   │   │   ├── gemini_provider.py              # Gemini API
│   │   │   ├── vertex_provider.py              # Vertex AI
│   │   │   └── __init__.py
│   │   │
│   │   └── agents/
│   │       ├── hallucination_detector.py       # ⭐ Critical agent
│   │       ├── document_relevance.py
│   │       ├── completeness_checker.py
│   │       ├── escalation_validator.py
│   │       ├── verification_agent.py
│   │       └── __init__.py
│   │
│   ├── orchestrator.py                         # Agent coordination
│   │
│   ├── utils/
│   │   ├── prompt_templates.py                 # Prompt management
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── requirements.txt
└── README.md
```

---

## 🔧 Usage Examples

### Evaluate Single Conversation

```python
from src.orchestrator import EvaluationOrchestrator, ConversationData

# Initialize
orchestrator = EvaluationOrchestrator(config)

# Prepare data
conversation = ConversationData(
    session_id="session_123",
    user_question="¿Cómo puedo abrir una cuenta?",
    ai_response="Para abrir una cuenta...",
    documents="Documento 1: Requisitos...",
    escalated=False
)

# Evaluate
result = orchestrator.evaluate_conversation(conversation)

# Check results
if result.hallucination['hallucination_detected']:
    print(f"⚠️ Hallucination detected: {result.hallucination['severity']}")
```

### Batch Evaluation

```python
# Prepare batch
conversations = [...]  # List of ConversationData

# Run batch
results = orchestrator.evaluate_batch(
    conversations,
    run_verification=True,
    max_workers=3
)

# Analyze
results_df = pd.DataFrame([r.to_dict() for r in results])
```

---

## 📊 Key Metrics

### Hallucination Detection

- **Hallucination Rate**: % of responses with made-up info
- **Severity**: None, Minor, Major, Critical
- **Types**: Fabrication, Distortion, Mixing, Contradiction
- **Grounding Ratio**: % of claims supported by documents

### Response Quality

- **Document Relevance Score**: 1-5 (Are docs relevant?)
- **Completeness Score**: 1-5 (Did Conecta use all info?)
- **Unnecessary Clarifications**: When answer was available

### Escalation Quality

- **Appropriate Escalations**: Should have gone to expert
- **Preventable Escalations**: Conecta had the answer

---

## 🎯 Priority: Hallucination Detection

The system is optimized for detecting **hallucinations** (made-up information), which is the most critical failure mode:

### Why Critical?
- ❌ Incorrect information to customers
- ❌ Compliance violations
- ❌ Financial losses
- ❌ Reputation damage

### Detection Method
1. Extract all factual claims from Conecta's response
2. Search documents for supporting evidence
3. Flag claims without clear document support
4. Verify critical findings with secondary agent
5. Provide specific evidence and severity rating

---

## 🔄 Extending the System

### Add New Agent

```python
from src.evaluators.base import BaseAgent, EvaluationResult

class MyCustomAgent(BaseAgent):
    def get_prompt(self, **kwargs) -> str:
        # Return formatted prompt
        pass

    def parse_response(self, response: dict) -> EvaluationResult:
        # Parse LLM response
        pass
```

### Switch Model for Agent

```python
config = EvaluatorConfig(
    # Use Pro for all agents
    document_relevance_model=ModelType.PRO,
    hallucination_detector_model=ModelType.PRO,
    completeness_checker_model=ModelType.PRO
)
```

---

## 📝 Output Files

After running analysis:

1. **conecta_evaluation_results_TIMESTAMP.csv**
   - Full evaluation results for all conversations

2. **critical_hallucinations_TIMESTAMP.csv**
   - Only conversations with major/critical hallucinations

3. **evaluation_summary_TIMESTAMP.json**
   - Summary statistics and key metrics

4. **conecta_evaluation_results.png**
   - Visualization dashboard

---

## 🐛 Troubleshooting

### API Key Issues

```bash
# Check if key is set
echo $GEMINI_API_KEY

# Set temporarily
export GEMINI_API_KEY='your-key'

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
```

### Rate Limiting

If you hit rate limits, adjust config:

```python
config = EvaluatorConfig(
    requests_per_minute=30,  # Lower rate
    max_retries=5  # More retries
)
```

### Parallel Execution Issues

Disable parallel execution:

```python
config = EvaluatorConfig(
    parallel_agents=False  # Run sequentially
)
```

---

## 📚 Dependencies

- **google-generativeai**: Gemini API
- **google-cloud-aiplatform**: Vertex AI (optional)
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **matplotlib, seaborn**: Visualization
- **jupyter**: Notebook interface

---

## 🤝 Contributing

This is a custom analysis system for Conecta. To modify:

1. Update agents in `src/evaluators/agents/`
2. Modify prompts in `src/utils/prompt_templates.py`
3. Adjust ETL in `src/etl/`

---

## 📄 License

Internal use only - Bank Davivienda

---

## 🎯 Next Steps

1. ✅ Run initial analysis on Langfuse data
2. 📊 Identify top hallucination patterns
3. 🔧 Improve Conecta's grounding mechanism
4. 📈 Monitor hallucination rate over time
5. 🚀 Expand to full conversation dataset

---

**Built with ❤️ for improving Conecta's reliability and trustworthiness**
