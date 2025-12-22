"""Tests for the interactive menu functionality."""

from __future__ import annotations

import subprocess
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

from mcl.executor import execute


def test_interactive_menu_when_no_subcommand_in_tty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that the interactive menu appears when there's a TTY."""
    import questionary

    # Mock TTY
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    # Mock questionary.select
    mock_select = MagicMock()
    mock_select.ask.return_value = "build"
    monkeypatch.setattr(questionary, "select", lambda *args, **kwargs: mock_select)

    # Mock subprocess.run
    captured: list[Any] = []

    def fake_run(cmd: Any, **kwargs: Any) -> None:
        captured.append((cmd, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)

    config = {
        "scripts": {
            "docker": {
                "build": "echo 'Building...'",
                "run": "echo 'Running...'",
            }
        },
        "vars": {},
    }

    # Execute without subcommand - should show menu and then execute the choice
    execute(config, "docker", [], dry_run=False, share_vars=False)

    # Verify that questionary.select was called
    assert mock_select.ask.called

    # Verify that the command was executed
    assert len(captured) == 1
    assert captured[0][0] == "echo 'Building...'"


def test_interactive_menu_cancelled_by_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that menu cancellation raises an error."""
    import questionary

    # Mock TTY
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    # Mock questionary.select to simulate Ctrl+C
    mock_select = MagicMock()
    mock_select.ask.return_value = None  # None = user cancelled
    monkeypatch.setattr(questionary, "select", lambda *args, **kwargs: mock_select)

    config = {
        "scripts": {
            "docker": {
                "build": "echo 'Building...'",
            }
        },
        "vars": {},
    }

    with pytest.raises(ValueError, match="cancelled by user"):
        execute(config, "docker", [], dry_run=False, share_vars=False)


def test_non_interactive_still_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that in non-TTY environment the classic error is raised."""
    # Mock non-TTY
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    config = {
        "scripts": {
            "docker": {
                "build": "echo 'Building...'",
            }
        },
        "vars": {},
    }

    with pytest.raises(ValueError, match="requires a subcommand"):
        execute(config, "docker", [], dry_run=False, share_vars=False)
