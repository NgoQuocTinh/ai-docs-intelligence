"""Tests for data collection modules"""

import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image

from src.data_collection import DatasetOrganizer, InvoiceGenerator


class TestDatasetOrganizer:
    """Test cases for DatasetOrganizer class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def temp_image(self, temp_dir):
        """Create a temporary test image."""
        img = Image.new('RGB', (100, 100), color='white')
        img_path = Path(temp_dir) / "test_image.png"
        img.save(img_path)
        return str(img_path)
    
    def test_initialization(self, temp_dir):
        """Test DatasetOrganizer initialization."""
        organizer = DatasetOrganizer(base_path=temp_dir)
        
        assert organizer.base_path == Path(temp_dir)
        assert organizer.raw_dir.exists()
        assert organizer.labels_dir.exists()
        assert organizer.ocr_text_dir.exists()
        assert organizer.preprocessed_dir.exists()
    
    def test_add_document(self, temp_dir, temp_image):
        """Test adding document to dataset."""
        organizer = DatasetOrganizer(base_path=temp_dir)
        
        doc_id = organizer.add_document(
            temp_image,
            metadata={"test_field": "test_value"}
        )
        
        assert doc_id is not None
        assert doc_id in organizer.metadata["documents"]
        
        # Check if file was copied
        doc_metadata = organizer.get_document(doc_id)
        assert doc_metadata is not None
        assert doc_metadata["test_field"] == "test_value"
    
    def test_list_documents(self, temp_dir, temp_image):
        """Test listing documents."""
        organizer = DatasetOrganizer(base_path=temp_dir)
        
        # Add multiple documents
        doc_id1 = organizer.add_document(temp_image)
        doc_id2 = organizer.add_document(temp_image)
        
        documents = organizer.list_documents()
        assert len(documents) == 2
        
        # Test limit
        documents_limited = organizer.list_documents(limit=1)
        assert len(documents_limited) == 1
    
    def test_get_stats(self, temp_dir, temp_image):
        """Test getting dataset statistics."""
        organizer = DatasetOrganizer(base_path=temp_dir)
        
        organizer.add_document(temp_image)
        organizer.add_document(temp_image)
        
        stats = organizer.get_stats()
        assert stats["total_documents"] == 2
        assert stats["total_size_bytes"] > 0
        assert stats["avg_file_size_bytes"] > 0
    
    def test_remove_document(self, temp_dir, temp_image):
        """Test removing document."""
        organizer = DatasetOrganizer(base_path=temp_dir)
        
        doc_id = organizer.add_document(temp_image)
        assert organizer.get_document(doc_id) is not None
        
        success = organizer.remove_document(doc_id)
        assert success is True
        assert organizer.get_document(doc_id) is None


class TestInvoiceGenerator:
    """Test cases for InvoiceGenerator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_initialization(self, temp_dir):
        """Test InvoiceGenerator initialization."""
        generator = InvoiceGenerator(output_dir=temp_dir)
        
        assert generator.output_dir == Path(temp_dir)
        assert generator.labels_dir.exists()
    
    def test_generate_invoice_data(self, temp_dir):
        """Test generating invoice data."""
        generator = InvoiceGenerator(output_dir=temp_dir)
        
        invoice_data = generator.generate_invoice_data()
        
        # Check required fields
        assert "invoice_number" in invoice_data
        assert "invoice_date" in invoice_data
        assert "vendor_name" in invoice_data
        assert "total_amount" in invoice_data
        assert "currency" in invoice_data
        assert "line_items" in invoice_data
        assert len(invoice_data["line_items"]) > 0
        
        # Check numeric fields
        assert isinstance(invoice_data["total_amount"], float)
        assert invoice_data["total_amount"] > 0
    
    def test_render_invoice_image(self, temp_dir):
        """Test rendering invoice as image."""
        generator = InvoiceGenerator(output_dir=temp_dir)
        
        invoice_data = generator.generate_invoice_data()
        img = generator.render_invoice_image(invoice_data, add_noise=False)
        
        assert img is not None
        assert isinstance(img, Image.Image)
        assert img.size == (generator.width, generator.height)
    
    def test_render_invoice_with_noise(self, temp_dir):
        """Test rendering invoice with noise."""
        generator = InvoiceGenerator(output_dir=temp_dir)
        
        invoice_data = generator.generate_invoice_data()
        img = generator.render_invoice_image(invoice_data, add_noise=True)
        
        assert img is not None
        assert isinstance(img, Image.Image)
    
    def test_generate_dataset(self, temp_dir):
        """Test generating dataset."""
        generator = InvoiceGenerator(output_dir=temp_dir)
        
        num_samples = 5
        doc_ids = generator.generate_dataset(
            num_samples=num_samples,
            add_noise_probability=0.5
        )
        
        assert len(doc_ids) == num_samples
        
        # Check if files were created
        for doc_id in doc_ids:
            image_path = generator.output_dir / f"{doc_id}.png"
            label_path = generator.labels_dir / f"{doc_id}.json"
            
            assert image_path.exists()
            assert label_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
