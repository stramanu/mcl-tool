"""Tests for script listing utilities."""

from __future__ import annotations

from mcl.commands import extract_script_maps, list_script_paths


def test_list_script_paths_flat() -> None:
    scripts = {"hello": "echo hi", "build": ["make"]}
    assert list_script_paths(scripts) == ["build", "hello"]


def test_list_script_paths_nested() -> None:
    scripts = {
        "example": {
            "hello": "echo hi",
            "date": {"utc": "date -u"},
            "list": ["ls"],
        }
    }
    result = list_script_paths(scripts)
    assert result == [
        "example date utc",
        "example hello",
        "example list",
    ]


def test_list_script_paths_ignores_unknown_types() -> None:
    scripts = {"invalid": 123}  # executor would error later; should not crash listing
    assert list_script_paths(scripts) == []


def test_extract_script_maps_defaults() -> None:
    g, l = extract_script_maps({})
    assert g == {}
    assert l == {}


def test_extract_script_maps_returns_dicts() -> None:
    config = {
        "__global_scripts__": {"example": {"hello": "echo global"}},
        "__local_scripts__": {"example": {"hello": "echo local"}},
    }
    g, l = extract_script_maps(config)
    assert g == {"example": {"hello": "echo global"}}
    assert l == {"example": {"hello": "echo local"}}
