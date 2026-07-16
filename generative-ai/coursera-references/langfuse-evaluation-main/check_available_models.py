#!/usr/bin/env python3
"""
Check which Gemini models are available with your API key
"""
import os
import sys

# Check if google-generativeai is installed
try:
    import google.generativeai as genai
except ImportError:
    print("❌ google-generativeai not installed")
    print("   Install with: pip install google-generativeai")
    sys.exit(1)

# Load API key
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not set")
    sys.exit(1)

print("🔍 Checking available Gemini models...")
print(f"   API Key: {api_key[:10]}...")
print()

# Configure
genai.configure(api_key=api_key)

# List models
print("=" * 80)
print("AVAILABLE MODELS (with generateContent support)")
print("=" * 80)
print()

available_models = []
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        available_models.append(model.name)
        print(f"✅ {model.name}")
        print(f"   Display name: {model.display_name}")
        print(f"   Description: {model.description[:100]}...")
        print()

print("=" * 80)
print(f"Total: {len(available_models)} models available")
print("=" * 80)
print()

# Recommendations
print("💡 RECOMMENDATIONS:")
print()

if 'models/gemini-1.5-pro' in available_models:
    print("✅ Use: gemini-1.5-pro (stable Pro model)")
elif 'models/gemini-1.5-pro-latest' in available_models:
    print("✅ Use: gemini-1.5-pro-latest")
elif 'models/gemini-pro' in available_models:
    print("⚠️  Use: gemini-pro (older but stable)")
else:
    print("❌ No stable Pro models found")

print()

if 'models/gemini-1.5-flash' in available_models:
    print("✅ Use: gemini-1.5-flash (stable Flash model)")
elif 'models/gemini-1.5-flash-latest' in available_models:
    print("✅ Use: gemini-1.5-flash-latest")
elif 'models/gemini-2.0-flash-exp' in available_models:
    print("⚠️  Use: gemini-2.0-flash-exp (experimental, v1beta only)")

print()
print("=" * 80)
print("NOTE: API key access uses v1beta endpoint")
print("For stable v1 API, use Vertex AI with GCP project")
print("=" * 80)
