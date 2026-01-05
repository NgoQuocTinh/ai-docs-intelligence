#!/usr/bin/env python3
"""
Verification script to check Week 1 infrastructure setup.
Run this after setup to verify all components are in place.
"""

import sys
import platform
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check(description, condition):
    """Check a condition and print result."""
    if condition:
        print(f"{GREEN}✓{RESET} {description}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}")
        return False

def main():
    """Main verification function."""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}AI Document Intelligence - Week 1 Infrastructure Verification{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    base_path = Path(__file__).parent.parent
    checks_passed = 0
    total_checks = 0
    
    # Check directories
    print(f"{BOLD}1. Directory Structure{RESET}")
    dirs_to_check = [
        'configs', 'dataset', 'dataset/raw', 'dataset/labels',
        'dataset/ocr_text/paddle', 'dataset/ocr_text/tesseract',
        'src', 'src/data_collection', 'src/ocr', 'src/utils',
        'notebooks', 'tests', 'scripts', 'docs', 'reports', 'logs'
    ]
    
    for dir_path in dirs_to_check:
        full_path = base_path / dir_path
        total_checks += 1
        if check(f"Directory exists: {dir_path}", full_path.exists()):
            checks_passed += 1
    
    # Check configuration files
    print(f"\n{BOLD}2. Configuration Files{RESET}")
    config_files = [
        'requirements.txt',
        'configs/invoice_schema.json',
        'configs/config.yaml',
        '.env.example',
        '.gitignore'
    ]
    
    for file_path in config_files:
        full_path = base_path / file_path
        total_checks += 1
        if check(f"File exists: {file_path}", full_path.exists()):
            checks_passed += 1
    
    # Check source modules
    print(f"\n{BOLD}3. Source Modules{RESET}")
    source_files = [
        'src/__init__.py',
        'src/utils/logger.py',
        'src/utils/file_utils.py',
        'src/data_collection/collect_invoices.py',
        'src/data_collection/generate_synthetic.py',
        'src/ocr/ocr_engine.py',
        'src/ocr/error_analysis.py'
    ]
    
    for file_path in source_files:
        full_path = base_path / file_path
        total_checks += 1
        if check(f"Module exists: {file_path}", full_path.exists()):
            checks_passed += 1
    
    # Check scripts
    print(f"\n{BOLD}4. Scripts{RESET}")
    script_files = [
        'scripts/setup_environment.sh',
        'scripts/generate_dataset.py'
    ]
    
    is_windows = platform.system() == 'Windows'
    
    for file_path in script_files:
        full_path = base_path / file_path
        total_checks += 1
        exists = full_path.exists()
        
        # On Windows, just check existence; on Unix, check executable bit
        if is_windows:
            condition = exists
        else:
            condition = exists and (full_path.stat().st_mode & 0o111)
        
        if check(f"Script exists{' and executable' if not is_windows else ''}: {file_path}", condition):
            checks_passed += 1
    
    # Check documentation
    print(f"\n{BOLD}5. Documentation{RESET}")
    doc_files = [
        'README.md',
        'docs/setup_guide.md',
        'docs/week1_report.md'
    ]
    
    for file_path in doc_files:
        full_path = base_path / file_path
        total_checks += 1
        if check(f"Documentation exists: {file_path}", full_path.exists()):
            checks_passed += 1
    
    # Check notebooks
    print(f"\n{BOLD}6. Jupyter Notebooks{RESET}")
    notebook_files = [
        'notebooks/01_data_exploration.ipynb',
        'notebooks/02_ocr_baseline.ipynb',
        'notebooks/03_error_analysis.ipynb'
    ]
    
    for file_path in notebook_files:
        full_path = base_path / file_path
        total_checks += 1
        if check(f"Notebook exists: {file_path}", full_path.exists()):
            checks_passed += 1
    
    # Check tests
    print(f"\n{BOLD}7. Test Suite{RESET}")
    test_files = [
        'tests/__init__.py',
        'tests/test_data_collection.py',
        'tests/test_ocr_engine.py'
    ]
    
    for file_path in test_files:
        full_path = base_path / file_path
        total_checks += 1
        if check(f"Test file exists: {file_path}", full_path.exists()):
            checks_passed += 1
    
    # Validate JSON schema
    print(f"\n{BOLD}8. Configuration Validation{RESET}")
    try:
        import json
        schema_path = base_path / 'configs' / 'invoice_schema.json'
        with open(schema_path) as f:
            schema = json.load(f)
        total_checks += 1
        if check("invoice_schema.json is valid JSON", True):
            checks_passed += 1
    except Exception as e:
        total_checks += 1
        check(f"invoice_schema.json validation: {e}", False)
    
    # Summary
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}Summary{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    
    percentage = (checks_passed / total_checks) * 100
    status_color = GREEN if percentage == 100 else YELLOW if percentage >= 80 else RED
    
    print(f"\nChecks passed: {status_color}{checks_passed}/{total_checks} ({percentage:.1f}%){RESET}")
    
    if percentage == 100:
        print(f"\n{GREEN}{BOLD}✓ Week 1 infrastructure is complete!{RESET}")
        print(f"\n{BOLD}Next steps:{RESET}")
        print("1. Run: ./scripts/setup_environment.sh")
        print("2. Generate dataset: python scripts/generate_dataset.py --num-samples 200")
        print("3. Explore notebooks in notebooks/ directory")
        return 0
    elif percentage >= 80:
        print(f"\n{YELLOW}{BOLD}⚠ Week 1 infrastructure is mostly complete.{RESET}")
        print("Review failed checks above.")
        return 1
    else:
        print(f"\n{RED}{BOLD}✗ Week 1 infrastructure setup incomplete.{RESET}")
        print("Multiple components are missing. Review setup instructions.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
