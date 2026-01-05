"""OCR error analyzer for comparing OCR results with ground truth"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher
import re

from ..utils.file_utils import read_json, write_json
from ..utils.logger import setup_logger


class OCRErrorAnalyzer:
    """Analyzes OCR errors by comparing with ground truth labels."""
    
    def __init__(
        self,
        labels_dir: str = "dataset/labels",
        ocr_results_dir: str = "dataset/ocr_text"
    ):
        """
        Initialize error analyzer.
        
        Args:
            labels_dir: Directory containing ground truth labels
            ocr_results_dir: Directory containing OCR results
        """
        self.labels_dir = Path(labels_dir)
        self.ocr_results_dir = Path(ocr_results_dir)
        self.logger = setup_logger(__name__)
        
        # Key fields to analyze
        self.key_fields = [
            "invoice_number",
            "invoice_date",
            "vendor_name",
            "total_amount"
        ]
        
        self.logger.info("OCRErrorAnalyzer initialized")
    
    def load_ground_truth(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Load ground truth label for document.
        
        Args:
            doc_id: Document ID
        
        Returns:
            Ground truth data or None if not found
        """
        label_file = self.labels_dir / f"{doc_id}.json"
        if not label_file.exists():
            self.logger.warning(f"Ground truth not found: {doc_id}")
            return None
        
        try:
            return read_json(label_file)
        except Exception as e:
            self.logger.error(f"Failed to load ground truth for {doc_id}: {e}")
            return None
    
    def load_ocr_result(
        self,
        doc_id: str,
        engine: str = "paddle"
    ) -> Optional[Dict[str, Any]]:
        """
        Load OCR result for document.
        
        Args:
            doc_id: Document ID
            engine: OCR engine name ("paddle" or "tesseract")
        
        Returns:
            OCR result data or None if not found
        """
        ocr_file = self.ocr_results_dir / engine / f"{doc_id}_ocr.json"
        if not ocr_file.exists():
            self.logger.warning(f"OCR result not found: {doc_id} ({engine})")
            return None
        
        try:
            data = read_json(ocr_file)
            return data.get(engine)
        except Exception as e:
            self.logger.error(f"Failed to load OCR result for {doc_id}: {e}")
            return None
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate string similarity using SequenceMatcher.
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score (0-1)
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        s1 = str(str1).lower().strip()
        s2 = str(str2).lower().strip()
        
        return SequenceMatcher(None, s1, s2).ratio()
    
    def _extract_field_from_ocr(
        self,
        ocr_result: Dict[str, Any],
        field_name: str,
        ground_truth_value: Any
    ) -> str:
        """
        Extract field value from OCR full text.
        
        Args:
            ocr_result: OCR result dictionary
            field_name: Field name to extract
            ground_truth_value: Ground truth value for reference
        
        Returns:
            Extracted field value
        """
        full_text = ocr_result.get("full_text", "")
        
        # Simple extraction based on field patterns
        if field_name == "invoice_number":
            # Look for patterns like "Invoice #: INV-1234" or "INV-1234"
            patterns = [
                r'invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
                r'(INV-\d+)',
                r'invoice\s+number\s*:?\s*([A-Z0-9-]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        elif field_name == "invoice_date":
            # Look for date patterns
            patterns = [
                r'date\s*:?\s*(\d{4}-\d{2}-\d{2})',
                r'(\d{4}-\d{2}-\d{2})',
                r'date\s*:?\s*(\d{2}/\d{2}/\d{4})'
            ]
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        elif field_name == "vendor_name":
            # Look for vendor name after "FROM:" or at the beginning
            patterns = [
                r'from\s*:?\s*([^\n]+)',
                r'^([A-Z][A-Za-z\s&,\.]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match.group(1).strip()
        
        elif field_name == "total_amount":
            # Look for total amount
            patterns = [
                r'total\s*:?\s*(\d+\.?\d*)',
                r'(\d+\.\d{2})\s*[A-Z]{3}$'
            ]
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        # Fallback: search for similar text in full text
        gt_str = str(ground_truth_value).lower()
        for line in full_text.split('\n'):
            if gt_str in line.lower():
                return line.strip()
        
        return ""
    
    def analyze_field_errors(
        self,
        doc_id: str,
        engine: str = "paddle"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze errors for important fields.
        
        Args:
            doc_id: Document ID
            engine: OCR engine name
        
        Returns:
            Dictionary containing field-level error analysis
        """
        # Load ground truth and OCR result
        ground_truth = self.load_ground_truth(doc_id)
        ocr_result = self.load_ocr_result(doc_id, engine)
        
        if not ground_truth or not ocr_result:
            return None
        
        field_errors = {}
        
        for field in self.key_fields:
            gt_value = ground_truth.get(field, "")
            
            # Extract field from OCR text
            ocr_value = self._extract_field_from_ocr(ocr_result, field, gt_value)
            
            # Calculate similarity
            similarity = self.calculate_similarity(str(gt_value), ocr_value)
            
            field_errors[field] = {
                "ground_truth": str(gt_value),
                "ocr_extracted": ocr_value,
                "similarity": similarity,
                "is_correct": similarity >= 0.85  # Threshold for correctness
            }
        
        return {
            "doc_id": doc_id,
            "engine": engine,
            "field_errors": field_errors,
            "avg_confidence": ocr_result.get("avg_confidence", 0.0),
            "num_blocks": ocr_result.get("num_blocks", 0)
        }
    
    def generate_error_report(
        self,
        engine: str = "paddle",
        doc_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive error report.
        
        Args:
            engine: OCR engine name
            doc_ids: List of document IDs to analyze (if None, analyze all)
        
        Returns:
            Dictionary containing error report
        """
        self.logger.info(f"Generating error report for {engine}")
        
        # Get document IDs if not provided
        if doc_ids is None:
            label_files = list(self.labels_dir.glob("*.json"))
            doc_ids = [f.stem for f in label_files if not f.stem.endswith("_metadata")]
        
        all_errors = []
        
        for doc_id in doc_ids:
            errors = self.analyze_field_errors(doc_id, engine)
            if errors:
                all_errors.append(errors)
        
        # Calculate overall statistics
        field_accuracy = self._calculate_field_accuracy(all_errors)
        
        report = {
            "engine": engine,
            "total_documents": len(doc_ids),
            "analyzed_documents": len(all_errors),
            "field_accuracy": field_accuracy,
            "detailed_errors": all_errors[:10],  # Include first 10 for review
            "summary": {
                "avg_confidence": sum(e["avg_confidence"] for e in all_errors) / len(all_errors) if all_errors else 0.0,
                "avg_blocks_per_doc": sum(e["num_blocks"] for e in all_errors) / len(all_errors) if all_errors else 0.0
            }
        }
        
        return report
    
    def _calculate_field_accuracy(
        self,
        all_errors: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate per-field accuracy.
        
        Args:
            all_errors: List of error analysis results
        
        Returns:
            Dictionary of field accuracies
        """
        field_stats = {field: {"correct": 0, "total": 0} for field in self.key_fields}
        
        for error_data in all_errors:
            for field, field_error in error_data["field_errors"].items():
                if field in field_stats:
                    field_stats[field]["total"] += 1
                    if field_error["is_correct"]:
                        field_stats[field]["correct"] += 1
        
        field_accuracy = {}
        for field, stats in field_stats.items():
            if stats["total"] > 0:
                field_accuracy[field] = stats["correct"] / stats["total"]
            else:
                field_accuracy[field] = 0.0
        
        # Overall accuracy
        total_correct = sum(s["correct"] for s in field_stats.values())
        total_fields = sum(s["total"] for s in field_stats.values())
        field_accuracy["overall"] = total_correct / total_fields if total_fields > 0 else 0.0
        
        return field_accuracy
    
    def save_report(
        self,
        report: Dict[str, Any],
        output_path: str
    ) -> None:
        """
        Save and print error report.
        
        Args:
            report: Error report dictionary
            output_path: Path to save report
        """
        # Save to file
        write_json(report, output_path)
        self.logger.info(f"Report saved to: {output_path}")
        
        # Print summary
        print("\n" + "="*60)
        print(f"OCR ERROR ANALYSIS REPORT - {report['engine'].upper()}")
        print("="*60)
        print(f"Total Documents: {report['total_documents']}")
        print(f"Analyzed Documents: {report['analyzed_documents']}")
        print(f"\nField Accuracy:")
        for field, accuracy in report['field_accuracy'].items():
            print(f"  {field}: {accuracy:.2%}")
        print(f"\nAverage Confidence: {report['summary']['avg_confidence']:.2%}")
        print(f"Average Blocks per Document: {report['summary']['avg_blocks_per_doc']:.1f}")
        print("="*60 + "\n")
