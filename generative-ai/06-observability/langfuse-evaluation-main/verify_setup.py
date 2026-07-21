#!/usr/bin/env python3
"""
Verify Conecta Evaluation System Setup
Run this to check if everything is configured correctly
"""

import sys
import os

print("="*80)
print("🔍 CONECTA EVALUATION SYSTEM - SETUP VERIFICATION")
print("="*80)
print()

# Check Python version
print("1. Checking Python version...")
python_version = sys.version_info
if python_version >= (3, 10):
    print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
else:
    print(f"   ⚠️  Python {python_version.major}.{python_version.minor}.{python_version.micro} (recommend 3.10+)")
print()

# Check dependencies
print("2. Checking dependencies...")
required_packages = [
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
    'jupyter',
]

optional_packages = [
    ('google.generativeai', 'Gemini API'),
    ('vertexai', 'Vertex AI'),
    ('dotenv', 'Environment variables'),
]

missing = []
for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - MISSING")
        missing.append(package)

print()
print("   Optional packages:")
for package, name in optional_packages:
    try:
        __import__(package)
        print(f"   ✅ {package} ({name})")
    except ImportError:
        print(f"   ⚠️  {package} ({name}) - optional")

if missing:
    print()
    print(f"   ❌ Missing {len(missing)} required package(s)")
    print(f"   Run: pip install -r requirements.txt")
else:
    print()
    print("   ✅ All required packages installed")
print()

# Check environment variables
print("3. Checking environment configuration...")

# Try to load .env file
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"   ✅ .env file found")
    else:
        print(f"   ⚠️  .env file not found (will use system environment)")
except ImportError:
    print(f"   ⚠️  python-dotenv not installed (will use system environment)")
print()

gemini_key = os.getenv('GEMINI_API_KEY')
vertex_project = os.getenv('VERTEX_PROJECT_ID')

has_credentials = False

if gemini_key:
    if gemini_key and gemini_key != 'your-gemini-api-key-here':
        print(f"   ✅ GEMINI_API_KEY found: {gemini_key[:10]}..." if len(gemini_key) > 10 else "   ✅ GEMINI_API_KEY found")
        has_credentials = True
    else:
        print(f"   ⚠️  GEMINI_API_KEY is set but appears to be placeholder")
else:
    print(f"   ❌ GEMINI_API_KEY not set")

if vertex_project:
    if vertex_project != 'your-project-id-here':
        print(f"   ✅ VERTEX_PROJECT_ID found: {vertex_project}")
        has_credentials = True
    else:
        print(f"   ⚠️  VERTEX_PROJECT_ID is set but appears to be placeholder")
else:
    print(f"   ⚠️  VERTEX_PROJECT_ID not set")

print()

# Check data files
print("4. Checking data files...")
data_files = [
    'df_merged_final_oct_v3.csv',
    'df_merged_genesys (1).csv',
    '1758819667267-lf-traces-export-cm38vdgjp005z3hq2htm5f0mx.csv',
    'base_conocimiento_ajustada_cargue_produccion_v2 (1).csv'
]

all_files_present = True
for file in data_files:
    if os.path.exists(file):
        size_mb = os.path.getsize(file) / 1024 / 1024
        print(f"   ✅ {file} ({size_mb:.1f} MB)")
    else:
        print(f"   ❌ {file} - NOT FOUND")
        all_files_present = False

print()

# Check project structure
print("5. Checking project structure...")
required_dirs = ['src', 'notebooks']
for dir in required_dirs:
    if os.path.isdir(dir):
        print(f"   ✅ {dir}/")
    else:
        print(f"   ❌ {dir}/ - NOT FOUND")

print()

# Final verdict
print("="*80)
print("📊 FINAL VERDICT")
print("="*80)
print()

if not missing and has_credentials and all_files_present:
    print("✅ ✅ ✅  EVERYTHING IS READY! ✅ ✅ ✅")
    print()
    print("Next steps:")
    print("1. Start Jupyter: jupyter notebook notebooks/conecta_hallucination_analysis.ipynb")
    print("2. Run the analysis!")
else:
    print("⚠️  SETUP INCOMPLETE")
    print()
    print("Actions needed:")

    if missing:
        print(f"   → Install dependencies: pip install -r requirements.txt")

    if not has_credentials:
        print(f"   → Set up API credentials:")
        print(f"     1. Edit .env file")
        print(f"     2. Add your GEMINI_API_KEY")
        print(f"     Get key from: https://makersuite.google.com/app/apikey")

    if not all_files_present:
        print(f"   → Ensure all CSV data files are in the project root")

print()
print("="*80)
print("For help, see: QUICKSTART.md")
print("="*80)
