"""Synthetic invoice generator"""

import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from faker import Faker

from ..utils.file_utils import write_json, ensure_dir
from ..utils.logger import setup_logger


class InvoiceGenerator:
    """Generates synthetic invoice images with labels."""
    
    def __init__(
        self,
        output_dir: str = "dataset/raw",
        locale: str = "en_US"
    ):
        """
        Initialize invoice generator.
        
        Args:
            output_dir: Output directory for generated invoices
            locale: Locale for generating fake data (default: "en_US")
        """
        self.output_dir = Path(output_dir)
        self.labels_dir = Path(output_dir).parent / "labels"
        self.faker = Faker(locale)
        self.logger = setup_logger(__name__)
        
        ensure_dir(self.output_dir)
        ensure_dir(self.labels_dir)
        
        # Invoice template settings
        self.width = 800
        self.height = 1000
        self.bg_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.font_size_title = 32
        self.font_size_normal = 16
        self.font_size_small = 12
        
        self.logger.info(f"InvoiceGenerator initialized for locale: {locale}")
    
    def generate_invoice_data(self) -> Dict[str, Any]:
        """
        Generate random invoice data.
        
        Returns:
            Dictionary containing invoice data
        """
        # Generate basic info
        invoice_number = f"INV-{random.randint(1000, 9999)}"
        invoice_date = self.faker.date_between(start_date='-1y', end_date='today')
        due_date = invoice_date + timedelta(days=random.randint(15, 60))
        
        # Generate vendor info
        vendor_name = self.faker.company()
        vendor_address = self.faker.address().replace('\n', ', ')
        vendor_tax_id = f"TAX-{random.randint(100000, 999999)}"
        
        # Generate customer info
        customer_name = self.faker.name()
        customer_address = self.faker.address().replace('\n', ', ')
        
        # Generate line items
        num_items = random.randint(1, 5)
        line_items = []
        subtotal = 0.0
        
        for _ in range(num_items):
            description = self.faker.catch_phrase()
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10, 500), 2)
            amount = round(quantity * unit_price, 2)
            
            line_items.append({
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": amount
            })
            subtotal += amount
        
        # Calculate tax and total
        tax_rate = random.choice([0, 5, 8, 10, 15, 20])
        tax_amount = round(subtotal * tax_rate / 100, 2)
        total_amount = round(subtotal + tax_amount, 2)
        
        # Currency
        currency = random.choice(["USD", "EUR", "GBP", "VND"])
        
        invoice_data = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "vendor_name": vendor_name,
            "vendor_address": vendor_address,
            "vendor_tax_id": vendor_tax_id,
            "customer_name": customer_name,
            "customer_address": customer_address,
            "line_items": line_items,
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "currency": currency,
            "payment_terms": f"Net {random.choice([15, 30, 45, 60])} days",
            "notes": "Thank you for your business!"
        }
        
        return invoice_data
    
    def render_invoice_image(
        self,
        data: Dict[str, Any],
        add_noise: bool = False
    ) -> Image.Image:
        """
        Render invoice data as image.
        
        Args:
            data: Invoice data dictionary
            add_noise: Whether to add noise to image
        
        Returns:
            PIL Image object
        """
        # Create blank image
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        y_position = 40
        x_margin = 40
        
        # Try to use default font
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size_title)
            font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size_normal)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size_small)
        except (OSError, IOError):
            # Fallback to default font
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Title
        draw.text((x_margin, y_position), "INVOICE", fill=self.text_color, font=font_title)
        y_position += 60
        
        # Invoice details
        draw.text((x_margin, y_position), f"Invoice #: {data['invoice_number']}", fill=self.text_color, font=font_normal)
        y_position += 25
        draw.text((x_margin, y_position), f"Date: {data['invoice_date']}", fill=self.text_color, font=font_normal)
        y_position += 25
        draw.text((x_margin, y_position), f"Due Date: {data['due_date']}", fill=self.text_color, font=font_normal)
        y_position += 40
        
        # Vendor info
        draw.text((x_margin, y_position), "FROM:", fill=self.text_color, font=font_normal)
        y_position += 25
        draw.text((x_margin, y_position), data['vendor_name'], fill=self.text_color, font=font_small)
        y_position += 20
        # Wrap vendor address
        address_lines = self._wrap_text(data['vendor_address'], 50)
        for line in address_lines:
            draw.text((x_margin, y_position), line, fill=self.text_color, font=font_small)
            y_position += 18
        draw.text((x_margin, y_position), f"Tax ID: {data['vendor_tax_id']}", fill=self.text_color, font=font_small)
        y_position += 35
        
        # Customer info
        draw.text((x_margin, y_position), "TO:", fill=self.text_color, font=font_normal)
        y_position += 25
        draw.text((x_margin, y_position), data['customer_name'], fill=self.text_color, font=font_small)
        y_position += 20
        address_lines = self._wrap_text(data['customer_address'], 50)
        for line in address_lines:
            draw.text((x_margin, y_position), line, fill=self.text_color, font=font_small)
            y_position += 18
        y_position += 25
        
        # Line items header
        draw.text((x_margin, y_position), "Description", fill=self.text_color, font=font_normal)
        draw.text((x_margin + 300, y_position), "Qty", fill=self.text_color, font=font_normal)
        draw.text((x_margin + 380, y_position), "Price", fill=self.text_color, font=font_normal)
        draw.text((x_margin + 500, y_position), "Amount", fill=self.text_color, font=font_normal)
        y_position += 30
        
        # Line items
        for item in data['line_items']:
            desc = self._truncate_text(item['description'], 30)
            draw.text((x_margin, y_position), desc, fill=self.text_color, font=font_small)
            draw.text((x_margin + 300, y_position), str(item['quantity']), fill=self.text_color, font=font_small)
            draw.text((x_margin + 380, y_position), f"{item['unit_price']:.2f}", fill=self.text_color, font=font_small)
            draw.text((x_margin + 500, y_position), f"{item['amount']:.2f}", fill=self.text_color, font=font_small)
            y_position += 25
        
        y_position += 20
        
        # Totals
        draw.text((x_margin + 380, y_position), "Subtotal:", fill=self.text_color, font=font_normal)
        draw.text((x_margin + 500, y_position), f"{data['subtotal']:.2f} {data['currency']}", fill=self.text_color, font=font_normal)
        y_position += 25
        
        draw.text((x_margin + 380, y_position), f"Tax ({data['tax_rate']}%):", fill=self.text_color, font=font_normal)
        draw.text((x_margin + 500, y_position), f"{data['tax_amount']:.2f} {data['currency']}", fill=self.text_color, font=font_normal)
        y_position += 25
        
        draw.text((x_margin + 380, y_position), "TOTAL:", fill=self.text_color, font=font_normal)
        draw.text((x_margin + 500, y_position), f"{data['total_amount']:.2f} {data['currency']}", fill=self.text_color, font=font_normal)
        y_position += 40
        
        # Payment terms and notes
        draw.text((x_margin, y_position), f"Payment Terms: {data['payment_terms']}", fill=self.text_color, font=font_small)
        y_position += 25
        draw.text((x_margin, y_position), data['notes'], fill=self.text_color, font=font_small)
        
        # Add noise if requested
        if add_noise:
            img = self._add_noise(img)
        
        return img
    
    def _add_noise(self, img: Image.Image) -> Image.Image:
        """
        Add realistic noise to image.
        
        Args:
            img: Input image
        
        Returns:
            Noisy image
        """
        # Random rotation
        angle = random.uniform(-5, 5)
        img = img.rotate(angle, fillcolor=self.bg_color, expand=False)
        
        # Adjust brightness
        brightness_factor = random.uniform(0.8, 1.2)
        img_array = np.array(img, dtype=np.float32)
        img_array = np.clip(img_array * brightness_factor, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        
        # Add Gaussian noise
        if random.random() > 0.5:
            img_array = np.array(img, dtype=np.float32)
            noise = np.random.normal(0, random.uniform(5, 15), img_array.shape)
            img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_array)
        
        # Slight blur
        if random.random() > 0.5:
            img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
        
        return img
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """Wrap text to multiple lines."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _truncate_text(self, text: str, max_chars: int) -> str:
        """Truncate text to max characters."""
        if len(text) <= max_chars:
            return text
        return text[:max_chars-3] + "..."
    
    def generate_dataset(
        self,
        num_samples: int = 200,
        add_noise_probability: float = 0.5
    ) -> List[str]:
        """
        Generate dataset of synthetic invoices.
        
        Args:
            num_samples: Number of invoices to generate
            add_noise_probability: Probability of adding noise to each image
        
        Returns:
            List of generated document IDs
        """
        doc_ids = []
        
        self.logger.info(f"Generating {num_samples} synthetic invoices...")
        
        for i in range(num_samples):
            # Generate invoice data
            invoice_data = self.generate_invoice_data()
            
            # Generate document ID
            doc_id = f"synthetic_{datetime.now().strftime('%Y%m%d')}_{i:04d}"
            
            # Add confidence scores (synthetic data has perfect confidence)
            invoice_data['confidence_scores'] = {
                'invoice_number': 1.0,
                'invoice_date': 1.0,
                'vendor_name': 1.0,
                'total_amount': 1.0
            }
            
            # Determine if noise should be added
            add_noise = random.random() < add_noise_probability
            
            # Render image
            img = self.render_invoice_image(invoice_data, add_noise=add_noise)
            
            # Save image
            image_path = self.output_dir / f"{doc_id}.png"
            img.save(image_path)
            
            # Save label
            label_path = self.labels_dir / f"{doc_id}.json"
            write_json(invoice_data, label_path)
            
            doc_ids.append(doc_id)
            
            if (i + 1) % 50 == 0:
                self.logger.info(f"Generated {i + 1}/{num_samples} invoices")
        
        self.logger.info(f"Successfully generated {num_samples} synthetic invoices")
        return doc_ids
