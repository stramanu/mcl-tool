# API Reference

This document summarizes the public API exposed by the `mcl` package. Function signatures use type hints and Google-style docstrings; run `pydoc mcl` or generate Sphinx docs for more detail.

## mcl.config
- `load_config(local: bool = False) -> dict[str, Any]`: Returns merged global and local configuration data.
- `save_config(config: Mapping[str, Any], path: Path) -> None`: Persists configuration as JSON with indentation.
- `init_local() -> None`: Creates an empty `mcl.json` if it does not already exist.
- `edit_global() -> None`: Opens the global config in `$EDITOR` (defaults to `nano` or `notepad`) and raises `ValueError` if the editor command fails.

## mcl.executor
- `execute(config: Mapping[str, Any], cmd_name: str, args: Sequence[str], dry_run: bool, share_vars: bool) -> None`: Resolves script definitions and runs each step after substitution.
- `render_script(...) -> list[str]`: Helper that prepares command fragments with substitutions and optional arguments.

## mcl.cli
- `cli()` : Click command group registered as the console entry point `mcl`.
- Subcommands: `init`, `edit`, `run`.

## Usage Example
```python
from mcl.config import load_config
from mcl.executor import execute

config = load_config(local=True)
execute(config, "echo", ["world"], dry_run=True, share_vars=False)
```
