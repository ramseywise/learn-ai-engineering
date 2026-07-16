#!/bin/bash

# Conecta Evaluation System Setup Script

echo "🚀 Setting up Conecta Evaluation System..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Set your API key:"
echo "   export GEMINI_API_KEY='your-api-key-here'"
echo ""
echo "   OR for Vertex AI:"
echo "   export VERTEX_PROJECT_ID='your-project-id'"
echo ""
echo "2. Start Jupyter:"
echo "   jupyter notebook notebooks/conecta_hallucination_analysis.ipynb"
echo ""
echo "3. Run the analysis!"
echo ""
echo "📚 See README.md for full documentation"
echo ""
