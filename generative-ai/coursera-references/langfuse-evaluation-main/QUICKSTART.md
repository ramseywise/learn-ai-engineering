# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Credentials

**Option A: Using .env file (Recommended)**

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API key
nano .env
# OR
code .env
```

Add your Gemini API key:
```env
GEMINI_API_KEY=your-actual-api-key-here
```

**Get your Gemini API key:**
👉 https://makersuite.google.com/app/apikey

**Option B: Using environment variable**

```bash
export GEMINI_API_KEY='your-actual-api-key-here'
```

### Step 3: Run the Analysis

```bash
# Start Jupyter
jupyter notebook notebooks/conecta_hallucination_analysis.ipynb
```

Or run the automated setup:

```bash
./setup.sh
```

---

## ✅ Verify Setup

Run this in Python to check if everything is configured:

```python
import sys
sys.path.insert(0, '..')

from src.utils.env_loader import load_environment, validate_environment

# Load .env file
load_environment()

# Validate credentials
if validate_environment():
    print("✅ All set! Ready to run analysis.")
else:
    print("❌ Setup incomplete. Follow instructions above.")
```

---

## 🔧 Troubleshooting

### "No module named 'google.generativeai'"

```bash
pip install google-generativeai
```

### "GEMINI_API_KEY not found"

Make sure you:
1. Created `.env` file from `.env.example`
2. Added your actual API key
3. Restarted your Jupyter kernel

### "API key is invalid"

Get a new key from: https://makersuite.google.com/app/apikey

---

## 📊 What You'll Get

After running the analysis:

1. **Hallucination Detection**
   - How often Conecta makes up information
   - Severity levels (Critical/Major/Minor)
   - Specific examples with evidence

2. **Response Quality**
   - Document relevance scores
   - Completeness metrics
   - Grounding ratios

3. **Escalation Analysis**
   - Preventable vs necessary escalations
   - Cost implications

4. **Visualizations**
   - Dashboards and charts
   - Saved as PNG files

---

## 💰 Cost

**Approximate cost: $3.70 per 1,000 conversations**

For the complete Langfuse dataset (~975 conversations):
- **Total cost: ~$3.60**

---

## 🎯 Next Steps

1. ✅ Complete setup (you are here)
2. 📊 Run initial analysis
3. 🔍 Review hallucination findings
4. 📝 Generate recommendations
5. 🚀 Implement improvements to Conecta

---

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.
