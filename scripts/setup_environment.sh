#!/bin/bash

# Environment setup script for AI Document Intelligence

set -e

echo "=========================================="
echo "AI Document Intelligence - Setup Script"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

required_version="3.10"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.10 or higher is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

# Create directory structure
echo ""
echo "Creating directory structure..."
mkdir -p dataset/{raw,ocr_text/{paddle,tesseract},labels,preprocessed}
mkdir -p src/{data_collection,ocr,utils}
mkdir -p notebooks
mkdir -p tests
mkdir -p reports
mkdir -p docs
mkdir -p scripts
mkdir -p logs
mkdir -p models
mkdir -p output

# Create .gitkeep files for empty directories
touch reports/.gitkeep
touch logs/.gitkeep
touch models/.gitkeep
touch output/.gitkeep

echo "Directory structure created."

# Check Tesseract installation
echo ""
echo "Checking Tesseract installation..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version 2>&1 | head -n1)
    echo "Tesseract installed: $tesseract_version"
else
    echo "Warning: Tesseract not found. Please install it manually:"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "  macOS: brew install tesseract"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

# Verify installations
echo ""
echo "Verifying Python packages..."
python3 << EOF
try:
    import numpy
    import pandas
    import cv2
    import PIL
    print("✓ Core packages installed")
except ImportError as e:
    print(f"✗ Error: {e}")

try:
    import pytesseract
    print("✓ Pytesseract installed")
except ImportError as e:
    print(f"✗ Pytesseract error: {e}")

try:
    from paddleocr import PaddleOCR
    print("✓ PaddleOCR installed")
except ImportError as e:
    print(f"✗ PaddleOCR error: {e}")
EOF

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To generate synthetic dataset, run:"
echo "  python scripts/generate_dataset.py --num-samples 200"
echo ""
