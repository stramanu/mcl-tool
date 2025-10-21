# Contributing to mcl-tool

Thanks for your interest! The project follows strict practices to keep the code base clean and testable.

## Developer Setup
1. Clone: `git clone https://github.com/stramanu/mcl-tool.git`
2. Create a virtual env: `python -m venv .venv && source .venv/bin/activate`
3. Install dev deps: `pip install -e '.[dev]'` (use quotes on zsh to avoid glob expansion)
4. Install pre-commit: `pre-commit install`
5. Run tests: `pytest --cov=src/mcl`
6. Type check: `mypy src tests`

## Testing Your Changes
To test the development version locally:

### Option 1: Activate the virtual environment
```bash
cd /path/to/mcl-tool
source .venv/bin/activate
mcl --help
```

### Option 2: Use the full path
```bash
/path/to/mcl-tool/.venv/bin/mcl --help
```

### Option 3: Create a shell alias (recommended)
Add to your `.bashrc` or `.zshrc`:
```bash
alias mcld="/path/to/mcl-tool/.venv/bin/mcl"
```
Then use `mcld` to invoke the development version anywhere:
```bash
mcld build win
mcld run test
```

## Contribution Workflow
- **Fork & Branch**: Create `feature/` or `fix/` branches from `main`.
- **Commits**: Prefer Conventional Commit messages (e.g. `feat: add validation`).
- **Pull Request**: Target `main`, describe changes, include tests.
- **Code Review**: Expect review cycles; keep black/mypy happy before requesting review.
- **Pre-flight checks**: Run `pre-commit run --all-files`, `pytest --cov=src/mcl`, and `mypy src tests` before pushing.

## Best Practices
- **Design**: Enforce SRP, keep type hints and Google-style docstrings throughout modules.
- **Testing**: Maintain high coverage; unit-test executor logic, integration-test the CLI.
- **Logging**: Use module loggers instead of `print`; pick suitable levels.
- **Security**: Validate JSON input; scripts always use `shell=True` for proper environment variable and shell syntax handling.
- **Documentation**: Update README and docs under `docs/` when behavior or workflows change.
- **Versioning**: Follow semantic versioning; update `CHANGELOG.md` with every release.

## Code Layout
```
repo root
|-- src/mcl/
|   |-- __init__.py
|   |-- cli.py
|   |-- commands.py
|   |-- config.py
|   `-- executor.py
|-- tests/
|   |-- test_cli.py
|   |-- test_commands.py
|   |-- test_config.py
|   `-- test_executor.py
|-- docs/
|   |-- api.md
|   |-- architecture.md
|   |-- development.md
|   |-- devlog.md
|   `-- testing.md
`-- .github/
	|-- copilot-instructions.md
	`-- workflows/ci.yml
```

## Future Ideas
- Configuration validation with Pydantic.
- Optional YAML support.
- Cross-platform test matrix via tox.

Questions? Open an issue!
