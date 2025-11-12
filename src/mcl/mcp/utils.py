"""Utility functions for MCP server."""

import json
from pathlib import Path
from typing import Any, Dict


def validate_json_config(content: str) -> Dict[str, Any]:
    """
    Validate JSON configuration content.

    Args:
        content: JSON string to validate

    Returns:
        Parsed JSON as dictionary

    Raises:
        ValueError: If JSON is invalid
    """
    try:
        config = json.loads(content)
        if not isinstance(config, dict):
            raise ValueError("Config must be a JSON object")
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


def atomic_write(path: Path, content: str) -> None:
    """
    Write file atomically with backup.

    Args:
        path: Path to file
        content: Content to write

    Raises:
        IOError: If write fails
    """
    backup_path = path.with_suffix(path.suffix + ".bak")

    # Create backup if file exists
    if path.exists():
        path.rename(backup_path)

    try:
        path.write_text(content, encoding="utf-8")
        # Remove backup on success
        if backup_path.exists():
            backup_path.unlink()
    except Exception as e:
        # Restore backup on failure
        if backup_path.exists():
            backup_path.rename(path)
        raise IOError(f"Failed to write {path}: {e}") from e
