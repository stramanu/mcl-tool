**Project Snapshot**
- `mcl-tool` is a Click-based CLI for running user-defined command recipes; packaging is driven by `pyproject.toml` with the `mcl` console script.
- Keep type hints and Google-style docstrings consistent across modules; static analysis (mypy strict) is part of the expected workflow.
- Logging replaces prints; configure via `logging.basicConfig` in `cli` and use module-level loggers elsewhere.

**Source Layout**
- `src/mcl/cli.py` hosts the Click group, global flags (`--dry-run`, `--share-vars`), and subcommands `init`, `edit`, `run`.
- `src/mcl/config.py` owns json config IO, merging `~/.mcl/global-mcl.json` with project `mcl.json`; guard against invalid JSON by raising `ValueError`.
- `src/mcl/executor.py` parses script templates, substitutes `$1` style args and vars, and invokes subprocesses; only enable `shell=True` when `share-vars` is active.
- `docs/architecture.md` and `docs/api.md` explain the CLI→Config→Executor pipeline and should be updated if flows change.

**Runtime Flow**
- `mcl run <cmd>` (or shorthand `mcl <cmd>`) loads merged config, resolves the script list, applies substitutions, then executes each command; respect dry-run by short-circuiting before subprocess. Invoking `mcl` with no args prints help plus local scripts (showing overrides) followed by remaining global script paths.
- Scripts can be strings, lists of shell fragments, or nested mappings; pass additional CLI arguments to traverse nested structures (e.g. `mcl example hello`). Ignore lines starting with hash characters inside script arrays when executing.
- Treat missing commands or substitution failures as `ValueError` so CLI surfaces them via `click.Abort()`.

**Config Mechanics**
- JSON schema: scripts may be strings, lists, or nested objects (e.g. `{ "example": { "hello": "echo hi" } }`); ensure merges preserve existing keys and let local override global. Vars remain key/value pairs for substitution.
- `init_local()` must create an empty `mcl.json` without clobbering existing files; warn instead of overwriting.
- `edit_conf()` opens the global config via `$EDITOR` (default `nano`/`notepad`); avoid hardcoding other editors.

**Testing & Quality**
- Dev setup: `python -m venv .venv && source .venv/bin/activate`, then `pip install -e .[dev]` to get pytest, mypy, black, pre-commit.
- Run `pytest --cov=src/mcl` for coverage; use tmp paths and monkeypatching when touching filesystem or subprocess.
- Pre-commit uses black (line length 88) and mypy strict; keep CI parity by running hooks locally before committing.

**Workflow Tips**
- When extending CLI, add new `@cli.command()` functions in `src/mcl/cli.py` and document usage in `docs/architecture.md`.
- Maintain SRP by isolating config, CLI, and executor concerns; avoid mixing subprocess logic into the config layer.
- Update `CHANGELOG.md` on version bumps and keep `__version__` in sync with `pyproject.toml`.
- New external deps must be declared in `pyproject.toml` and, if optional, placed under `[project.optional-dependencies]`.
