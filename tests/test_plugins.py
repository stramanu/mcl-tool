"""Tests for the plugin discovery and management system."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from mcl.plugins import discover_plugins, list_plugins


class MockEntryPoint:
    """Mock entry point for testing."""

    def __init__(self, name: str, value: str, load_fn: Any = None) -> None:
        self.name = name
        self.value = value
        self._load_fn = load_fn or (lambda: lambda args: 0)

    def load(self) -> Any:
        """Load the entry point."""
        if callable(self._load_fn):
            return self._load_fn()
        return self._load_fn


class TestDiscoverPlugins:
    """Tests for plugin discovery."""

    @patch("mcl.plugins.importlib.metadata.entry_points")
    def test_discover_no_plugins(self, mock_entry_points: MagicMock) -> None:
        """Test discovery when no plugins are installed."""
        # Python 3.10+ API (select)
        mock_eps = MagicMock()
        mock_eps.select.return_value = []
        mock_entry_points.return_value = mock_eps

        plugins = discover_plugins()

        assert plugins == {}
        mock_eps.select.assert_called_once_with(group="mcl.plugins")

    @patch("mcl.plugins.importlib.metadata.entry_points")
    def test_discover_single_plugin(self, mock_entry_points: MagicMock) -> None:
        """Test discovery with a single plugin."""
        test_fn = lambda args: 0
        ep = MockEntryPoint("test-plugin", "test_pkg.cli:main", lambda: test_fn)

        mock_eps = MagicMock()
        mock_eps.select.return_value = [ep]
        mock_entry_points.return_value = mock_eps

        plugins = discover_plugins()

        assert "test-plugin" in plugins
        assert plugins["test-plugin"] == test_fn

    @patch("mcl.plugins.importlib.metadata.entry_points")
    def test_discover_multiple_plugins(self, mock_entry_points: MagicMock) -> None:
        """Test discovery with multiple plugins."""
        fn1 = lambda args: 0
        fn2 = lambda args: 1
        ep1 = MockEntryPoint("plugin-one", "pkg1.cli:main", lambda: fn1)
        ep2 = MockEntryPoint("plugin-two", "pkg2.cli:main", lambda: fn2)

        mock_eps = MagicMock()
        mock_eps.select.return_value = [ep1, ep2]
        mock_entry_points.return_value = mock_eps

        plugins = discover_plugins()

        assert len(plugins) == 2
        assert "plugin-one" in plugins
        assert "plugin-two" in plugins
        assert plugins["plugin-one"] == fn1
        assert plugins["plugin-two"] == fn2

    @patch("mcl.plugins.importlib.metadata.entry_points")
    def test_discover_plugin_load_failure(self, mock_entry_points: MagicMock) -> None:
        """Test that plugin load failures don't crash discovery."""

        def failing_load() -> Any:
            raise ImportError("Plugin module not found")

        ep_good = MockEntryPoint("good-plugin", "good.cli:main", lambda: lambda a: 0)
        ep_bad = MockEntryPoint("bad-plugin", "bad.cli:main", failing_load)

        mock_eps = MagicMock()
        mock_eps.select.return_value = [ep_good, ep_bad]
        mock_entry_points.return_value = mock_eps

        plugins = discover_plugins()

        # Only the good plugin should be loaded
        assert len(plugins) == 1
        assert "good-plugin" in plugins
        assert "bad-plugin" not in plugins

    @patch("mcl.plugins.importlib.metadata.entry_points")
    def test_discover_legacy_api(self, mock_entry_points: MagicMock) -> None:
        """Test discovery using legacy Python 3.8-3.9 API."""
        test_fn = lambda args: 0
        ep = MockEntryPoint("test-plugin", "test_pkg.cli:main", lambda: test_fn)

        # Simulate legacy API (dict-like access, no select method)
        mock_eps = {"mcl.plugins": [ep]}
        mock_entry_points.return_value = mock_eps

        plugins = discover_plugins()

        assert "test-plugin" in plugins
        assert plugins["test-plugin"] == test_fn

    @patch("mcl.plugins.importlib.metadata.entry_points")
    def test_discover_legacy_api_no_plugins(self, mock_entry_points: MagicMock) -> None:
        """Test legacy API when no plugins are registered."""
        mock_eps: dict[str, list[Any]] = {}
        mock_entry_points.return_value = mock_eps

        plugins = discover_plugins()

        assert plugins == {}


class TestListPlugins:
    """Tests for listing plugins with metadata."""

    @patch("mcl.plugins.importlib.metadata.entry_points")
    @patch("mcl.plugins.importlib.metadata.distribution")
    def test_list_no_plugins(
        self, mock_dist: MagicMock, mock_entry_points: MagicMock
    ) -> None:
        """Test listing when no plugins are installed."""
        mock_eps = MagicMock()
        mock_eps.select.return_value = []
        mock_entry_points.return_value = mock_eps

        plugins = list_plugins()

        assert plugins == []

    @patch("mcl.plugins.importlib.metadata.entry_points")
    @patch("mcl.plugins.importlib.metadata.distribution")
    def test_list_plugin_with_version(
        self, mock_dist: MagicMock, mock_entry_points: MagicMock
    ) -> None:
        """Test listing plugin with version information."""
        ep = MockEntryPoint("test-plugin", "test_pkg.cli:main")

        mock_eps = MagicMock()
        mock_eps.select.return_value = [ep]
        mock_entry_points.return_value = mock_eps

        # Mock distribution metadata
        mock_dist_obj = MagicMock()
        mock_dist_obj.version = "1.2.3"
        mock_dist.return_value = mock_dist_obj

        plugins = list_plugins()

        assert len(plugins) == 1
        assert plugins[0] == ("test-plugin", "v1.2.3")

    @patch("mcl.plugins.importlib.metadata.entry_points")
    @patch("mcl.plugins.importlib.metadata.distribution")
    def test_list_plugin_version_not_found(
        self, mock_dist: MagicMock, mock_entry_points: MagicMock
    ) -> None:
        """Test listing when version cannot be determined."""
        ep = MockEntryPoint("test-plugin", "test_pkg.cli:main")

        mock_eps = MagicMock()
        mock_eps.select.return_value = [ep]
        mock_entry_points.return_value = mock_eps

        # Simulate version lookup failure
        mock_dist.side_effect = Exception("Not found")

        plugins = list_plugins()

        assert len(plugins) == 1
        assert plugins[0] == ("test-plugin", "unknown version")

    @patch("mcl.plugins.importlib.metadata.entry_points")
    def test_list_legacy_api(self, mock_entry_points: MagicMock) -> None:
        """Test listing with legacy Python 3.8-3.9 API."""
        ep = MockEntryPoint("test-plugin", "test_pkg.cli:main")

        mock_eps = {"mcl.plugins": [ep]}
        mock_entry_points.return_value = mock_eps

        plugins = list_plugins()

        assert len(plugins) == 1
        assert plugins[0][0] == "test-plugin"
