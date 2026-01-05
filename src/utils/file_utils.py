"""File utilities for AI Document Intelligence"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union


def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read JSON file.
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Dictionary containing JSON data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Write data to JSON file.
    
    Args:
        data: Data to write
        file_path: Path to output JSON file
        indent: JSON indentation level (default: 2)
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_text(file_path: Union[str, Path]) -> str:
    """
    Read text file.
    
    Args:
        file_path: Path to text file
    
    Returns:
        File contents as string
    
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text(text: str, file_path: Union[str, Path]) -> None:
    """
    Write text to file.
    
    Args:
        text: Text to write
        file_path: Path to output file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern to match (default: "*")
        recursive: Whether to search recursively (default: False)
    
    Returns:
        List of matching file paths
    """
    path = Path(directory)
    if not path.exists():
        return []
    
    if recursive:
        return sorted(path.rglob(pattern))
    else:
        return sorted(path.glob(pattern))


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
    
    Returns:
        Path object for the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in bytes
    
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return path.stat().st_size


def validate_path(file_path: Union[str, Path]) -> bool:
    """
    Validate if path exists.
    
    Args:
        file_path: Path to validate
    
    Returns:
        True if path exists, False otherwise
    """
    return Path(file_path).exists()
