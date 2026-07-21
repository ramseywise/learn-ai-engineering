# Analyzing Sample Conversations - Quick Guide

## 🎯 Goal

Before running full evaluation on all conversations, you should:
1. **Test the evaluation system** on 10 sample conversations
2. **Understand what the AI evaluators detect**
3. **Validate evaluation quality**
4. **Adjust if needed** before spending money on full analysis

---

## 🚀 Two Ways to Analyze Examples

### Option 1: Standalone Script (Quickest)

Run the standalone analysis script:

```bash
# If using virtual environment
source venv/bin/activate

# Run analysis
python3 analyze_sample_conversations.py
```

**What it does:**
- Loads 10 sample conversations
- Runs multi-agent evaluation
- Shows detailed results for each conversation
- Displays summary statistics
- Interactive (press Enter between conversations)

**Output:**
```
Quick Summary Table
Quality Report
Detailed examination of each conversation
  - User question
  - Conecta's response
  - AI evaluator findings
  - Hallucination evidence
  - Document relevance
  - Completeness analysis
```

**Cost:** ~$0.04 for 10 conversations

---

### Option 2: Jupyter Notebook (More Interactive)

Use the comprehensive notebook with new analysis section:

```bash
jupyter notebook notebooks/conecta_hallucination_analysis.ipynb
```

**New cells to add** (copy from `notebooks/example_analysis_cells.txt`):

1. **Import Analysis Helpers** - Visualization tools
2. **Select & Evaluate 10 Samples** - Run evaluation
3. **Quick Summary Table** - Overview of results
4. **Quality Report** - Metrics and interpretation
5. **Detailed Examination** - Each conversation in detail
6. **Problematic Cases** - Focus on issues
7. **Evaluation Quality Checklist** - Manual review guide

**To add the cells:**
1. Open the notebook
2. Find Cell 13 (after "Test on Single Conversation")
3. Insert new cells and copy code from `example_analysis_cells.txt`

---

## 📊 What You'll See

### Summary Table

```
session_id      hallucination  severity  grounding  doc_score  comp_score  unnecessary_clarif
00321044...     ✅            none      100%       5/5        5/5         ✅
a7b3c...        🔴            major     60%        3/5        2/5         🔴
```

**Read as:**
- 🔴 = Issue detected
- ✅ = No issues
- Grounding = % claims supported by documents
- Doc score = Relevance of retrieved documents
- Comp score = Completeness of response

### Quality Report

```
📊 Overall Statistics:
   Total evaluations: 10
   ✅ Successful: 10
   ❌ Failed: 0

🎯 Detection Metrics:
   Average confidence: 85.3%
   Detection rate: 30.0%
   Average claims per response: 4.2
   Average grounding ratio: 78.5%

📈 Severity Distribution:
   ✅ NONE: 7
   🟡 MINOR: 2
   🔴 MAJOR: 1
   🔥 CRITICAL: 0
```

### Detailed Conversation Analysis

For each conversation, you'll see:

**1. User Question**
```
📝 USER QUESTION:
──────────────────────────────────────────────────
Como puedo cancelar una tarjeta de crédito?
```

**2. Conecta's Response**
```
🤖 CONECTA'S RESPONSE:
──────────────────────────────────────────────────
Para cancelar tu tarjeta de crédito Davivienda...
[Full response]
```

**3. Documents Used** (optional)
```
📚 DOCUMENTS USED:
──────────────────────────────────────────────────
Documento 1234: Cancelación de tarjetas
[Document content]
```

**4. Hallucination Detection** (CRITICAL)
```
🚨 HALLUCINATION DETECTION (CRITICAL)
──────────────────────────────────────────────────
🔴 Hallucination Detected: True
🔴 Severity: MAJOR
   Type: fabrication
   Confidence: 87.5%

📊 Claims Analysis:
   Total claims examined: 5
   ✅ Grounded in documents: 3 (60.0%)
   ❌ Hallucinated/Unsupported: 2

💭 AI Evaluator's Assessment:
The response contains claims about cancellation fees that
are not mentioned in the source documents. Specifically...

🔍 HALLUCINATED CLAIMS (Evidence):
   Claim #1:
   📌 Statement: "La cancelación tiene un costo de $50,000"
   📄 Document Support: NOT FOUND
   💡 Explanation: This fee is not mentioned in any of the
                   provided documents about card cancellation.
```

**5. Document Relevance**
```
🔍 DOCUMENT RELEVANCE
──────────────────────────────────────────────────
   Score: [███░░] 3/5
   Documents contain answer: ✅ Yes

   ⚠️  Missing Information:
      • Specific cancellation procedures
      • Required documents
```

**6. Completeness Check**
```
✅ COMPLETENESS CHECK
──────────────────────────────────────────────────
   Score: [██░░░] 2/5
   Used all relevant info: ❌ No
   🔴 UNNECESSARY CLARIFICATION DETECTED
      → Conecta asked for clarification when answer
         was in documents!

   ⚠️  Information NOT included in response:
      • Online cancellation option
      • Timeframe for cancellation
```

**7. Escalation Validation**
```
🎯 ESCALATION VALIDATION
──────────────────────────────────────────────────
   Actually escalated: ❌ No
   Escalation was appropriate: ❌ No
   Should have escalated: ❌ No

   💭 Reason: The documents contain sufficient information
              to answer the question. No escalation needed.
```

**8. Secondary Verification** (if hallucination detected)
```
🔬 SECONDARY VERIFICATION (Critical Finding)
──────────────────────────────────────────────────
   Verified: ✅ Confirmed
   Adjusted severity: major
   Final recommendation: REJECT

   💭 Verification explanation:
   The original finding is correct. The cancellation fee
   claim is indeed not supported by any documents.
```

---

## 🎯 How to Use This Information

### 1. Validate Evaluations

For each conversation, ask yourself:
- ✅ **Is the hallucination detection correct?**
- ✅ **Are the severity levels appropriate?**
- ✅ **Does the completeness assessment make sense?**
- ✅ **Are document relevance scores accurate?**

### 2. Look for Patterns

```
Common issues to spot:
□ Conecta frequently makes up information
□ Documents often don't contain answers
□ Conecta asks for unnecessary clarification
□ Responses are incomplete
□ Escalations are inappropriate
```

### 3. Adjust if Needed

**If evaluations are too strict:**
```python
# In notebook or config
config.temperature = 0.2  # Higher = more lenient
```

**If evaluations are too lenient:**
```python
config.temperature = 0.05  # Lower = more strict
```

**If specific prompts need tuning:**
```python
# Edit: src/utils/prompt_templates.py
# Adjust the prompts for each agent
```

### 4. Decide Next Steps

**Evaluations look good?**
→ Proceed to full batch evaluation

**Need adjustments?**
→ Tune prompts/config and re-run sample

**Want more examples?**
→ Change sample size or indices

---

## 💡 Pro Tips

### Focus on Interesting Cases

The script automatically identifies:
- 🔴 Hallucinations detected
- 🔴 Unnecessary clarifications
- 🔴 Low grounding (<80%)
- 🔴 Poor document relevance (<3/5)

Review these first!

### Compare with Your Judgment

For a few conversations:
1. Read the user question
2. Read Conecta's response
3. Read the documents
4. Form your own opinion
5. Compare with AI evaluation
6. Assess agreement

### Check Edge Cases

Look for:
- Very short questions (vague)
- Very long responses (complex)
- Technical banking terminology
- Ambiguous requests

### Document Your Findings

Create a checklist:
```
✅ Hallucination detection is accurate
❌ Completeness scoring too strict
✅ Document relevance makes sense
⚠️  Need to adjust severity threshold
```

---

## 📋 Evaluation Quality Checklist

After reviewing 10 examples:

**Hallucination Detection:**
- [ ] Flagged hallucinations are actually incorrect
- [ ] No false positives (correct info marked as hallucination)
- [ ] No false negatives (missed hallucinations)
- [ ] Severity levels make sense

**Document Relevance:**
- [ ] Relevant documents scored high
- [ ] Irrelevant documents scored low
- [ ] "Has answer" flag is accurate

**Completeness:**
- [ ] Complete responses scored high
- [ ] Incomplete responses scored low
- [ ] "Unnecessary clarification" flag is accurate

**Overall Quality:**
- [ ] AI evaluations align with human judgment
- [ ] Confidence scores correlate with accuracy
- [ ] No systematic biases detected

---

## 🐛 Troubleshooting

### "Model not found" error

The model name was fixed. If you still see this:
```bash
# Update the code
git pull
```

### Script hangs / takes too long

- Check your internet connection
- Verify API key is valid
- Reduce sample size to 5 conversations

### Evaluations seem random

- Lower temperature for consistency
- Use Pro model for all agents
- Check if documents are being loaded correctly

---

## 🎓 What to Learn

From this analysis, you should understand:

1. **How the AI evaluators work**
   - What they detect
   - How they reason
   - Their strengths and limitations

2. **Conecta's performance patterns**
   - Common hallucination types
   - Document retrieval quality
   - Response completeness

3. **System reliability**
   - False positive rate
   - False negative rate
   - Overall accuracy

4. **Next steps**
   - Whether to proceed to full analysis
   - What adjustments are needed
   - Expected results

---

## 📚 Next Steps

**After analyzing examples:**

1. ✅ Review evaluation quality
2. ✅ Adjust prompts/config if needed
3. ✅ Re-run sample if necessary
4. 🚀 Proceed to full batch evaluation
5. 📊 Generate comprehensive report
6. 💡 Create improvement recommendations

**Ready for full analysis?**
→ See main notebook or run full evaluation

**Need help?**
→ See README.md for complete documentation

---

**Happy analyzing! 🚀**
