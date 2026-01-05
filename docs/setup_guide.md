# Setup Guide - AI Document Intelligence

## Prerequisites

### Required Software
- **Python 3.10+**: The project requires Python 3.10 or higher
- **Tesseract OCR**: For text extraction
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### Recommended
- **CUDA Toolkit** (optional): For GPU acceleration with PaddleOCR
- **8GB RAM minimum**: For processing large documents
- **Storage**: At least 5GB free space for datasets and models

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/NgoQuocTinh/ai-docs-intelligence.git
cd ai-docs-intelligence
```

### 2. Run Setup Script

The easiest way to set up the environment is using the provided setup script:

```bash
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh
```

This script will:
- Check Python version
- Create a virtual environment
- Install all dependencies
- Create directory structure
- Verify installations

### 3. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4. Verify Installation

```python
python3 << EOF
import numpy
import pandas
import cv2
from PIL import Image
import pytesseract
from paddleocr import PaddleOCR

print("✓ All packages installed successfully!")
EOF
```

## Quick Start

### Generate Synthetic Dataset

Generate 200 synthetic invoices for testing:

```bash
python scripts/generate_dataset.py --num-samples 200 --output dataset/raw
```

Options:
- `--num-samples`: Number of invoices to generate (default: 200)
- `--output`: Output directory (default: dataset/raw)
- `--locale`: Locale for fake data (default: en_US, options: en_US, vi_VN)
- `--noise-prob`: Probability of adding noise (default: 0.5)

### Run OCR on Dataset

```python
from src.ocr import OCREngine

# Initialize OCR engine
engine = OCREngine(engine="paddle", use_gpu=False)

# Process single image
result = engine.process_image("dataset/raw/sample.png")

# Batch process
results = engine.batch_process(
    input_dir="dataset/raw",
    output_dir="dataset/ocr_text/paddle"
)
```

### Run Error Analysis

```python
from src.ocr import OCRErrorAnalyzer

# Initialize analyzer
analyzer = OCRErrorAnalyzer(
    labels_dir="dataset/labels",
    ocr_results_dir="dataset/ocr_text"
)

# Generate error report
report = analyzer.generate_error_report(engine="paddle")

# Save report
analyzer.save_report(report, "reports/paddle_error_report.json")
```

## Project Structure

```
ai-docs-intelligence/
├── configs/              # Configuration files
├── dataset/              # Dataset storage
│   ├── raw/             # Original documents
│   ├── labels/          # Ground truth labels
│   ├── ocr_text/        # OCR outputs
│   └── preprocessed/    # Processed images
├── src/                 # Source code
│   ├── data_collection/ # Data collection modules
│   ├── ocr/            # OCR modules
│   └── utils/          # Utility modules
├── notebooks/           # Jupyter notebooks
├── tests/              # Unit tests
├── scripts/            # Utility scripts
├── docs/               # Documentation
└── reports/            # Analysis reports
```

## Troubleshooting

### Tesseract Not Found

If you get a "tesseract not found" error:

1. Verify installation: `tesseract --version`
2. If not installed, follow the installation steps for your OS
3. On Windows, add Tesseract to PATH

### PaddleOCR Import Error

If PaddleOCR fails to import:

```bash
pip install paddlepaddle==2.5.0 paddleocr==2.7.0
```

For GPU support:
```bash
pip install paddlepaddle-gpu==2.5.0
```

### Memory Issues

If you encounter memory errors:

1. Reduce batch size in configurations
2. Process images in smaller batches
3. Use lower resolution images

### Permission Errors

If you get permission errors:

```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

## Running Tests

Run unit tests:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_data_collection.py -v
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `DATA_DIR`: Dataset directory path
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEFAULT_OCR_ENGINE`: Default OCR engine (paddle or tesseract)

## Next Steps

1. **Explore Data**: Open `notebooks/01_data_exploration.ipynb`
2. **Run OCR Baseline**: Open `notebooks/02_ocr_baseline.ipynb`
3. **Analyze Errors**: Open `notebooks/03_error_analysis.ipynb`
4. **Read Documentation**: Check `docs/week1_report.md` for detailed findings

## Getting Help

- Check existing documentation in `docs/`
- Review notebooks for examples
- Run tests to verify setup: `pytest tests/ -v`
- Check logs in `logs/` directory

## Additional Resources

- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [Tesseract OCR Documentation](https://github.com/tesseract-ocr/tesseract)
- [Pillow Documentation](https://pillow.readthedocs.io/)
