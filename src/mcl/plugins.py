"""Plugin discovery and management for mcl.

This module provides functionality to discover and manage mcl plugins
via Python entry points in the 'mcl.plugins' namespace.
"""

from __future__ import annotations

import importlib.metadata
import logging
from typing import Callable, Dict, List, Tuple

logger = logging.getLogger(__name__)

PluginEntry = Callable[[List[str]], int]


def discover_plugins() -> Dict[str, PluginEntry]:
    """Discover all installed mcl plugins via entry points.

    Plugins are discovered through the 'mcl.plugins' entry point namespace.
    Failed plugin loads are logged but do not prevent other plugins from loading.

    Returns:
        Dictionary mapping plugin names to their entry point callables.
        Each callable accepts a list of command-line arguments and returns
        an exit code (0 for success).

    Example:
        >>> plugins = discover_plugins()
        >>> if 'docker' in plugins:
        ...     exit_code = plugins['docker'](['ps', '-a'])
    """
    plugins: Dict[str, PluginEntry] = {}

    try:
        eps = importlib.metadata.entry_points()

        # Python 3.10+ uses select(), 3.8-3.9 uses dict-like access
        if hasattr(eps, "select"):
            group = eps.select(group="mcl.plugins")
        else:
            group = eps.get("mcl.plugins", [])

        for ep in group:
            try:
                plugin_fn = ep.load()
                plugins[ep.name] = plugin_fn
                logger.debug(f"Loaded plugin: {ep.name}")
            except Exception as e:
                logger.warning(f"Failed to load plugin '{ep.name}': {e}")

    except Exception as e:
        logger.error(f"Error discovering plugins: {e}")

    return plugins


def list_plugins() -> List[Tuple[str, str]]:
    """List all available plugins with their metadata.

    Attempts to retrieve version information for each plugin by looking up
    the distribution metadata. If version cannot be determined, reports
    "unknown version".

    Returns:
        List of (name, version/description) tuples.

    Example:
        >>> plugins = list_plugins()
        >>> for name, version in plugins:
        ...     print(f"{name}: {version}")
        docker: v1.0.0
        git: v0.5.2
    """
    plugins_info: List[Tuple[str, str]] = []

    try:
        eps = importlib.metadata.entry_points()

        # Python 3.10+ uses select(), 3.8-3.9 uses dict-like access
        if hasattr(eps, "select"):
            group = eps.select(group="mcl.plugins")
        else:
            group = eps.get("mcl.plugins", [])

        for ep in group:
            # Try to get package version
            try:
                # Extract package name from entry point value (e.g., 'pkg.module:func')
                pkg_name = ep.value.split(":")[0].split(".")[0]
                dist = importlib.metadata.distribution(pkg_name)
                version = dist.version
                plugins_info.append((ep.name, f"v{version}"))
            except Exception:
                plugins_info.append((ep.name, "unknown version"))

    except Exception as e:
        logger.error(f"Error listing plugins: {e}")

    return plugins_info
