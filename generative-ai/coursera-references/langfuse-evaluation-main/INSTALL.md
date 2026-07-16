# Installation Guide

## ⚠️ Your system uses an externally-managed Python environment

You have two options:

---

## Option 1: Use Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py

# When you're done, deactivate
deactivate
```

**Every time you work on the project:**
```bash
source venv/bin/activate
jupyter notebook notebooks/conecta_hallucination_analysis.ipynb
```

---

## Option 2: Install System-Wide (Quick but not recommended)

```bash
pip install --break-system-packages -r requirements.txt
```

⚠️ **Warning**: This can cause conflicts with system packages.

---

## Option 3: Install Just What You Need

```bash
# Install only the Gemini API package
pip install --break-system-packages google-generativeai
```

---

## ✅ After Installation

Run verification:
```bash
python3 verify_setup.py
```

You should see:
```
✅ ✅ ✅  EVERYTHING IS READY! ✅ ✅ ✅
```

Then start the analysis:
```bash
jupyter notebook notebooks/conecta_hallucination_analysis.ipynb
```

---

## 🐛 Troubleshooting

### "No module named 'google.generativeai'"

Your virtual environment is not activated. Run:
```bash
source venv/bin/activate
```

### "Jupyter not found"

Install in your virtual environment:
```bash
source venv/bin/activate
pip install jupyter
```

### API Key Issues

Make sure `.env` file contains:
```env
GEMINI_API_KEY=AIzaSyAKCpNj0J0i_-GCU2bZya7rEXjkO_OPk2Y
```

(Your key is already set correctly!)
