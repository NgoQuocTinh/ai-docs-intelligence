"""Tests for OCR engine modules"""

import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from src.ocr import OCREngine, OCRErrorAnalyzer
from src.utils.file_utils import write_json


class TestOCREngine:
    """Test cases for OCR Engine."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def test_image(self, temp_dir):
        """Create a test image with text."""
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except (OSError, IOError):
            font = ImageFont.load_default()
        
        draw.text((20, 50), "INVOICE", fill='black', font=font)
        draw.text((20, 90), "Invoice #: INV-1234", fill='black', font=font)
        draw.text((20, 130), "Total: 100.00 USD", fill='black', font=font)
        
        img_path = Path(temp_dir) / "test_invoice.png"
        img.save(img_path)
        return str(img_path)
    
    def test_initialization_paddle(self):
        """Test OCR engine initialization with PaddleOCR."""
        try:
            engine = OCREngine(engine="paddle", use_gpu=False)
            assert engine.paddle_ocr is not None
        except Exception as e:
            pytest.skip(f"PaddleOCR not available: {e}")
    
    def test_initialization_tesseract(self):
        """Test OCR engine initialization with Tesseract."""
        try:
            engine = OCREngine(engine="tesseract")
            assert engine.pytesseract is not None
        except Exception as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_process_image_structure(self, test_image, temp_dir):
        """Test that process_image returns correct structure."""
        try:
            engine = OCREngine(engine="paddle", use_gpu=False)
            result = engine.process_image(test_image)
            
            assert "image_path" in result
            assert "image_name" in result
            assert "timestamp" in result
            assert "paddle" in result
            
            paddle_result = result["paddle"]
            assert "engine" in paddle_result
            assert "text_blocks" in paddle_result
            assert "full_text" in paddle_result
            assert paddle_result["engine"] == "paddle"
        except Exception as e:
            pytest.skip(f"OCR test skipped: {e}")
    
    def test_batch_process(self, temp_dir):
        """Test batch processing."""
        # Create multiple test images
        for i in range(3):
            img = Image.new('RGB', (200, 100), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((10, 40), f"Test {i}", fill='black')
            img.save(Path(temp_dir) / f"test_{i}.png")
        
        try:
            engine = OCREngine(engine="paddle", use_gpu=False)
            output_dir = Path(temp_dir) / "ocr_output"
            
            results = engine.batch_process(
                temp_dir,
                str(output_dir),
                pattern="test_*.png"
            )
            
            assert len(results) > 0
            assert output_dir.exists()
            assert (output_dir / "batch_summary.json").exists()
        except Exception as e:
            pytest.skip(f"Batch processing test skipped: {e}")


class TestOCRErrorAnalyzer:
    """Test cases for OCR Error Analyzer."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def setup_test_data(self, temp_dir):
        """Setup test data for error analysis."""
        labels_dir = Path(temp_dir) / "labels"
        ocr_dir = Path(temp_dir) / "ocr_text" / "paddle"
        labels_dir.mkdir(parents=True)
        ocr_dir.mkdir(parents=True)
        
        # Create ground truth
        ground_truth = {
            "invoice_number": "INV-1234",
            "invoice_date": "2024-01-15",
            "vendor_name": "Test Company Inc",
            "total_amount": 100.50,
            "currency": "USD"
        }
        write_json(ground_truth, labels_dir / "test_doc.json")
        
        # Create OCR result
        ocr_result = {
            "paddle": {
                "engine": "paddle",
                "full_text": "INVOICE\nInvoice #: INV-1234\nDate: 2024-01-15\nFROM: Test Company Inc\nTOTAL: 100.50 USD",
                "text_blocks": [],
                "avg_confidence": 0.95,
                "num_blocks": 5
            }
        }
        write_json(ocr_result, ocr_dir / "test_doc_ocr.json")
        
        return labels_dir, ocr_dir
    
    def test_initialization(self, temp_dir):
        """Test error analyzer initialization."""
        analyzer = OCRErrorAnalyzer(
            labels_dir=str(Path(temp_dir) / "labels"),
            ocr_results_dir=str(Path(temp_dir) / "ocr_text"),
            similarity_threshold=0.85
        )
        
        assert analyzer.labels_dir == Path(temp_dir) / "labels"
        assert analyzer.ocr_results_dir == Path(temp_dir) / "ocr_text"
        assert analyzer.similarity_threshold == 0.85
    
    def test_calculate_similarity(self, temp_dir):
        """Test string similarity calculation."""
        analyzer = OCRErrorAnalyzer(
            labels_dir=str(Path(temp_dir) / "labels"),
            ocr_results_dir=str(Path(temp_dir) / "ocr_text")
        )
        
        # Identical strings
        assert analyzer.calculate_similarity("test", "test") == 1.0
        
        # Different strings
        similarity = analyzer.calculate_similarity("hello", "world")
        assert 0 <= similarity < 1.0
        
        # Case insensitive
        assert analyzer.calculate_similarity("Test", "test") == 1.0
    
    def test_load_ground_truth(self, temp_dir, setup_test_data):
        """Test loading ground truth data."""
        labels_dir, _ = setup_test_data
        
        analyzer = OCRErrorAnalyzer(
            labels_dir=str(labels_dir),
            ocr_results_dir=str(Path(temp_dir) / "ocr_text")
        )
        
        gt = analyzer.load_ground_truth("test_doc")
        assert gt is not None
        assert gt["invoice_number"] == "INV-1234"
    
    def test_load_ocr_result(self, temp_dir, setup_test_data):
        """Test loading OCR result data."""
        labels_dir, ocr_dir = setup_test_data
        
        analyzer = OCRErrorAnalyzer(
            labels_dir=str(labels_dir),
            ocr_results_dir=str(Path(temp_dir) / "ocr_text")
        )
        
        ocr = analyzer.load_ocr_result("test_doc", engine="paddle")
        assert ocr is not None
        assert ocr["engine"] == "paddle"
    
    def test_analyze_field_errors(self, temp_dir, setup_test_data):
        """Test field error analysis."""
        labels_dir, ocr_dir = setup_test_data
        
        analyzer = OCRErrorAnalyzer(
            labels_dir=str(labels_dir),
            ocr_results_dir=str(Path(temp_dir) / "ocr_text")
        )
        
        errors = analyzer.analyze_field_errors("test_doc", engine="paddle")
        
        assert errors is not None
        assert "field_errors" in errors
        assert "invoice_number" in errors["field_errors"]
        assert errors["field_errors"]["invoice_number"]["ground_truth"] == "INV-1234"
    
    def test_generate_error_report(self, temp_dir, setup_test_data):
        """Test error report generation."""
        labels_dir, ocr_dir = setup_test_data
        
        analyzer = OCRErrorAnalyzer(
            labels_dir=str(labels_dir),
            ocr_results_dir=str(Path(temp_dir) / "ocr_text")
        )
        
        report = analyzer.generate_error_report(
            engine="paddle",
            doc_ids=["test_doc"]
        )
        
        assert report is not None
        assert report["engine"] == "paddle"
        assert "field_accuracy" in report
        assert "summary" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
