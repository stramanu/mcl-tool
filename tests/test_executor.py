"""Tests for mcl.executor."""

from __future__ import annotations

import subprocess
from typing import Any

import pytest

from mcl.executor import execute, render_script


def test_render_script_substitutes_args_and_vars() -> None:
    script = ["echo $1", "echo $project", "  # comment"]
    result = render_script(script, ["hello"], {"project": "mcl"})
    assert result == ["echo hello", "echo mcl"]


def test_render_script_raises_on_missing_arg() -> None:
    script = ["echo $2"]
    with pytest.raises(ValueError):
        render_script(script, ["only-one"], {})


def test_execute_runs_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []

    def fake_run(cmd: Any, **kwargs: Any) -> None:
        calls.append((cmd, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {"scripts": {"hello": ["echo $1"]}, "vars": {}}
    execute(config, "hello", ["world"], dry_run=False, share_vars=False)

    assert calls
    cmd, kwargs = calls[0]
    assert cmd == "echo world"
    assert kwargs["shell"] is True
    assert kwargs["check"] is True


def test_execute_dry_run_skips_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_: Any, **__: Any) -> None:  # pragma: no cover - safety
        raise AssertionError("subprocess.run should not be called during dry-run")

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {"scripts": {"noop": ["echo $1"]}, "vars": {}}
    execute(config, "noop", ["ok"], dry_run=True, share_vars=False)


def test_execute_share_vars_exports_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[Any] = []

    def fake_run(cmd: Any, **kwargs: Any) -> None:
        captured.append((cmd, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {"scripts": {"env": ["echo $project"]}, "vars": {"project": "mcl"}}
    execute(config, "env", [], dry_run=False, share_vars=True)

    assert captured
    cmd, kwargs = captured[0]
    assert isinstance(cmd, str)
    assert kwargs["shell"] is True
    env = kwargs["env"]
    assert env["project"] == "mcl"


def test_execute_supports_nested_scripts(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Any] = []

    def fake_run(cmd: Any, **kwargs: Any) -> None:
        captured.append((cmd, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {
        "scripts": {
            "example": {
                "hello": "echo Hello, World!",
                "list": ["ls -la"],
            }
        },
        "vars": {},
    }

    execute(config, "example", ["hello", "there"], dry_run=False, share_vars=False)

    assert captured
    cmd, kwargs = captured[0]
    assert cmd == "echo Hello, World!"
    assert kwargs["shell"] is True
    assert kwargs["check"] is True


def test_execute_nested_requires_valid_subcommand(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that nested scripts without TTY raise an error."""
    # Mock stdin.isatty() to return False (non-interactive environment)
    import sys

    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    config = {
        "scripts": {
            "example": {
                "hello": ["echo hi"],
            }
        },
        "vars": {},
    }

    with pytest.raises(ValueError, match="requires a subcommand"):
        execute(config, "example", [], dry_run=True, share_vars=False)

    with pytest.raises(ValueError, match="has no subcommand"):
        execute(config, "example", ["missing"], dry_run=True, share_vars=False)


def test_execute_handles_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment variables in commands are handled correctly."""
    captured: list[Any] = []

    def fake_run(cmd: Any, **kwargs: Any) -> None:
        captured.append((cmd, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {
        "scripts": {"build": {"win": "GOOS=windows GOARCH=amd64 wails build"}},
        "vars": {},
    }

    execute(config, "build", ["win"], dry_run=False, share_vars=False)

    assert captured
    cmd, kwargs = captured[0]
    assert cmd == "GOOS=windows GOARCH=amd64 wails build"
    assert kwargs["shell"] is True
    assert kwargs["check"] is True


def test_render_script_escapes_double_dollar() -> None:
    """Test that double dollar $$ remains as literal $ in output."""
    script = ["echo $$1", "echo $$project", "echo $$HOME"]
    result = render_script(script, [], {})
    assert result == ["echo $1", "echo $project", "echo $HOME"]


def test_render_script_mixed_escaped_and_substituted() -> None:
    """Test scripts with both regular placeholders and escaped ones."""
    script = ["echo $1 $$2", "echo $name and $$USER"]
    result = render_script(script, ["hello"], {"name": "mcl"})
    assert result == ["echo hello $2", "echo mcl and $USER"]


def test_execute_generate_shell_script(monkeypatch: pytest.MonkeyPatch) -> None:
    """Real-world scenario: creating a shell script with bash parameters."""
    captured: list[Any] = []

    def fake_run(cmd: Any, **kwargs: Any) -> None:
        captured.append((cmd, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {
        "scripts": {
            "create-script": [
                "echo '#!/bin/bash' > script.sh",
                "echo 'echo Hello $$1' >> script.sh",
                "chmod +x script.sh",
            ]
        },
        "vars": {},
    }

    execute(config, "create-script", [], dry_run=False, share_vars=False)

    assert len(captured) == 3
    assert captured[0][0] == "echo '#!/bin/bash' > script.sh"
    assert captured[1][0] == "echo 'echo Hello $1' >> script.sh"
    assert captured[2][0] == "chmod +x script.sh"


def test_double_dollar_with_optional_args() -> None:
    """Test that $$N works correctly with optional placeholders."""
    script = ["echo ?$1 $$2"]

    # With argument provided
    result = render_script(script, ["arg1"], {})
    assert result == ["echo arg1 $2"]

    # Without argument
    result = render_script(script, [], {})
    assert result == ["echo  $2"]


def test_escaped_vars_not_substituted() -> None:
    """Test that $$varname is not replaced with config vars."""
    script = ["echo $$project and $version"]
    result = render_script(script, [], {"project": "mcl", "version": "1.0"})
    assert result == ["echo $project and 1.0"]


def test_multiple_consecutive_dollars() -> None:
    """Test edge case with multiple consecutive dollar signs."""
    # $$$ should become $$ after first unescape, then $ after replacements
    # But with our implementation: $$$ stays as $$$ during matching (no match),
    # then becomes $ during unescape
    script = ["echo $$$1"]
    result = render_script(script, ["value"], {})
    # The first $$ prevents matching, so $1 is not replaced
    # Then $$ becomes $ during unescape
    assert result == ["echo $$1"]


def test_execute_script_nested_under_run_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that scripts under a 'run' key can be executed by the executor.

    This tests the bug fix where 'mcl run service' would fail because the CLI
    command 'run' intercepted the call, passing 'service' as cmd_name instead
    of the full path 'run.service'.
    """
    captured: list[Any] = []

    def fake_run(cmd: Any, **kwargs: Any) -> None:
        captured.append((cmd, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {
        "scripts": {
            "run": {
                "service": "echo example",
                "db": {"start": "echo db start"},
            }
        },
        "vars": {},
    }

    # Test simple nested script under "run"
    execute(config, "service", [], dry_run=False, share_vars=False)
    assert captured
    cmd, kwargs = captured[0]
    assert cmd == "echo example"
    assert kwargs["shell"] is True

    # Test deeply nested script under "run"
    captured.clear()
    execute(config, "db", ["start"], dry_run=False, share_vars=False)
    assert captured
    cmd, kwargs = captured[0]
    assert cmd == "echo db start"
