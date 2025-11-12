"""Plugin templates for 'mcl plugin new' command."""

from typing import Dict, Any
from pathlib import Path


# Template definitions
TEMPLATES = {
    "simple": {
        "name": "Simple Plugin",
        "description": "Basic plugin with minimal dependencies",
    },
    "click": {
        "name": "Click-based Plugin",
        "description": "Plugin using Click framework for complex CLIs",
    },
    "api-client": {
        "name": "API Client Plugin",
        "description": "REST API wrapper with authentication",
    },
}


def get_template_list() -> Dict[str, Dict[str, str]]:
    """
    Get available plugin templates.

    Returns:
        Dictionary mapping template keys to metadata
    """
    return TEMPLATES


def render_simple_plugin(plugin_name: str, description: str) -> Dict[str, str]:
    """
    Render a simple plugin template.

    Args:
        plugin_name: Plugin name (e.g., 'hello')
        description: Plugin description

    Returns:
        Dictionary mapping file paths to content
    """
    package_name = plugin_name.replace("-", "_")
    pypi_name = f"mcl-plugin-{plugin_name}"

    return {
        "pyproject.toml": f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{pypi_name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.8"
authors = [
    {{name = "Your Name", email = "you@example.com"}}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.entry-points."mcl.plugins"]
{plugin_name} = "mcl_plugin_{package_name}:main"

[tool.setuptools.packages.find]
where = ["src"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
""",
        f"src/mcl_plugin_{package_name}/__init__.py": f'''"""MCL {plugin_name} plugin."""

__version__ = "0.1.0"

from .cli import main

__all__ = ["main"]
''',
        f"src/mcl_plugin_{package_name}/cli.py": '''"""CLI interface for the plugin."""

import os
from typing import List


def main(args: List[str]) -> int:
    """
    Main entry point for the plugin.
    
    Args:
        args: Command-line arguments passed after the plugin name
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Check for dry-run mode
    dry_run = os.getenv("MCL_DRY_RUN") == "1"
    
    if dry_run:
        print(f"[DRY-RUN] Would execute with args: {args}")
        return 0
    
    # TODO: Implement your plugin logic here
    if not args:
        print("Hello from your new MCL plugin!")
        print("Add your implementation in src/mcl_plugin_*/cli.py")
    else:
        print(f"Received arguments: {args}")
    
    return 0
''',
        f"tests/test_{package_name}.py": f'''"""Tests for {plugin_name} plugin."""

import pytest
from mcl_plugin_{package_name} import cli


def test_main_no_args():
    """Test plugin runs with no arguments."""
    result = cli.main([])
    assert result == 0


def test_main_with_args():
    """Test plugin receives arguments."""
    result = cli.main(["arg1", "arg2"])
    assert result == 0


def test_main_dry_run(monkeypatch):
    """Test dry-run mode."""
    monkeypatch.setenv("MCL_DRY_RUN", "1")
    result = cli.main(["test"])
    assert result == 0
''',
        "README.md": f"""# MCL {plugin_name.title()} Plugin

{description}

## Installation

```bash
pip install {pypi_name}
```

## Usage

```bash
mcl {plugin_name} [args]
```

## Development

```bash
# Install in development mode
pip install -e '.[dev]'

# Run tests
pytest

# Install plugin locally
pip install -e .
```

## Examples

```bash
# Basic usage
mcl {plugin_name}

# With arguments
mcl {plugin_name} arg1 arg2

# Dry-run mode
mcl --dry-run {plugin_name}
```
""",
        ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
""",
    }


def render_click_plugin(plugin_name: str, description: str) -> Dict[str, str]:
    """
    Render a Click-based plugin template.

    Args:
        plugin_name: Plugin name (e.g., 'docker')
        description: Plugin description

    Returns:
        Dictionary mapping file paths to content
    """
    package_name = plugin_name.replace("-", "_")
    pypi_name = f"mcl-plugin-{plugin_name}"

    base_files = render_simple_plugin(plugin_name, description)

    # Override pyproject.toml to include Click dependency
    base_files[
        "pyproject.toml"
    ] = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{pypi_name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "click>=8.0",
]
authors = [
    {{name = "Your Name", email = "you@example.com"}}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.entry-points."mcl.plugins"]
{plugin_name} = "mcl_plugin_{package_name}:main"

[tool.setuptools.packages.find]
where = ["src"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
"""

    # Override cli.py with Click implementation
    base_files[
        f"src/mcl_plugin_{package_name}/cli.py"
    ] = f'''"""CLI interface using Click framework."""

import os
import click


@click.group()
def cli():
    """{description}"""
    pass


@cli.command()
@click.argument('name', default='World')
def hello(name: str):
    """Say hello to someone."""
    dry_run = os.getenv("MCL_DRY_RUN") == "1"
    
    if dry_run:
        click.echo(f"[DRY-RUN] Would greet: {{name}}")
    else:
        click.echo(f"Hello, {{name}}! 👋")


@cli.command()
@click.option('--count', '-c', default=1, help='Number of times to repeat')
@click.argument('message')
def repeat(count: int, message: str):
    """Repeat a message multiple times."""
    dry_run = os.getenv("MCL_DRY_RUN") == "1"
    
    if dry_run:
        click.echo(f"[DRY-RUN] Would repeat '{{message}}' {{count}} times")
    else:
        for _ in range(count):
            click.echo(message)


def main(args: list[str]) -> int:
    """
    Main entry point that bridges MCL to Click.
    
    Args:
        args: Command-line arguments from MCL
    
    Returns:
        Exit code
    """
    try:
        cli(args, standalone_mode=False)
        return 0
    except click.ClickException as e:
        e.show()
        return e.exit_code
    except Exception as e:
        click.echo(f"Error: {{e}}", err=True)
        return 1
'''

    # Update README with Click examples
    base_files[
        "README.md"
    ] = f"""# MCL {plugin_name.title()} Plugin

{description}

Built with [Click](https://click.palletsprojects.com/) framework for rich CLI features.

## Installation

```bash
pip install {pypi_name}
```

## Usage

```bash
# Show available commands
mcl {plugin_name} --help

# Example commands
mcl {plugin_name} hello Alice
mcl {plugin_name} repeat "Hello!" --count 3
```

## Development

```bash
# Install in development mode with dependencies
pip install -e '.[dev]'

# Run tests
pytest

# Check types
mypy src
```

## Examples

```bash
# Basic usage
mcl {plugin_name} hello World

# With options
mcl {plugin_name} repeat "test" -c 5

# Dry-run mode
mcl --dry-run {plugin_name} hello
```
"""

    return base_files


def render_api_client_plugin(plugin_name: str, description: str) -> Dict[str, str]:
    """
    Render an API client plugin template.

    Args:
        plugin_name: Plugin name (e.g., 'github')
        description: Plugin description

    Returns:
        Dictionary mapping file paths to content
    """
    package_name = plugin_name.replace("-", "_")
    pypi_name = f"mcl-plugin-{plugin_name}"

    base_files = render_simple_plugin(plugin_name, description)

    # Override pyproject.toml to include requests
    base_files[
        "pyproject.toml"
    ] = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{pypi_name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28",
]
authors = [
    {{name = "Your Name", email = "you@example.com"}}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.entry-points."mcl.plugins"]
{plugin_name} = "mcl_plugin_{package_name}:main"

[tool.setuptools.packages.find]
where = ["src"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "responses>=0.22",
]
"""

    # Override cli.py with API client implementation
    base_files[
        f"src/mcl_plugin_{package_name}/cli.py"
    ] = '''"""API client CLI interface."""

import os
import sys
import requests
from typing import List, Optional


class APIClient:
    """Simple API client with authentication."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
    
    def get(self, endpoint: str) -> dict:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint (e.g., '/users')
        
        Returns:
            JSON response as dictionary
        """
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()


def main(args: List[str]) -> int:
    """
    Main entry point for API client plugin.
    
    Args:
        args: Command-line arguments
    
    Returns:
        Exit code
    """
    dry_run = os.getenv("MCL_DRY_RUN") == "1"
    
    # Get API credentials from environment
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("API_BASE_URL", "https://api.example.com")
    
    if not args:
        print("Usage: mcl plugin-name <endpoint>")
        print("Example: mcl plugin-name users")
        print()
        print("Environment variables:")
        print("  API_KEY       - API authentication key")
        print("  API_BASE_URL  - Base URL (default: https://api.example.com)")
        return 0
    
    endpoint = args[0]
    
    if dry_run:
        print(f"[DRY-RUN] Would call: {base_url}/{endpoint}")
        return 0
    
    try:
        client = APIClient(base_url, api_key)
        result = client.get(endpoint)
        
        # Pretty print JSON response
        import json
        print(json.dumps(result, indent=2))
        
        return 0
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
'''

    # Update README with API client examples
    base_files[
        "README.md"
    ] = f"""# MCL {plugin_name.title()} Plugin

{description}

## Installation

```bash
pip install {pypi_name}
```

## Configuration

Set environment variables for authentication:

```bash
export API_KEY="your-api-key-here"
export API_BASE_URL="https://api.example.com"  # optional
```

Or use MCL's variable system in `mcl.json`:

```json
{{
  "vars": {{
    "api_key": "your-key",
    "api_url": "https://api.example.com"
  }}
}}
```

## Usage

```bash
# Call API endpoint
mcl {plugin_name} users

# With dry-run
mcl --dry-run {plugin_name} users/123
```

## Development

```bash
# Install with dev dependencies
pip install -e '.[dev]'

# Run tests
pytest

# Test with mock API
python -c "from tests.test_{package_name} import test_api_call; test_api_call()"
```

## Examples

```bash
# List users
API_KEY="abc123" mcl {plugin_name} users

# Get specific resource
API_KEY="abc123" mcl {plugin_name} users/42

# Dry-run mode (doesn't call API)
mcl --dry-run {plugin_name} users
```
"""

    return base_files


def generate_plugin(
    plugin_name: str,
    description: str,
    template: str,
    output_dir: Path,
) -> None:
    """
    Generate plugin files from template.

    Args:
        plugin_name: Plugin name (e.g., 'hello')
        description: Plugin description
        template: Template name ('simple', 'click', 'api-client')
        output_dir: Output directory for generated files

    Raises:
        ValueError: If template is unknown
    """
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template: {template}")

    # Select renderer
    if template == "simple":
        files = render_simple_plugin(plugin_name, description)
    elif template == "click":
        files = render_click_plugin(plugin_name, description)
    elif template == "api-client":
        files = render_api_client_plugin(plugin_name, description)
    else:
        raise ValueError(f"Template not implemented: {template}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write all files
    for file_path, content in files.items():
        full_path = output_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
