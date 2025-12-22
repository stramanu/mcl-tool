# Changelog

## [Unreleased]

### Added

- **Interactive subcommand selection**: When executing a nested command without specifying a subcommand in an interactive terminal (TTY), mcl now displays an interactive menu using `questionary`. Users can navigate with arrow keys and select with Enter.
- New dependency: `questionary>=2.0` for interactive menus.
- Three comprehensive tests for interactive menu behavior covering TTY/non-TTY modes and user cancellation.
- Documentation in `docs/architecture.md` explaining the new interactive feature.

### Changed

- **Simplified default output**: Running `mcl` without arguments now shows an interactive menu in TTY environments or a text list otherwise. Use `mcl --help` for detailed usage information.
- **Consistent space notation**: Scripts are now displayed AND executed with space-separated paths (e.g., `example hello`, `docker build`) for complete consistency. Previously used dot notation for display only.
- Non-interactive environments (pipes, scripts, CI/CD) maintain the original error message behavior for backward compatibility.
- Updated `executor.py` to detect TTY and show interactive menu only when appropriate.

## [0.3.0] - 2025-11-25

### Added

- **Escape mechanism**: Use `$$` to output literal `$` in scripts without substitution. This allows generating shell scripts with their own parameter placeholders (e.g., `$$1` becomes `$1` in output).
- Six comprehensive tests for the escape mechanism covering various scenarios.
- Detailed documentation and examples in README.md and docs/api.md.

### Fixed

- Fixed `--version` command that previously threw RuntimeError. Now properly displays package version.

### Changed

- Updated regex patterns to use negative lookbehind to skip `$$` sequences during substitution.
- Mypy Python version requirement updated to 3.10+ for compatibility.

## [0.2.0] - 2025-10-21

### Fixed

- **BREAKING**: Subprocess execution now always uses `shell=True` to properly support environment variables and complex shell syntax (fixes commands like `GOOS=windows GOARCH=amd64 wails build`).
- Improved type safety in CLI with proper type hints for `ScriptGroup.get_command()`.

### Added

- New test for environment variable handling in nested scripts.
- Developer testing section in CONTRIBUTING.md with multiple setup options.

### Changed

- Removed conditional `shell=False` path in executor that prevented env var handling.
- Updated all subprocess mocking tests to expect `shell=True` behavior.
- Type annotations now use PEP 585 style (`list`, `dict`) instead of `List`, `Dict`.
- Updated security best practices documentation.

## [0.1.0] - 2025-10-15

### Added

- Base CLI with `run`, `init`, and `edit` commands.
- JSON config loading and merging.
- Variable and argument parsing in the executor.
- Nested script resolution with shorthand invocation (`mcl <script> ...`).
- GitHub Actions CI pipeline (lint + pytest coverage).

### Changed

- Package published as `mcl-tool`; CLI entry point is `mcl`.
