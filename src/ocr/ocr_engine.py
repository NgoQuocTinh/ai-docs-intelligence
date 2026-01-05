"""OCR engine wrapper supporting PaddleOCR and Tesseract"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Literal
import cv2
import numpy as np
from datetime import datetime

from ..utils.file_utils import write_json, ensure_dir, list_files
from ..utils.logger import setup_logger


class OCREngine:
    """Wrapper for OCR engines (PaddleOCR and Tesseract)."""
    
    def __init__(
        self,
        engine: Literal["paddle", "tesseract", "both"] = "paddle",
        use_gpu: bool = False,
        lang: str = "en"
    ):
        """
        Initialize OCR engine.
        
        Args:
            engine: OCR engine to use ("paddle", "tesseract", or "both")
            use_gpu: Whether to use GPU for PaddleOCR (default: False)
            lang: Language for OCR (default: "en")
        """
        self.engine = engine
        self.lang = lang
        self.logger = setup_logger(__name__)
        
        # Initialize PaddleOCR if needed
        if engine in ["paddle", "both"]:
            try:
                from paddleocr import PaddleOCR
                self.paddle_ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang=lang,
                    use_gpu=use_gpu,
                    show_log=False
                )
                self.logger.info(f"PaddleOCR initialized (GPU: {use_gpu})")
            except Exception as e:
                self.logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.paddle_ocr = None
        else:
            self.paddle_ocr = None
        
        # Initialize Tesseract if needed
        if engine in ["tesseract", "both"]:
            try:
                import pytesseract
                self.pytesseract = pytesseract
                # Test if tesseract is installed
                pytesseract.get_tesseract_version()
                self.logger.info("Tesseract initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Tesseract: {e}")
                self.pytesseract = None
        else:
            self.pytesseract = None
    
    def extract_text_paddle(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text using PaddleOCR.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary containing OCR results
        """
        if self.paddle_ocr is None:
            raise RuntimeError("PaddleOCR not initialized")
        
        try:
            result = self.paddle_ocr.ocr(image_path, cls=True)
            
            text_blocks = []
            full_text = []
            
            if result and result[0]:
                for line in result[0]:
                    if line:
                        bbox = line[0]
                        text_info = line[1]
                        text = text_info[0]
                        confidence = float(text_info[1])
                        
                        # Convert bbox coordinates
                        x_coords = [point[0] for point in bbox]
                        y_coords = [point[1] for point in bbox]
                        
                        text_block = {
                            "text": text,
                            "confidence": confidence,
                            "bbox": {
                                "x_min": int(min(x_coords)),
                                "y_min": int(min(y_coords)),
                                "x_max": int(max(x_coords)),
                                "y_max": int(max(y_coords))
                            }
                        }
                        text_blocks.append(text_block)
                        full_text.append(text)
            
            return {
                "engine": "paddle",
                "text_blocks": text_blocks,
                "full_text": "\n".join(full_text),
                "num_blocks": len(text_blocks),
                "avg_confidence": np.mean([b["confidence"] for b in text_blocks]) if text_blocks else 0.0
            }
        
        except Exception as e:
            self.logger.error(f"PaddleOCR extraction failed: {e}")
            return {
                "engine": "paddle",
                "text_blocks": [],
                "full_text": "",
                "num_blocks": 0,
                "avg_confidence": 0.0,
                "error": str(e)
            }
    
    def extract_text_tesseract(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text using Tesseract.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary containing OCR results
        """
        if self.pytesseract is None:
            raise RuntimeError("Tesseract not initialized")
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Get detailed OCR data
            data = self.pytesseract.image_to_data(
                gray,
                output_type=self.pytesseract.Output.DICT,
                lang='eng'
            )
            
            text_blocks = []
            full_text = []
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:  # Only process non-empty text
                    confidence = float(data['conf'][i]) / 100.0  # Convert to 0-1 range
                    if confidence > 0:  # Filter out invalid detections
                        text_block = {
                            "text": text,
                            "confidence": confidence,
                            "bbox": {
                                "x_min": int(data['left'][i]),
                                "y_min": int(data['top'][i]),
                                "x_max": int(data['left'][i] + data['width'][i]),
                                "y_max": int(data['top'][i] + data['height'][i])
                            }
                        }
                        text_blocks.append(text_block)
                        full_text.append(text)
            
            return {
                "engine": "tesseract",
                "text_blocks": text_blocks,
                "full_text": " ".join(full_text),
                "num_blocks": len(text_blocks),
                "avg_confidence": np.mean([b["confidence"] for b in text_blocks]) if text_blocks else 0.0
            }
        
        except Exception as e:
            self.logger.error(f"Tesseract extraction failed: {e}")
            return {
                "engine": "tesseract",
                "text_blocks": [],
                "full_text": "",
                "num_blocks": 0,
                "avg_confidence": 0.0,
                "error": str(e)
            }
    
    def process_image(
        self,
        image_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process single image with configured OCR engine(s).
        
        Args:
            image_path: Path to image file
            output_dir: Optional output directory for results
        
        Returns:
            Dictionary containing OCR results
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        self.logger.info(f"Processing image: {path.name}")
        
        results = {
            "image_path": str(path),
            "image_name": path.name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Run PaddleOCR
        if self.engine in ["paddle", "both"] and self.paddle_ocr:
            paddle_result = self.extract_text_paddle(image_path)
            results["paddle"] = paddle_result
        
        # Run Tesseract
        if self.engine in ["tesseract", "both"] and self.pytesseract:
            tesseract_result = self.extract_text_tesseract(image_path)
            results["tesseract"] = tesseract_result
        
        # Save results if output directory provided
        if output_dir:
            ensure_dir(output_dir)
            output_path = Path(output_dir) / f"{path.stem}_ocr.json"
            write_json(results, output_path)
            self.logger.info(f"Results saved to: {output_path}")
        
        return results
    
    def batch_process(
        self,
        input_dir: str,
        output_dir: str,
        pattern: str = "*.png"
    ) -> List[Dict[str, Any]]:
        """
        Batch process images in directory.
        
        Args:
            input_dir: Input directory containing images
            output_dir: Output directory for OCR results
            pattern: File pattern to match (default: "*.png")
        
        Returns:
            List of OCR results for all processed images
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Get all matching images
        image_files = list_files(input_path, pattern=pattern, recursive=False)
        self.logger.info(f"Found {len(image_files)} images to process")
        
        results = []
        for i, image_file in enumerate(image_files, 1):
            try:
                result = self.process_image(str(image_file), output_dir)
                results.append(result)
                
                if i % 10 == 0:
                    self.logger.info(f"Processed {i}/{len(image_files)} images")
            
            except Exception as e:
                self.logger.error(f"Failed to process {image_file}: {e}")
                continue
        
        self.logger.info(f"Batch processing complete: {len(results)}/{len(image_files)} successful")
        
        # Save summary
        summary = {
            "total_images": len(image_files),
            "successful": len(results),
            "failed": len(image_files) - len(results),
            "timestamp": datetime.now().isoformat()
        }
        summary_path = Path(output_dir) / "batch_summary.json"
        write_json(summary, summary_path)
        
        return results
