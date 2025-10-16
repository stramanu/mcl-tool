# mcl-tool — My Command Line

A batteries-included CLI that turns JSON recipes into reusable automation scripts.

**Author:** [Emanuele Strazzullo](https://github.com/stramanu)
- **Dev friendly** – strict type hints, pytest coverage, mypy/black enforced in CI.
- **Open source** – licensed under MIT, free to fork, adapt, and redistribute with attribution.

[![PyPI](https://img.shields.io/pypi/v/mcl-tool)](https://pypi.org/project/mcl-tool/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![CI](https://github.com/stramanu/mcl-tool/actions/workflows/ci.yml/badge.svg)

## Why mcl-tool?
- **Composable scripts** – author commands once in JSON and call them from anywhere.
- **Args & vars aware** – mix positional placeholders (`$1`, `$2`) with named variables and optional fragments (`?$1`).
- **Nested flows** – drill into structures like `example.date.utc` via `mcl example date utc`.
- **Safe execution** – dry-run mode, opt-in environment sharing, structured logging.
- **Dev friendly** – strict type hints, pytest coverage, mypy/black enforced in CI.

## Installation

### macOS / Linux (virtual environment recommended)
1. Ensure Python 3.10+ is available (`python3 --version`).
2. If `venv` is missing, install it (e.g. `sudo apt install python3-venv` on Debian/Ubuntu or `brew install python@3.11` on macOS).
3. Create and activate an isolated environment:
	```bash
	python3 -m venv ~/.venvs/mcl
	source ~/.venvs/mcl/bin/activate
	python -m pip install --upgrade pip
	```
4. Install the CLI inside the environment:
	```bash
	pip install mcl-tool
	```

### System-wide install via pipx
If you prefer a standalone binary-like install, use [pipx](https://pipx.pypa.io/):
```bash
pipx install mcl-tool
```
This keeps `mcl` isolated while exposing the command on your PATH.

## Quick Start
1. **Initialize a project config**
	```bash
	mcl init
	```
2. **Edit `mcl.json`** (local overrides global `~/.mcl/global-mcl.json`):
	```json
	{
		"vars": {
			"project": "mcl",
			"version": "0.1.0"
		},
		"scripts": {
			"example": {
				"hello": "echo Hello, $1!",
				"deploy": [
					"echo Deploying $project",
					"?$1",
					"echo Version $version"
				],
				"date": {
					"show": "date",
					"utc": "date -u"
				}
			}
		}
	}
	```
3. **Run commands**
	```bash
	mcl example hello Alice      # -> echo Hello, Alice!
	mcl example deploy staging  # -> optional arg substituted into '?$1'
	mcl --dry-run example date utc
	mcl                        # -> shows available scripts from global + local config
	```

## Command Reference
| Command | Description |
| --- | --- |
| `mcl init` | Create a stub `mcl.json` without overwriting existing files. |
| `mcl edit` | Open the global config (`~/.mcl/global-mcl.json`) in `$EDITOR`. |
| `mcl run <script> [args...]` | Execute a script node; errors bubble as `ValueError` for clean Click aborts. |
| `mcl <script> [args...]` | Shorthand for `mcl run ...`, including nested paths (`mcl example date utc`). |
| `--dry-run` | Print rendered commands without executing. |
| `--share-vars` | Export config vars and args as env vars for shell-based scripts. |

## Configuration Notes
- Scripts accept strings, ordered lists, or nested objects; comment lines starting with `#` are ignored.
- Positional placeholders (`$1`, `$2`, …) map to CLI args; optional placeholders (`?$3`) drop when missing.
- Config vars become substitutions (`$project`) and, with `--share-vars`, exported env vars (`project`, `MCL_ARG_1`, …).
- Global config lives in `~/.mcl/global-mcl.json`; local `mcl.json` overrides keys during merge.
- Running `mcl` with no args prints local scripts first (overrides highlighted) and global scripts second for quick discovery.

## Development
- Create an environment: `python -m venv .venv && source .venv/bin/activate`
- Install dev extras: `pip install -e '.[dev]'`
- Run quality gates:
	```bash
	black --check .
	mypy src tests
	pytest --cov=src/mcl
	```
- GitHub Actions (`.github/workflows/ci.yml`) mirrors these steps.

See `docs/architecture.md` for a deep dive into the CLI → Config → Executor pipeline, and `docs/testing.md` for pytest tips. Contribution guidelines live in `CONTRIBUTING.md`.

## Roadmap
- Config schema validation (Pydantic).
- Optional YAML support.
- Multi-platform test matrix via tox.

Have ideas? Open an issue or PR! 🎉
