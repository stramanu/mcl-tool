"""Tests for the Click CLI."""

from __future__ import annotations

import importlib
from typing import Any

import pytest
from click.testing import CliRunner

cli_module = importlib.import_module("mcl.cli")
from mcl.cli import cli


def test_run_invokes_executor(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    calls: dict[str, Any] = {}

    def fake_load_config(*_, **__):  # type: ignore[no-untyped-def]
        calls["load_config"] = True
        return {"scripts": {"test": ["echo hi"]}, "vars": {}}

    def fake_execute(
        config: dict[str, Any],
        cmd: str,
        args: list[str],
        dry_run: bool,
        share_vars: bool,
    ) -> None:
        calls["execute"] = {
            "config": config,
            "cmd": cmd,
            "args": args,
            "dry_run": dry_run,
            "share_vars": share_vars,
        }

    monkeypatch.setattr(cli_module, "load_config", fake_load_config)
    monkeypatch.setattr(cli_module, "execute", fake_execute)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--dry-run", "run", "test", "arg1"])

    assert result.exit_code == 0
    assert calls["load_config"] is True
    execute_args = calls["execute"]
    assert execute_args["cmd"] == "test"
    assert execute_args["args"] == ["arg1"]
    assert execute_args["dry_run"] is True
    assert execute_args["share_vars"] is False


def test_run_reports_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()

    def fake_load_config(*_, **__):  # type: ignore[no-untyped-def]
        return {"scripts": {"bad": ["echo hi"]}, "vars": {}}

    def fake_execute(*_, **__):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    monkeypatch.setattr(cli_module, "load_config", fake_load_config)
    monkeypatch.setattr(cli_module, "execute", fake_execute)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["run", "bad"])

    assert result.exit_code != 0
    assert "Error: boom" in result.output


def test_init_local_command(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    invoked = {"count": 0}

    def fake_init_local() -> None:
        invoked["count"] += 1

    monkeypatch.setattr(cli_module, "init_local_config", fake_init_local)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])

    assert result.exit_code == 0
    assert invoked["count"] == 1


def test_edit_conf_command(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    invoked = {"count": 0}

    def fake_edit_global() -> None:
        invoked["count"] += 1

    monkeypatch.setattr(cli_module, "edit_global", fake_edit_global)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["edit"])

    assert result.exit_code == 0
    assert invoked["count"] == 1


def test_edit_conf_command_reports_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()

    def fake_edit_global() -> None:
        raise ValueError("Editor 'nano' not found")

    monkeypatch.setattr(cli_module, "edit_global", fake_edit_global)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["edit"])

    assert result.exit_code != 0
    assert "Error: Editor 'nano' not found" in result.output


def test_direct_script_invocation(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    calls: dict[str, Any] = {}

    def fake_load_config(*_, **__):  # type: ignore[no-untyped-def]
        calls["load_config"] = True
        return {"scripts": {"test": ["echo $1"]}, "vars": {}}

    def fake_execute(
        config: dict[str, Any],
        cmd: str,
        args: list[str],
        dry_run: bool,
        share_vars: bool,
    ) -> None:
        calls["execute"] = {
            "config": config,
            "cmd": cmd,
            "args": args,
            "dry_run": dry_run,
            "share_vars": share_vars,
        }

    monkeypatch.setattr(cli_module, "load_config", fake_load_config)
    monkeypatch.setattr(cli_module, "execute", fake_execute)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--dry-run", "test", "arg1", "arg2"])

    assert result.exit_code == 0
    assert calls["load_config"] is True
    execute_args = calls["execute"]
    assert execute_args["cmd"] == "test"
    assert execute_args["args"] == ["arg1", "arg2"]
    assert execute_args["dry_run"] is True
    assert execute_args["share_vars"] is False


def test_nested_script_invocation(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    calls: dict[str, Any] = {}

    def fake_load_config(*_, **__):  # type: ignore[no-untyped-def]
        calls["load_config"] = True
        return {
            "scripts": {
                "example": {
                    "date": {
                        "utc": ["date -u"],
                    }
                }
            },
            "vars": {},
        }

    def fake_execute(
        config: dict[str, Any],
        cmd: str,
        args: list[str],
        dry_run: bool,
        share_vars: bool,
    ) -> None:
        calls.setdefault("execute", []).append(
            {
                "config": config,
                "cmd": cmd,
                "args": args,
                "dry_run": dry_run,
                "share_vars": share_vars,
            }
        )

    monkeypatch.setattr(cli_module, "load_config", fake_load_config)
    monkeypatch.setattr(cli_module, "execute", fake_execute)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["example", "date", "utc", "extra"])

    assert result.exit_code == 0
    assert calls["load_config"] is True
    execute_calls = calls["execute"]
    assert len(execute_calls) == 1
    execute_args = execute_calls[0]
    assert execute_args["cmd"] == "example"
    assert execute_args["args"] == ["date", "utc", "extra"]
    assert execute_args["dry_run"] is False
    assert execute_args["share_vars"] is False


def test_usage_lists_scripts(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()

    def fake_load_config(*_, **__):  # type: ignore[no-untyped-def]
        return {
            "scripts": {
                "example": {
                    "hello": "echo hi",
                    "build": ["make"],
                    "date": {"utc": "date -u"},
                }
            },
            "__global_scripts__": {
                "example": {
                    "hello": "echo global",
                    "date": {"utc": "date -u"},
                    "list": "ls",
                }
            },
            "__local_scripts__": {
                "example": {
                    "hello": "echo hi",
                    "build": ["make"],
                }
            },
        }

    monkeypatch.setattr(cli_module, "load_config", fake_load_config)

    with runner.isolated_filesystem():
        result = runner.invoke(cli, [])

    assert "Tip: use `mcl run <script>`" in result.output
    assert "Local scripts" in result.output
    assert "Global scripts" in result.output
    assert "example.hello" in result.output
    assert "example.build" in result.output
    assert "example.date.utc" in result.output
    # ensure overridden local command not repeated in global section
    global_section = result.output[result.output.rfind("Global scripts") :]
    assert global_section.count("example.hello") == 0
    assert result.exit_code == 0
