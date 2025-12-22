"""Utilities for enumerating available scripts."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Tuple

ScriptTree = Mapping[str, Any]


def list_script_paths(scripts: ScriptTree) -> List[str]:
    """Return space-separated command paths from the provided script mapping."""

    paths: List[str] = []

    def _walk(prefix: List[str], node: Any) -> None:
        if isinstance(node, Mapping):
            if not node:
                paths.append(" ".join(prefix))
                return
            for key, child in node.items():
                _walk(prefix + [str(key)], child)
            return

        if isinstance(node, Iterable) and not isinstance(node, (str, bytes)):
            paths.append(" ".join(prefix))
            return

        if isinstance(node, str):
            paths.append(" ".join(prefix))
            return

        # unsupported types are ignored; executor will raise at runtime

    sorted_keys = sorted(scripts.keys())
    for top in sorted_keys:
        _walk([str(top)], scripts[top])

    return sorted(paths)


def extract_script_maps(
    config: Mapping[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Return global and local script dictionaries if available."""

    global_scripts = config.get("__global_scripts__") or {}
    local_scripts = config.get("__local_scripts__") or {}

    gs = global_scripts if isinstance(global_scripts, dict) else {}
    ls = local_scripts if isinstance(local_scripts, dict) else {}

    return gs, ls
