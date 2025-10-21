"""Tests for mcl.config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcl import config


def _override_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    global_dir = tmp_path / ".mcl"
    monkeypatch.setattr(config, "GLOBAL_DIR", global_dir, raising=False)
    monkeypatch.setattr(
        config, "GLOBAL_CONFIG", global_dir / "global-mcl.json", raising=False
    )
    monkeypatch.setattr(config, "LOCAL_CONFIG", project_dir / "mcl.json", raising=False)


def test_load_config_returns_defaults_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _override_paths(tmp_path, monkeypatch)
    result = config.load_config(local=True)
    assert result["scripts"] == {}
    assert result["vars"] == {}
    assert result.get("__global_scripts__") == {}
    assert result.get("__local_scripts__") == {}


def test_load_config_merges_local_over_global(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _override_paths(tmp_path, monkeypatch)

    config.ensure_global_dir()
    config.GLOBAL_CONFIG.write_text(
        json.dumps({"scripts": {"echo": ["echo global"]}, "vars": {"env": "prod"}})
    )

    local_payload = {
        "scripts": {"echo": ["echo local"], "build": ["echo build"]},
        "vars": {"env": "local"},
    }
    config.LOCAL_CONFIG.write_text(json.dumps(local_payload))

    result = config.load_config(local=True)
    assert result["scripts"]["echo"] == ["echo local"]
    assert result["scripts"]["build"] == ["echo build"]
    assert result["vars"]["env"] == "local"
    assert result.get("__global_scripts__") == {"echo": ["echo global"]}
    assert result.get("__local_scripts__") == local_payload["scripts"]


def test_load_config_raises_on_invalid_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _override_paths(tmp_path, monkeypatch)

    config.ensure_global_dir()
    config.GLOBAL_CONFIG.write_text("{invalid}")

    with pytest.raises(ValueError):
        config.load_config(local=False)


def test_init_local_skips_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    _override_paths(tmp_path, monkeypatch)
    config.ensure_global_dir()
    config.save_config({"scripts": {}, "vars": {}}, config.LOCAL_CONFIG)

    config.init_local()

    assert "Local config already exists" in caplog.text
