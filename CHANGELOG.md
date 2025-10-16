# Changelog

## [0.1.0] - 2025-10-15
### Added
- Base CLI with `run`, `init`, and `edit` commands.
- JSON config loading and merging.
- Variable and argument parsing in the executor.
- Nested script resolution with shorthand invocation (`mcl <script> ...`).
- GitHub Actions CI pipeline (lint + pytest coverage).

### Changed
- Package published as `mcl-tool`; CLI entry point is `mcl`.

## [Unreleased]
- Add Pydantic based configuration validation.
