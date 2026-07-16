# Quick Import Checker - Run this first!
# This verifies your MLflow installation and imports

import sys

print("🔍 Checking MLflow Installation...")
print("=" * 60)

# Check Python version
print(f"Python version: {sys.version}")

# Check MLflow installation
try:
    import mlflow
    print(f"✅ MLflow installed: version {mlflow.__version__}")
except ImportError:
    print("❌ MLflow not installed!")
    print("   Fix: pip install mlflow")
    sys.exit(1)

# Check if version is 3.0+
version_parts = mlflow.__version__.split('.')
major_version = int(version_parts[0])

if major_version < 3:
    print(f"⚠️  Warning: MLflow {mlflow.__version__} detected")
    print(f"   Some features require MLflow 3.0+")
    print(f"   Upgrade: pip install --upgrade mlflow>=3.0.0")
else:
    print(f"✅ MLflow version is 3.x - Good!")

print("\n" + "=" * 60)
print("Testing Imports...")
print("=" * 60)

# Test 1: Basic imports
try:
    import pandas as pd
    print("✅ pandas imported")
except ImportError:
    print("❌ pandas not found - Install: pip install pandas")

# Test 2: GenAI evaluate import
try:
    from mlflow.genai import evaluate as genai_evaluate
    print("✅ mlflow.genai.evaluate imported")
except ImportError as e:
    print(f"❌ Cannot import mlflow.genai.evaluate: {e}")
    print("   This is required for new API")

# Test 3: Metrics import (the tricky one!)
try:
    from mlflow.metrics.genai import make_genai_metric
    print("✅ mlflow.metrics.genai.make_genai_metric imported")
except ImportError as e:
    print(f"❌ Cannot import from mlflow.metrics.genai: {e}")
    print("   Note: The import path is mlflow.metrics.genai (not mlflow.genai)")

# Test 4: Legacy imports (should still work)
try:
    from mlflow.metrics.genai import answer_relevance, faithfulness
    print("✅ Predefined metrics (answer_relevance, faithfulness) available")
except ImportError as e:
    print(f"⚠️  Predefined metrics not available: {e}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

# Show the correct import pattern
print("\n✅ CORRECT import pattern for your version:")
print("""
import mlflow
import pandas as pd
from mlflow.genai import evaluate as genai_evaluate
from mlflow.metrics.genai import make_genai_metric

# For predefined metrics:
from mlflow.metrics.genai import answer_relevance, faithfulness
""")

# Check for common issues
print("\n💡 Common Issues:")
print("  - ImportError? Run: pip install --upgrade mlflow>=3.0.0")
print("  - Still issues? Run: pip install --upgrade mlflow pandas openai")
print("  - API key issues? Set: OPENAI_API_KEY in your .env file")

print("\n" + "=" * 60)
print("🎯 Next Steps:")
print("=" * 60)
print("1. If all ✅ - Run: python test_updated_api.py")
print("2. If any ❌ - Follow the fix instructions above")
print("=" * 60)