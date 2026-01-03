#!/usr/bin/env bash
echo "🔧 setting up cerrfix environment..."

if command -v conda >/dev/null 2>&1; then
    echo "📦 conda detected"
    echo "➡️  to create environment run:"
    echo "   conda env create -f environment.yml"
    conda env create -f environment.yml
    echo "   conda activate .cerrfix-env"
    conda activate .cerrfix-env
else
    echo "📦 conda not found"
    echo "➡️  using pip (recommended: virtualenv)"
    echo "   python3 -m venv .cerrfix-env"
    python3 -m venv .cerrfix-env
    echo "   source .cerrfix-env/bin/activate"
    source .cerrfix-env/bin/activate
    echo "   pip install -r requirements.txt"
    pip install -r requirements.txt

fi

