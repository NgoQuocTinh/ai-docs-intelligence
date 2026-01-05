#!/usr/bin/env python3
"""Quick dataset generation script for synthetic invoices"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import InvoiceGenerator
from src.utils.logger import setup_logger


def main():
    """Main function to generate synthetic dataset."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic invoice dataset"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=200,
        help="Number of invoices to generate (default: 200)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="dataset/raw",
        help="Output directory (default: dataset/raw)"
    )
    parser.add_argument(
        "--locale",
        type=str,
        default="en_US",
        help="Locale for fake data (default: en_US)"
    )
    parser.add_argument(
        "--noise-prob",
        type=float,
        default=0.5,
        help="Probability of adding noise to images (default: 0.5)"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger("generate_dataset", log_file="logs/dataset_generation.log")
    
    logger.info("="*60)
    logger.info("Synthetic Invoice Dataset Generation")
    logger.info("="*60)
    logger.info(f"Number of samples: {args.num_samples}")
    logger.info(f"Output directory: {args.output}")
    logger.info(f"Locale: {args.locale}")
    logger.info(f"Noise probability: {args.noise_prob}")
    
    try:
        # Create generator
        generator = InvoiceGenerator(
            output_dir=args.output,
            locale=args.locale
        )
        
        # Generate dataset
        doc_ids = generator.generate_dataset(
            num_samples=args.num_samples,
            add_noise_probability=args.noise_prob
        )
        
        logger.info("="*60)
        logger.info(f"Successfully generated {len(doc_ids)} invoices!")
        logger.info(f"Images saved to: {args.output}")
        logger.info(f"Labels saved to: {Path(args.output).parent / 'labels'}")
        logger.info("="*60)
        
        return 0
    
    except Exception as e:
        logger.error(f"Failed to generate dataset: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
