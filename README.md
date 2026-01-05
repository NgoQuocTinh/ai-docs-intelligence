# AI Document Intelligence

A comprehensive AI-powered document intelligence system for automated invoice processing, text extraction, and data analysis.

## 🎯 Project Overview

This project implements a complete pipeline for intelligent document processing with focus on invoice analysis:

- **OCR Processing**: Multiple OCR engines (PaddleOCR, Tesseract)
- **Data Extraction**: Automated field extraction from invoices
- **Error Analysis**: Comprehensive accuracy metrics and error tracking
- **Synthetic Data**: Realistic invoice generation for testing
- **Modular Design**: Easy to extend and customize

## 📅 30-Day Roadmap

### Week 1: Data Ownership & Infrastructure ✅
- [x] Complete project structure setup
- [x] Dataset organization system
- [x] OCR baseline (PaddleOCR + Tesseract)
- [x] Synthetic invoice generator (200+ samples)
- [x] Error analysis framework
- [x] Unit tests and documentation

### Week 2: Preprocessing & Features (In Progress)
- [ ] Advanced image preprocessing pipeline
- [ ] Feature engineering for field extraction
- [ ] OCR optimization and parameter tuning
- [ ] Enhanced error pattern analysis
- [ ] Performance benchmarking

### Week 3: Model Training
- [ ] Custom field extraction model
- [ ] Layout analysis model
- [ ] Model evaluation and validation
- [ ] Hyperparameter optimization

### Week 4: Production & Deployment
- [ ] REST API development
- [ ] Web interface (Streamlit)
- [ ] Docker containerization
- [ ] Documentation and demo
- [ ] Performance optimization

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Tesseract OCR
- 8GB RAM (minimum)

### Installation

```bash
# Clone repository
git clone https://github.com/NgoQuocTinh/ai-docs-intelligence.git
cd ai-docs-intelligence

# Run setup script
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh

# Activate virtual environment
source venv/bin/activate
```

### Generate Synthetic Dataset

```bash
python scripts/generate_dataset.py --num-samples 200
```

### Run OCR Processing

```python
from src.ocr import OCREngine

engine = OCREngine(engine="paddle")
result = engine.process_image("dataset/raw/sample.png")
print(result["paddle"]["full_text"])
```

### Run Error Analysis

```python
from src.ocr import OCRErrorAnalyzer

analyzer = OCRErrorAnalyzer()
report = analyzer.generate_error_report(engine="paddle")
analyzer.save_report(report, "reports/error_report.json")
```

## 📁 Project Structure

```
ai-docs-intelligence/
├── configs/              # Configuration files
│   ├── invoice_schema.json
│   └── config.yaml
├── dataset/              # Dataset storage
│   ├── raw/             # Original documents
│   ├── labels/          # Ground truth labels
│   ├── ocr_text/        # OCR outputs
│   └── preprocessed/    # Processed images
├── src/                 # Source code
│   ├── data_collection/ # Dataset management
│   │   ├── collect_invoices.py
│   │   └── generate_synthetic.py
│   ├── ocr/            # OCR processing
│   │   ├── ocr_engine.py
│   │   └── error_analysis.py
│   └── utils/          # Utilities
│       ├── logger.py
│       └── file_utils.py
├── notebooks/           # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_ocr_baseline.ipynb
│   └── 03_error_analysis.ipynb
├── tests/              # Unit tests
│   ├── test_data_collection.py
│   └── test_ocr_engine.py
├── scripts/            # Automation scripts
│   ├── setup_environment.sh
│   └── generate_dataset.py
├── docs/               # Documentation
│   ├── setup_guide.md
│   └── week1_report.md
└── reports/            # Analysis reports
```

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.10+**: Primary language
- **PaddleOCR**: Advanced OCR engine
- **Tesseract**: Traditional OCR engine
- **OpenCV**: Image processing
- **Pillow**: Image manipulation

### ML/AI Frameworks
- **PyTorch**: Deep learning
- **Transformers**: NLP models
- **scikit-learn**: ML utilities

### Data & APIs
- **Pandas/NumPy**: Data processing
- **FastAPI**: REST API
- **Streamlit**: Web interface
- **SQLAlchemy**: Database ORM

### Testing & Quality
- **pytest**: Unit testing
- **Faker**: Synthetic data
- **pydantic**: Data validation

## 📊 Features

### Data Collection
- **DatasetOrganizer**: Manage document datasets with metadata
- **InvoiceGenerator**: Generate realistic synthetic invoices
- Supports multiple locales and noise levels

### OCR Processing
- **Dual Engine Support**: PaddleOCR and Tesseract
- **Batch Processing**: Process multiple documents efficiently
- **Structured Output**: JSON format with bounding boxes and confidence scores

### Error Analysis
- **Field-Level Accuracy**: Track accuracy for critical fields
- **String Similarity**: Fuzzy matching for extracted text
- **Comprehensive Reports**: Detailed error analysis with metrics

## 📈 Performance

### Dataset Metrics
- 200+ synthetic invoices generated
- Multiple noise levels for robustness testing
- Complete ground truth labels

### OCR Metrics
(Updated after baseline testing)
- Field extraction accuracy
- Processing speed
- Confidence scores

## 🧪 Testing

Run unit tests:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test
pytest tests/test_data_collection.py -v
```

Target: >70% code coverage

## 📚 Documentation

- **Setup Guide**: [docs/setup_guide.md](docs/setup_guide.md)
- **Week 1 Report**: [docs/week1_report.md](docs/week1_report.md)
- **API Documentation**: Auto-generated from docstrings
- **Notebooks**: Interactive examples in `notebooks/`

## 🤝 Contributing

This is a learning and development project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation

## 🔍 Troubleshooting

See [docs/setup_guide.md](docs/setup_guide.md) for common issues and solutions.

## 📄 License

This project is developed for educational and research purposes.

## 👥 Team

AI Document Intelligence Team

## 🙏 Acknowledgments

- PaddleOCR team for excellent OCR engine
- Tesseract OCR community
- Open source contributors

## 📬 Contact

For questions or issues, please open a GitHub issue.

---

**Status**: Week 1 Complete ✅  
**Last Updated**: January 2024  
**Version**: 0.1.0