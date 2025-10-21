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


def test_execute_nested_requires_valid_subcommand() -> None:
    config = {
        "scripts": {
            "example": {
                "hello": ["echo hi"],
            }
        },
        "vars": {},
    }

    with pytest.raises(ValueError):
        execute(config, "example", [], dry_run=True, share_vars=False)

    with pytest.raises(ValueError):
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
