# Architecture Overview

mcl-tool is a modular CLI that flows user requests through a clear pipeline: CLI -> Config -> Executor -> Shell.

```
[User: mcl run cmd args] --> [cli.py: parse & context]
                             |
                             v
[config.py: load & merge JSON] --> [executor.py: substitute vars/args]
                             |
                             v
[subprocess: execute command] <-- [flags: dry-run/share-vars]
```

## Modules and Responsibilities
- **cli.py**: Handles Click argument parsing and context propagation. Provides `init`, `edit`, and `run` commands. Calling `mcl` with no arguments shows a merged list of available script paths for quick discovery.
- **config.py**: Loads and merges JSON config from global and project locations. Local values override global ones.
- **executor.py**: Applies substitution rules for `$1` style arguments and config variables, skips comment lines, and runs subprocesses.
- **__init__.py**: Exposes version metadata and the CLI entry point for packaging.

## Design Principles
- **SRP**: Keep configuration logic out of the CLI and executor.
- **Explicit errors**: Raise `ValueError` for invalid JSON, missing scripts, or unresolved placeholders so the CLI can abort cleanly.
- **Security**: Default to `shell=False`; only enable `shell=True` when `--share-vars` is explicitly requested.
- **Extensibility**: New commands live in `cli.py`; new substitution features belong in `executor.py`.

## Configuration Schema
JSON structure:
```
{
  "scripts": {
    "name": ["echo $1"],
    "deploy": ["?$2", "echo $project"],
    "example": {
      "hello": "echo Hello, World!",
      "list": ["ls -la"],
      "nested": {
        "show": "date"
      }
    }
  },
  "vars": {
    "project": "mcl",
    "author": "Your Name"
  }
}
```
- **scripts**: Each value can be a string command, a list of shell fragments, or another mapping of subcommands. Nested structures are traversed by passing the desired path as additional CLI arguments (e.g. `mcl example hello`). Lines starting with `#` are ignored when executing.
- **vars**: Key/value pairs injected during substitution and optionally exported to the environment.

## Known Trade-offs
- JSON keeps dependencies light but lacks schema validation; future work may introduce Pydantic.
- Using `shell=True` for shared environments trades safety for convenience; keep it opt-in.
