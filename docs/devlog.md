# Development Log

## 2025-10-15
- Initialized project scaffold: created packaging metadata, documentation set, and core directories (`src/mcl`, `docs`, `tests`).
- Added baseline contributor docs and change log to anchor future iterations.
- Planned executor features (argument substitution, optional fragments, share-vars safety) for upcoming implementation.
- Implemented config, executor, and CLI modules with logging, substitution, and Click integration per design notes.
- Added pytest suites covering config merging, executor substitutions, and CLI wiring.
- Updated development extras to include `pytest-cov` so coverage runs use the documented command.
- Enabled shorthand invocation (`mcl <script> ...`) by delegating unknown commands to the `run` handler and documented the behavior.
- Added support for nested script definitions, letting commands reference hierarchical config paths. Scripts are displayed and executed consistently using space notation (e.g., `mcl example hello`).
- Hardened CLI delegation (direct invocation + nested paths) and expanded CLI tests to cover alias resolution and nested script execution.
- Added script discovery UX: running `mcl` displays merged script paths; utilities for listing scripts are unit-tested.

## 2025-10-16
- Renamed CLI subcommands to `init` and `edit`, updating tests and docs for consistency.
- Improved global config editing by surfacing editor launch failures as `ValueError` with helpful CLI messaging.
- Synced documentation (README, API reference, architecture, contributing guide) with the latest behaviors and project layout.
