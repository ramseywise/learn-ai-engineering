# Deep Hallucination Analysis Guide

## 🎯 What This Does

Goes beyond basic detection to understand **WHY** Conecta hallucinates:

- **Root Cause Analysis**: Document length? Question quality? Missing information?
- **Pattern Detection**: When do hallucinations happen most?
- **Validation**: See exact examples to check if evaluator is accurate or too strict
- **Correlations**: Statistical analysis of hallucination triggers

---

## 🚀 Quick Start

```bash
# Run the deep analysis
python3 analyze_hallucinations_detailed.py
```

**What happens:**
1. Analyzes 50 conversations (larger sample for pattern detection)
2. Runs AI evaluation on each
3. Identifies ALL hallucinations (including minor ones)
4. Shows correlation analysis
5. Displays detailed examples with full context
6. Lets you validate if evaluator is correct

**Time:** ~2-3 minutes
**Cost:** ~$0.05 (using Flash 2.0)

---

## 📊 What You'll See

### 1. Correlation Analysis

```
CORRELATION ANALYSIS: What Causes Hallucinations?

📊 Sample Size:
   Total conversations: 50
   With hallucinations: 12 (24.0%)
   Clean responses: 38 (76.0%)

📈 FACTOR COMPARISON (Hallucination vs Clean):

🔴 Document Length:
   Hallucination cases: 8,432.5
   Clean cases: 3,221.1
   Difference: +161.8%

🟡 Number of Documents:
   Hallucination cases: 4.2
   Clean cases: 2.8
   Difference: +50.0%

🔴 Document Relevance Score:
   Hallucination cases: 2.3/5
   Clean cases: 4.1/5
   Difference: -43.9%
```

**Indicators:**
- 🔴 Major difference (>20%) - strong correlation
- 🟡 Moderate difference (10-20%) - possible factor
- ✅ Small difference (<10%) - not a factor

### 2. Boolean Factor Analysis

```
🔍 BOOLEAN FACTOR ANALYSIS:

🔴 Documents Have Answer:
   In hallucination cases: 33.3%
   In clean cases: 89.5%
   Difference: -56.2 percentage points
```

**Key insight:** Shows whether hallucinations happen when:
- Documents are missing the answer (expected)
- Documents HAVE the answer but Conecta ignores it (CRITICAL BUG)

### 3. Detailed Examples

For each hallucination case, you see:

```
HALLUCINATION EXAMPLE 1/10
Severity: MAJOR | Grounding: 60%

📊 CONTEXT METRICS:
   Documents provided: 3
   Total document length: 12,450 chars
   Document relevance: 2/5
   Documents have answer: ❌ No
   Question length: 15 words
   Response length: 87 words

❓ USER QUESTION:
Como puedo aumentar el cupo de mi tarjeta de crédito?

🤖 CONECTA'S RESPONSE:
Para aumentar el cupo de tu tarjeta de crédito Davivienda,
puedes solicitarlo a través de nuestra aplicación móvil o
llamando al *555. El aumento está sujeto a evaluación de tu
historial crediticio y capacidad de pago. El proceso toma
aproximadamente 48 horas hábiles y te notificaremos por SMS.

🚨 HALLUCINATION DETECTED (MAJOR):

📊 Grounding Ratio: 60% of claims supported

💭 AI EVALUATOR'S REASONING:
The response contains specific claims about process timing (48 hours)
and notification method (SMS) that are not mentioned in the provided
documents. The general process is correct, but these specific details
appear to be fabricated.

🔍 SPECIFIC HALLUCINATED CLAIMS:

   Claim #1:
   📌 Statement: "El proceso toma aproximadamente 48 horas hábiles"
   💡 Issue: The documents do not specify any timeframe for the
             credit increase evaluation process.

   Claim #2:
   📌 Statement: "te notificaremos por SMS"
   💡 Issue: The notification method is not mentioned in the source
             documents. This could be incorrect or outdated information.

─────────────────────────────────────────────────────────────
❓ VALIDATION QUESTION: Is this actually a hallucination,
   or is the evaluator being too strict?
─────────────────────────────────────────────────────────────
```

**For each example, ask yourself:**
- ✅ Is the claim actually false/unsupported?
- ✅ Or is this reasonable inference from context?
- ✅ Is the evaluator too strict?

---

## 🔍 What to Look For

### Pattern 1: Long Documents = Hallucinations

**If you see:**
```
🔴 Document Length:
   Hallucination cases: 12,450
   Clean cases: 3,200
   Difference: +288%
```

**Hypothesis:** Conecta struggles to parse long documents accurately.

**Action:**
- Implement document chunking
- Improve retrieval to return smaller, more focused excerpts
- Test if reducing max document length helps

---

### Pattern 2: Documents Have Answer But Still Hallucinates

**If you see:**
```
⚠️ HALLUCINATING DESPITE HAVING THE ANSWER!
   75% of hallucination cases had the answer in documents.
```

**This is CRITICAL!** Means:
- Retrieval is working (found correct docs)
- But Conecta is ADDING false details on top of correct info

**Action:**
- Review prompt engineering
- Add explicit instruction: "Only use information from documents, do not add details"
- Check if response is mixing multiple document contexts

---

### Pattern 3: Poor Retrieval = Hallucinations

**If you see:**
```
🎯 POOR DOCUMENT RETRIEVAL → HALLUCINATIONS
   Hallucination cases have relevance score 2.1/5
   Clean cases have relevance score 4.3/5
```

**Hypothesis:** When retrieval fails, Conecta invents info instead of saying "I don't know"

**Action:**
- Improve retrieval system
- Add confidence threshold (if relevance < 3, admit uncertainty)
- Enhance embedding/indexing strategy

---

### Pattern 4: Vague Questions = Hallucinations

**If you see:**
```
❓ VAGUE QUESTIONS → HALLUCINATIONS
   67% of hallucination cases vs 23% of clean cases had vague questions
```

**Hypothesis:** Conecta fills gaps when question is too general

**Action:**
- Add clarification requests for vague questions
- Don't allow responses when question is <5 words
- Implement question quality scoring

---

## 🧪 Testing Different Hypotheses

The script automatically generates hypotheses based on detected patterns:

```
📚 LONGER DOCUMENTS → MORE HALLUCINATIONS
   Hypothesis: Conecta struggles to parse long documents accurately.

🎯 POOR DOCUMENT RETRIEVAL → HALLUCINATIONS
   Hypothesis: When retrieval fails, Conecta invents information.

⚠️ HALLUCINATING DESPITE HAVING THE ANSWER!
   Hypothesis: CRITICAL - Conecta adds false details even when correct info available.
```

**For each hypothesis:**
1. Review the detailed examples
2. Check if pattern holds
3. Test potential fixes
4. Re-run analysis to validate improvement

---

## 🎯 Validation Checklist

After reviewing examples, assess evaluator quality:

### Hallucination Detection Accuracy

**For each example shown:**

- [ ] **True Positive**: Claim is actually unsupported by documents
- [ ] **False Positive**: Claim is reasonable inference, evaluator too strict
- [ ] **Severity Correct**: Minor/major/critical classification makes sense

**Red flags (evaluator too strict):**
- Flagging reasonable paraphrasing as hallucination
- Marking general knowledge as fabrication
- Too literal interpretation of documents

**Red flags (evaluator too lenient):**
- Missing obvious fabricated details
- Accepting vague claims without evidence
- Not catching contradictions

### Overall Assessment

```
Evaluator Accuracy: ___/10 examples correct

False Positive Rate: ___% (flagged correct info as hallucination)
False Negative Rate: ___% (missed actual hallucinations)

Recommendation:
□ Evaluator is accurate - proceed to full analysis
□ Evaluator too strict - adjust temperature or prompts
□ Evaluator too lenient - use Pro model or adjust prompts
□ Need more examples to decide
```

---

## 🔧 Customization

### Change Sample Size

Edit `analyze_hallucinations_detailed.py` line 259:

```python
sample_size = min(50, len(conversation_df))  # Change 50 to desired number
```

**Recommendations:**
- **10-20**: Quick validation of evaluator
- **50**: Good for pattern detection
- **100+**: Statistical significance for correlations

### Focus on Specific Cases

After running once, load the output CSV:

```python
import pandas as pd

# Load results
df = pd.read_csv('hallucination_analysis_detailed.csv')

# Filter for specific patterns
severe_cases = df[df['severity'].isin(['major', 'critical'])]
long_doc_hallucinations = df[(df['has_hallucination']) & (df['avg_doc_length'] > 10000)]
has_answer_but_hallucinated = df[(df['has_hallucination']) & (df['doc_has_answer'])]

# Examine
for idx, row in has_answer_but_hallucinated.iterrows():
    print(f"Question: {row['user_question']}")
    print(f"Response: {row['ai_response'][:200]}...")
    print(f"Evidence: {row['evidence']}")
    print()
```

### Add Custom Metrics

Edit the `calculate_text_metrics` function to add your own factors:

```python
def calculate_text_metrics(text: str) -> Dict[str, Any]:
    # Add custom metrics
    has_numbers = bool(re.search(r'\d', text))
    has_technical_terms = any(term in text.lower() for term in ['credito', 'cuenta', 'tarjeta'])

    return {
        ...
        'has_numbers': has_numbers,
        'has_technical_terms': has_technical_terms
    }
```

---

## 📈 Interpreting Results

### Scenario 1: Low Hallucination Rate (<10%)

```
✅ Conecta is performing well
```

**Next steps:**
- Review minor cases to ensure evaluator isn't missing issues
- Proceed to full analysis with confidence
- Focus on other quality metrics (completeness, escalation)

---

### Scenario 2: Moderate Rate (10-30%)

```
⚠️ Some issues detected
```

**Check:**
- Are hallucinations happening when documents don't have answer? (Expected)
- Or when documents DO have answer? (Critical bug)

**Next steps:**
- Identify primary cause from correlation analysis
- Implement targeted fix
- Re-run analysis to validate improvement

---

### Scenario 3: High Rate (>30%)

```
🔴 Significant hallucination problem
```

**Likely causes:**
1. Poor document retrieval (most common)
2. Prompt engineering issues
3. Model limitations
4. Training data problems

**Next steps:**
- Review detailed examples to identify root cause
- Focus on highest-impact fix first
- Consider if evaluator is too strict (check false positive rate)

---

## 💡 Common Findings

### Finding: "Hallucinations only when docs don't have answer"

**Status:** ✅ Expected behavior
**Action:** Improve retrieval OR add explicit "I don't know" responses

### Finding: "Hallucinations even when docs have answer"

**Status:** 🔴 Critical bug
**Action:** Fix prompt to prevent adding unsupported details

### Finding: "Long documents → more hallucinations"

**Status:** ⚠️ Model limitation
**Action:** Chunk documents, improve extraction

### Finding: "Vague questions → more hallucinations"

**Status:** ⚠️ Expected but fixable
**Action:** Request clarification for vague questions

### Finding: "Evaluator is too strict"

**Status:** ⚠️ False positives
**Action:** Adjust temperature (0.1 → 0.2) or switch to Pro model

---

## 🔄 Iteration Process

1. **Run initial analysis** (this script)
2. **Identify primary pattern** (e.g., long docs → hallucinations)
3. **Implement fix** (e.g., document chunking)
4. **Re-run analysis** to validate improvement
5. **Repeat** for next highest-impact issue

**Track improvements:**
```
Iteration 1: 28% hallucination rate
→ Fixed retrieval threshold
Iteration 2: 19% hallucination rate
→ Added document chunking
Iteration 3: 12% hallucination rate
→ Improved prompt engineering
Final: 8% hallucination rate ✅
```

---

## 📁 Output Files

The script creates:

**hallucination_analysis_detailed.csv**
- All analyzed conversations
- Metrics for each (doc length, question quality, etc.)
- Hallucination flags and evidence
- Use for custom analysis in Excel/Python

**Columns:**
- `session_id`: Conversation identifier
- `has_hallucination`: True/False
- `severity`: none/minor/major/critical
- `grounding_ratio`: % of claims supported (0.0-1.0)
- `q_length`, `r_length`: Text lengths
- `doc_count`, `avg_doc_length`: Document metrics
- `doc_relevance_score`: 1-5 relevance rating
- `user_question`, `ai_response`: Full text
- `evidence`: List of hallucinated claims
- `reasoning`: AI evaluator explanation

---

## 🎓 What You Should Learn

After this analysis, you should understand:

1. **Primary Hallucination Trigger**
   - Is it missing information? Poor retrieval? Long documents? Vague questions?

2. **Evaluator Quality**
   - Is it accurate? Too strict? Missing issues?

3. **Severity Distribution**
   - Mostly minor (acceptable)? Or major/critical (urgent fix needed)?

4. **Actionable Insights**
   - What specific fix will have biggest impact?

5. **Confidence Level**
   - Ready for full analysis? Or need to tune evaluator first?

---

## ❓ FAQ

**Q: Script shows 0 hallucinations but I know there are issues**

A: Evaluator may be too lenient. Try:
- Lowering temperature (0.1 → 0.05)
- Reviewing a few cases manually
- Checking if documents actually contain correct info

**Q: Too many hallucinations flagged, but they look correct to me**

A: Evaluator may be too strict. Try:
- Raising temperature (0.1 → 0.2)
- Check if flagged claims are reasonable inferences
- Review prompt templates

**Q: No clear patterns in correlation analysis**

A: May need larger sample size (increase to 100+) or more diverse sample

**Q: Want to focus only on critical/major cases**

A: After first run, filter the CSV:
```python
df = pd.read_csv('hallucination_analysis_detailed.csv')
severe = df[df['severity'].isin(['major', 'critical'])]
```

---

**Ready to dive deep? Run the script!**

```bash
python3 analyze_hallucinations_detailed.py
```
