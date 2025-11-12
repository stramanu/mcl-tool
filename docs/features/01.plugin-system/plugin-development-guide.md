# MCL Plugin Development Guide

This guide walks you through creating, testing, and using a custom MCL plugin from scratch.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Creating Your First Plugin](#creating-your-first-plugin)
3. [Plugin Structure](#plugin-structure)
4. [Testing Your Plugin](#testing-your-plugin)
5. [Publishing Your Plugin](#publishing-your-plugin)
6. [Advanced Features](#advanced-features)

---

## Quick Start

Want to jump straight in? Here's a 5-minute plugin:

```bash
# 1. Create plugin directory
mkdir -p my-first-plugin/src/mcl_plugin_hello

# 2. Create the plugin code
cat > my-first-plugin/src/mcl_plugin_hello/__init__.py << 'EOF'
"""A simple MCL plugin that greets users."""

def main(args: list[str]) -> int:
    """Main entry point for the hello plugin."""
    name = args[0] if args else "World"
    print(f"Hello, {name}! 👋")
    return 0
EOF

# 3. Create package configuration
cat > my-first-plugin/pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mcl-plugin-hello"
version = "0.1.0"
description = "A simple greeting plugin for MCL"
requires-python = ">=3.8"

[project.entry-points."mcl.plugins"]
hello = "mcl_plugin_hello:main"
EOF

# 4. Install in development mode
cd my-first-plugin
pip install -e .

# 5. Use it!
mcl hello Alice
# Output: Hello, Alice! 👋
```

---

## Creating Your First Plugin

Let's build a more complete plugin: **mcl-plugin-docker** — a utility for common Docker operations.

### Step 1: Project Setup

Create the plugin directory structure:

```
mcl-plugin-docker/
├── src/
│   └── mcl_plugin_docker/
│       ├── __init__.py
│       └── cli.py
├── tests/
│   └── test_cli.py
├── pyproject.toml
└── README.md
```

### Step 2: Write the Plugin Code

**`src/mcl_plugin_docker/__init__.py`**:

```python
"""MCL Docker plugin - Manage Docker containers and images."""

__version__ = "0.1.0"

from .cli import main

__all__ = ["main"]
```

**`src/mcl_plugin_docker/cli.py`**:

```python
"""CLI interface for the Docker plugin."""

import os
import sys
import subprocess
from typing import List


def main(args: List[str]) -> int:
    """
    Main entry point for the Docker plugin.
    
    Args:
        args: Command-line arguments passed after 'mcl docker'
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Check for dry-run mode (set by mcl --dry-run)
    dry_run = os.getenv("MCL_DRY_RUN") == "1"
    
    if not args:
        print_help()
        return 0
    
    command = args[0]
    
    if command == "ps":
        return list_containers(args[1:], dry_run)
    elif command == "clean":
        return clean_images(args[1:], dry_run)
    elif command == "logs":
        return show_logs(args[1:], dry_run)
    else:
        print(f"Unknown command: {command}")
        print_help()
        return 1


def print_help() -> None:
    """Display plugin help."""
    print("""
MCL Docker Plugin

Usage:
    mcl docker ps              List running containers
    mcl docker clean           Remove dangling images
    mcl docker logs <name>     Show container logs

Examples:
    mcl docker ps
    mcl docker clean
    mcl docker logs my-app
    mcl --dry-run docker clean
""")


def list_containers(args: List[str], dry_run: bool) -> int:
    """List running Docker containers."""
    cmd = ["docker", "ps", "--format", "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"]
    
    if dry_run:
        print(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
        return 0
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error listing containers: {e}")
        return e.returncode
    except FileNotFoundError:
        print("Error: Docker not found. Is Docker installed?")
        return 127


def clean_images(args: List[str], dry_run: bool) -> int:
    """Remove dangling Docker images."""
    cmd = ["docker", "image", "prune", "-f"]
    
    if dry_run:
        print(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
        return 0
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✓ Cleaned dangling images")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error cleaning images: {e}")
        return e.returncode


def show_logs(args: List[str], dry_run: bool) -> int:
    """Show logs for a container."""
    if not args:
        print("Error: Container name required")
        print("Usage: mcl docker logs <container-name>")
        return 1
    
    container_name = args[0]
    cmd = ["docker", "logs", "--tail", "50", "-f", container_name]
    
    if dry_run:
        print(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
        return 0
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error showing logs: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n✓ Stopped following logs")
        return 0
```

### Step 3: Configure Package Metadata

**`pyproject.toml`**:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mcl-plugin-docker"
version = "0.1.0"
description = "Docker utilities plugin for MCL"
readme = "README.md"
requires-python = ">=3.8"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

# Entry point registration - this is what MCL discovers!
[project.entry-points."mcl.plugins"]
docker = "mcl_plugin_docker:main"

[tool.setuptools.packages.find]
where = ["src"]
```

**Key points:**
- The `[project.entry-points."mcl.plugins"]` section registers your plugin
- The entry point name (`docker`) becomes the MCL subcommand
- The value (`mcl_plugin_docker:main`) points to your main function

### Step 4: Add Documentation

**`README.md`**:

```markdown
# MCL Docker Plugin

A plugin for MCL that provides convenient Docker operations.

## Installation

```bash
pip install mcl-plugin-docker
```

## Usage

```bash
# List running containers
mcl docker ps

# Clean dangling images
mcl docker clean

# Follow container logs
mcl docker logs my-app

# Dry-run mode
mcl --dry-run docker clean
```

## Requirements

- Docker installed and accessible via CLI
- MCL >= 0.2.0
```

---

## Testing Your Plugin

### Unit Tests

**`tests/test_cli.py`**:

```python
"""Tests for Docker plugin CLI."""

import pytest
from unittest.mock import patch, MagicMock
from mcl_plugin_docker import cli


def test_main_no_args():
    """Test help is shown when no arguments provided."""
    result = cli.main([])
    assert result == 0


def test_main_unknown_command():
    """Test error on unknown command."""
    result = cli.main(["invalid"])
    assert result == 1


def test_list_containers_dry_run(monkeypatch):
    """Test listing containers in dry-run mode."""
    monkeypatch.setenv("MCL_DRY_RUN", "1")
    result = cli.list_containers([], dry_run=True)
    assert result == 0


@patch('subprocess.run')
def test_clean_images_success(mock_run):
    """Test successful image cleanup."""
    mock_run.return_value = MagicMock(returncode=0)
    result = cli.clean_images([], dry_run=False)
    assert result == 0
    mock_run.assert_called_once()


def test_show_logs_no_container():
    """Test error when no container name provided."""
    result = cli.show_logs([], dry_run=False)
    assert result == 1
```

### Manual Testing

```bash
# Install in development mode
cd mcl-plugin-docker
pip install -e .

# Test commands
mcl docker ps
mcl docker clean
mcl --dry-run docker clean

# Check plugin is registered
mcl plugin list
# Should show: docker (v0.1.0)

# Get plugin details
mcl plugin info docker
```

---

## Publishing Your Plugin

### 1. Prepare for Release

```bash
# Ensure tests pass
pytest

# Check package builds correctly
python -m build

# Verify package contents
tar -tzf dist/mcl-plugin-docker-0.1.0.tar.gz
```

### 2. Publish to PyPI

```bash
# Install publishing tools
pip install twine

# Upload to PyPI
twine upload dist/*

# Or upload to TestPyPI first
twine upload --repository testpypi dist/*
```

### 3. Installation by Users

Once published, anyone can install your plugin:

```bash
pip install mcl-plugin-docker
```

And immediately use it:

```bash
mcl docker ps
```

---

## Advanced Features

### Access MCL Context

Plugins can access MCL's runtime context via environment variables:

```python
import os

def main(args: list[str]) -> int:
    # Check if running in dry-run mode
    dry_run = os.getenv("MCL_DRY_RUN") == "1"
    
    # Check if variable sharing is enabled
    share_vars = os.getenv("MCL_SHARE_VARS") == "1"
    
    # Access MCL arguments
    mcl_arg_1 = os.getenv("MCL_ARG_1", "")
    
    if dry_run:
        print(f"[DRY-RUN] Would process: {args}")
        return 0
    
    # ... actual logic
```

### Click Integration

For complex CLIs, use Click framework:

```python
"""CLI using Click framework."""

import click
import os


@click.group()
def cli():
    """Docker utilities for MCL."""
    pass


@cli.command()
@click.option('--all', '-a', is_flag=True, help='Show all containers')
def ps(all):
    """List Docker containers."""
    dry_run = os.getenv("MCL_DRY_RUN") == "1"
    
    cmd = ["docker", "ps"]
    if all:
        cmd.append("-a")
    
    if dry_run:
        print(f"[DRY-RUN] {' '.join(cmd)}")
    else:
        subprocess.run(cmd)


@cli.command()
@click.argument('container')
@click.option('--tail', default=50, help='Number of lines to show')
def logs(container, tail):
    """Show container logs."""
    # ... implementation


def main(args: list[str]) -> int:
    """Entry point that bridges MCL to Click."""
    try:
        cli(args)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
```

Then add Click to dependencies:

```toml
[project]
dependencies = [
    "click>=8.0",
]
```

### Configuration Support

Read configuration from MCL's config files:

```python
import json
from pathlib import Path


def load_plugin_config():
    """Load plugin configuration from mcl.json."""
    config_path = Path("mcl.json")
    
    if not config_path.exists():
        return {}
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Look for plugin-specific config
    return config.get("plugins", {}).get("docker", {})


def main(args: list[str]) -> int:
    config = load_plugin_config()
    default_registry = config.get("registry", "docker.io")
    
    # Use configuration
    print(f"Using registry: {default_registry}")
```

Example `mcl.json`:

```json
{
  "scripts": {
    "build": "docker build -t myapp ."
  },
  "plugins": {
    "docker": {
      "registry": "ghcr.io",
      "default_tag": "latest"
    }
  }
}
```

### Type Hints and Validation

Use type hints for better IDE support and validation:

```python
from typing import List, Optional, Dict, Any
import sys


def main(args: List[str]) -> int:
    """
    Main entry point with type hints.
    
    Args:
        args: Command-line arguments from MCL
    
    Returns:
        Exit code (0 = success)
    """
    config = parse_config()
    return execute_command(args, config)


def parse_config() -> Dict[str, Any]:
    """Parse and validate configuration."""
    # ... implementation
    return {}


def execute_command(args: List[str], config: Dict[str, Any]) -> int:
    """Execute command with validated inputs."""
    # ... implementation
    return 0
```

---

## Plugin Examples Gallery

### Simple Script Wrapper

```python
"""Wrap git commands with shortcuts."""

import subprocess
import sys


def main(args: list[str]) -> int:
    if not args:
        print("Usage: mcl git <command>")
        return 1
    
    cmd = args[0]
    
    shortcuts = {
        "st": ["status"],
        "co": ["checkout"] + args[1:],
        "br": ["branch"],
        "cm": ["commit", "-m"] + args[1:],
    }
    
    git_cmd = ["git"] + shortcuts.get(cmd, args)
    return subprocess.run(git_cmd).returncode
```

### API Client Plugin

```python
"""Call REST APIs with authentication."""

import os
import requests
from typing import List


def main(args: List[str]) -> int:
    api_key = os.getenv("API_KEY")
    
    if not api_key:
        print("Error: API_KEY environment variable required")
        return 1
    
    if not args:
        print("Usage: mcl api <endpoint>")
        return 1
    
    endpoint = args[0]
    base_url = "https://api.example.com"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{base_url}/{endpoint}", headers=headers)
    
    print(response.json())
    return 0 if response.ok else 1
```

---

## Best Practices

### ✅ Do's

- **Return proper exit codes**: 0 for success, non-zero for errors
- **Respect `MCL_DRY_RUN`**: Check the environment variable and skip actions
- **Use type hints**: Improves code quality and IDE support
- **Handle errors gracefully**: Catch exceptions and provide helpful messages
- **Document your plugin**: Clear README with examples
- **Test thoroughly**: Unit tests + manual testing
- **Follow naming convention**: `mcl-plugin-<name>`

### ❌ Don'ts

- **Don't ignore dry-run mode**: Always check `MCL_DRY_RUN`
- **Don't use `sys.argv` directly**: Use the `args` parameter
- **Don't assume dependencies**: Document all requirements
- **Don't modify MCL internals**: Plugins should be self-contained
- **Don't block user input**: Unless it's an interactive feature
- **Don't hardcode paths**: Use Path objects and environment variables

---

## Troubleshooting

### Plugin Not Found

```bash
# Check plugin is installed
pip list | grep mcl-plugin

# Verify entry point registration
python -c "from importlib.metadata import entry_points; print([ep for ep in entry_points(group='mcl.plugins')])"

# Check MCL can see it
mcl plugin list
```

### Import Errors

```bash
# Ensure plugin package is importable
python -c "import mcl_plugin_docker; print(mcl_plugin_docker.__file__)"

# Check PYTHONPATH if using editable install
pip install -e .
```

### Dry-Run Not Working

Make sure you check the environment variable:

```python
import os

dry_run = os.getenv("MCL_DRY_RUN") == "1"  # Note: it's a string "1", not boolean
```

---

## Resources

- **MCL Documentation**: [docs/](../..)
- **Plugin Architecture**: [architecture.md](./architecture.md)
- **Implementation Plan**: [implementation-plan.md](./implementation-plan.md)
- **Example Plugin**: [tests/fixtures/mcl_plugin_test/](../../../tests/fixtures/mcl_plugin_test/)
- **Python Packaging Guide**: https://packaging.python.org/
- **Entry Points**: https://setuptools.pypa.io/en/latest/userguide/entry_point.html

---

## Questions?

- Open an issue: [GitHub Issues](https://github.com/yourusername/mcl-tool/issues)
- Check existing plugins for inspiration
- Read the architecture documentation

Happy plugin building! 🚀
