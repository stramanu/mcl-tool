# Testing Guide

The project uses pytest with strict type checking and formatting enforcement.

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest --cov=src/mcl
```

## Guidelines
- Use `tmp_path` fixtures for filesystem interactions and keep tests hermetic.
- Monkeypatch environment variables or subprocess calls rather than relying on the host system.
- Cover executor edge cases: missing args, optional placeholders, dry-run behavior, and share-vars execution.
- CLI tests should rely on `click.testing.CliRunner` with monkeypatched config/executor dependencies.
- Keep coverage reports in CI by enabling the provided GitHub Actions workflow template.
