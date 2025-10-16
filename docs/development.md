# Development Notes

This guide captures practical tips for working on mcl-tool during day-to-day development.

## Sample Configuration
```json
{
  "scripts": {
    "greet": ["echo Hello $1"],
    "deploy": [
      "echo Deploying $project",
      "?$1",
      "echo Version $version"
    ],
    "example": {
      "hello": "echo Hello, World!",
      "list": ["ls -la"],
      "show_date": "date"
    }
  },
  "vars": {
    "project": "mcl",
    "version": "0.1.0"
  }
}
```
- `$1`, `$2`, ... map to positional arguments passed after the command name.
- `?$1` style placeholders are optional: the fragment is removed if the corresponding argument is missing.
- Config vars can be referenced with `$project` or exported as environment variables when `--share-vars` is used.

## Local Development Loop
1. Update or create `mcl.json` via `mcl init` or manual editing.
2. Run commands with `mcl run <script> [args]` or shorthand `mcl <script> [args]`. Nested definitions require specifying the path, e.g. `mcl example hello`.
3. Use `--dry-run` to inspect substitutions without executing anything.
4. Enable `--share-vars` to expose config vars and args as environment variables for shell evaluation.
5. Run `mcl` with no arguments to list local scripts (overrides first) and remaining global scripts.

## Quality Gates
- `pre-commit run --all-files` keeps formatting and typing consistent.
- `pytest --cov=src/mcl` must pass before merging changes.
- Run `mypy src` when touching type-heavy code to catch interface issues early.
