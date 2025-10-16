"""Configuration management utilities for mcl.

This module loads, merges, and persists JSON config files from the global
(~/.mcl/global-mcl.json) and project (./mcl.json) locations.
"""

from __future__ import annotations

import json
import logging
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping

logger = logging.getLogger(__name__)

GLOBAL_DIR: Path = Path.home() / ".mcl"
GLOBAL_CONFIG: Path = GLOBAL_DIR / "global-mcl.json"
LOCAL_CONFIG: Path = Path.cwd() / "mcl.json"

_DEFAULT_CONFIG: Dict[str, Any] = {"vars": {}, "scripts": {}}


def ensure_global_dir() -> None:
    """Create the global configuration directory if it does not already exist."""

    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path) -> Dict[str, Any]:
    """Load JSON content from ``path``.

    Raises a ``ValueError`` if the payload is invalid or not a dictionary.
    """

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:  # pragma: no cover - explicit branch
        raise ValueError(f"Invalid JSON in {path}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Configuration in {path} must be a JSON object")

    return data


def _merge_dicts(base: MutableMapping[str, Any], override: Mapping[str, Any]) -> None:
    """Recursively merge ``override`` into ``base`` keeping nested dicts intact."""

    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_dicts(base[key], value)
        else:
            base[key] = value


def load_config(local: bool = False) -> Dict[str, Any]:
    """Return the merged configuration.

    Args:
        local: Merge the project ``mcl.json`` file on top of the global config.

    Returns:
        A dictionary with ``scripts`` and ``vars`` keys at minimum.

    Raises:
        ValueError: If any JSON file is malformed.
    """

    ensure_global_dir()
    merged: Dict[str, Any] = {"vars": {}, "scripts": {}}

    global_data: Dict[str, Any] = {}
    if GLOBAL_CONFIG.exists():
        logger.debug("Loading global config from %s", GLOBAL_CONFIG)
        global_data = _load_json(GLOBAL_CONFIG)
        _merge_dicts(merged, global_data)

    local_data: Dict[str, Any] = {}
    if local and LOCAL_CONFIG.exists():
        logger.debug("Loading local config from %s", LOCAL_CONFIG)
        local_data = _load_json(LOCAL_CONFIG)
        _merge_dicts(merged, local_data)

    # Guarantee expected keys for downstream consumers.
    merged.setdefault("scripts", {})
    merged.setdefault("vars", {})

    if not isinstance(merged["scripts"], dict) or not isinstance(merged["vars"], dict):
        raise ValueError("Configuration keys 'scripts' and 'vars' must be objects")

    global_scripts = (
        global_data.get("scripts", {})
        if isinstance(global_data.get("scripts", {}), dict)
        else {}
    )
    if not isinstance(global_scripts, dict):
        global_scripts = {}
    local_scripts = (
        local_data.get("scripts", {})
        if isinstance(local_data.get("scripts", {}), dict)
        else {}
    )
    if not isinstance(local_scripts, dict):
        local_scripts = {}

    merged["__global_scripts__"] = global_scripts
    merged["__local_scripts__"] = local_scripts

    return merged


def save_config(config: Mapping[str, Any], path: Path) -> None:
    """Persist ``config`` to ``path`` using JSON indentation."""

    ensure_global_dir()
    with path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=4)
        handle.write("\n")
    logger.debug("Saved configuration to %s", path)


def init_local() -> None:
    """Create an empty ``mcl.json`` without overwriting existing files."""

    if LOCAL_CONFIG.exists():
        logger.warning("Local config already exists at %s", LOCAL_CONFIG)
        return

    save_config(_DEFAULT_CONFIG, LOCAL_CONFIG)
    logger.info("Created new local config at %s", LOCAL_CONFIG)


def edit_global() -> None:
    """Open the global configuration file in the user's editor."""

    ensure_global_dir()
    if not GLOBAL_CONFIG.exists():
        save_config(_DEFAULT_CONFIG, GLOBAL_CONFIG)

    editor = os.environ.get("EDITOR")
    if not editor:
        editor = "nano" if os.name == "posix" else "notepad"

    try:
        parts = shlex.split(editor)
    except ValueError as exc:  # pragma: no cover - invalid EDITOR is rare
        raise ValueError(f"Invalid EDITOR command: {editor}") from exc

    if not parts:
        raise ValueError("EDITOR command cannot be empty")

    try:
        exit_code = subprocess.call(parts + [str(GLOBAL_CONFIG)])
    except FileNotFoundError as exc:
        logger.warning("Editor '%s' not found", parts[0])
        raise ValueError(f"Editor '{parts[0]}' not found") from exc

    if exit_code != 0:
        logger.warning("Editor process exited with code %s", exit_code)
        raise ValueError(f"Editor exited with status {exit_code}")

    logger.info("Opened global config in editor %s", editor)
