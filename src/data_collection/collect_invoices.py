"""Dataset organizer for invoice documents"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..utils.file_utils import write_json, read_json, ensure_dir
from ..utils.logger import setup_logger


class DatasetOrganizer:
    """Organizes and manages invoice dataset with metadata."""
    
    def __init__(self, base_path: str = "dataset"):
        """
        Initialize dataset organizer.
        
        Args:
            base_path: Base directory for dataset
        """
        self.base_path = Path(base_path)
        self.logger = setup_logger(__name__)
        
        # Initialize directory structure
        self.raw_dir = self.base_path / "raw"
        self.labels_dir = self.base_path / "labels"
        self.ocr_text_dir = self.base_path / "ocr_text"
        self.preprocessed_dir = self.base_path / "preprocessed"
        
        self._create_directories()
        
        # Metadata file
        self.metadata_file = self.base_path / "dataset_metadata.json"
        self.metadata = self._load_metadata()
        
        self.logger.info(f"DatasetOrganizer initialized at {self.base_path}")
    
    def _create_directories(self) -> None:
        """Create necessary directory structure."""
        ensure_dir(self.raw_dir)
        ensure_dir(self.labels_dir)
        ensure_dir(self.ocr_text_dir / "paddle")
        ensure_dir(self.ocr_text_dir / "tesseract")
        ensure_dir(self.preprocessed_dir)
        self.logger.info("Dataset directories created")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load existing metadata or create new."""
        if self.metadata_file.exists():
            try:
                return read_json(self.metadata_file)
            except Exception as e:
                self.logger.warning(f"Failed to load metadata: {e}. Creating new.")
        
        return {
            "dataset_name": "invoice_dataset",
            "created_at": datetime.now().isoformat(),
            "documents": {},
            "statistics": {
                "total_documents": 0,
                "total_size_bytes": 0
            }
        }
    
    def _save_metadata(self) -> None:
        """Save metadata to file."""
        write_json(self.metadata, self.metadata_file)
    
    def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add document to dataset with metadata.
        
        Args:
            file_path: Path to document file
            metadata: Document metadata (optional)
        
        Returns:
            Document ID
        
        Raises:
            FileNotFoundError: If source file doesn't exist
        """
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Generate document ID
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Copy file to raw directory with document ID
        file_extension = source_path.suffix
        dest_path = self.raw_dir / f"{doc_id}{file_extension}"
        shutil.copy2(source_path, dest_path)
        
        # Create metadata for document
        doc_metadata = {
            "doc_id": doc_id,
            "filename": source_path.name,
            "file_extension": file_extension,
            "added_at": datetime.now().isoformat(),
            "file_size_bytes": dest_path.stat().st_size,
            "file_path": str(dest_path.relative_to(self.base_path))
        }
        
        # Add custom metadata if provided
        if metadata:
            doc_metadata.update(metadata)
        
        # Save document-specific metadata
        doc_metadata_file = self.labels_dir / f"{doc_id}_metadata.json"
        write_json(doc_metadata, doc_metadata_file)
        
        # Update dataset metadata
        self.metadata["documents"][doc_id] = doc_metadata
        self.metadata["statistics"]["total_documents"] += 1
        self.metadata["statistics"]["total_size_bytes"] += doc_metadata["file_size_bytes"]
        self.metadata["statistics"]["last_updated"] = datetime.now().isoformat()
        self._save_metadata()
        
        self.logger.info(f"Added document: {doc_id} ({source_path.name})")
        return doc_id
    
    def list_documents(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all documents with metadata.
        
        Args:
            limit: Maximum number of documents to return (optional)
        
        Returns:
            List of document metadata dictionaries
        """
        documents = list(self.metadata["documents"].values())
        if limit:
            documents = documents[:limit]
        return documents
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for specific document.
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document metadata or None if not found
        """
        return self.metadata["documents"].get(doc_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get dataset statistics.
        
        Returns:
            Dictionary containing dataset statistics
        """
        stats = self.metadata["statistics"].copy()
        
        # Add additional computed statistics
        if stats["total_documents"] > 0:
            stats["avg_file_size_bytes"] = (
                stats["total_size_bytes"] / stats["total_documents"]
            )
        else:
            stats["avg_file_size_bytes"] = 0
        
        # Count files in each directory
        stats["files_in_raw"] = len(list(self.raw_dir.glob("*")))
        stats["files_in_labels"] = len(list(self.labels_dir.glob("*.json")))
        stats["files_in_preprocessed"] = len(list(self.preprocessed_dir.glob("*")))
        
        return stats
    
    def remove_document(self, doc_id: str) -> bool:
        """
        Remove document from dataset.
        
        Args:
            doc_id: Document ID to remove
        
        Returns:
            True if removed successfully, False if not found
        """
        if doc_id not in self.metadata["documents"]:
            self.logger.warning(f"Document not found: {doc_id}")
            return False
        
        doc_metadata = self.metadata["documents"][doc_id]
        
        # Remove files
        file_path = self.base_path / doc_metadata["file_path"]
        if file_path.exists():
            file_path.unlink()
        
        metadata_file = self.labels_dir / f"{doc_id}_metadata.json"
        if metadata_file.exists():
            metadata_file.unlink()
        
        # Update metadata
        self.metadata["statistics"]["total_documents"] -= 1
        self.metadata["statistics"]["total_size_bytes"] -= doc_metadata["file_size_bytes"]
        del self.metadata["documents"][doc_id]
        self._save_metadata()
        
        self.logger.info(f"Removed document: {doc_id}")
        return True
