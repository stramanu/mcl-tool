# 💡 mcl Plugin System — Proof of Concept

## Overview

The goal of the plugin system is to extend **mcl** beyond static JSON-defined commands, allowing developers to create and share **modular command extensions** (plugins).
Each plugin can expose its own CLI interface under the main `mcl` command, providing new features, workflows, or integrations without modifying the mcl core.

---

## Concept

Each plugin acts as a **sub-command** of `mcl`, automatically detected and loaded at runtime.

Example:

```bash
mcl pippo
```

If the plugin `pippo` is installed, mcl delegates execution to the plugin’s own CLI handler.
Otherwise, it falls back to the default behavior (scripts from `mcl.json`).

---

## Plugin Structure

A plugin is simply a Python package exposing an entry point in a specific namespace, for example:

```
mcl_plugin_pippo/
  ├── __init__.py
  ├── cli.py
  └── setup.py
```

### setup.py

```python
from setuptools import setup

setup(
    name='mcl-plugin-pippo',
    entry_points={
        'mcl.plugins': [
            'pippo = mcl_plugin_pippo.cli:main'
        ]
    },
)
```

### cli.py

```python
def main():
    print("Hello from the Pippo plugin!")
```

---

## Plugin Discovery

At runtime, mcl automatically discovers installed plugins via **Python entry points**, similar to how tools like `pytest` or `flake8` load extensions.

Pseudocode:

```python
import importlib.metadata

def load_plugins():
    plugins = importlib.metadata.entry_points(group='mcl.plugins')
    for plugin in plugins:
        print(f"Loaded plugin: {plugin.name}")
```

This enables any developer to publish an extension to PyPI (e.g., `mcl-plugin-docker`, `mcl-plugin-git`) and make it instantly available with:

```bash
pip install mcl-plugin-git
```

---

## Command Routing

Once loaded, mcl routes commands based on the first argument:

```python
# mcl main
if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd in registered_plugins:
        registered_plugins[cmd]()
    else:
        run_local_or_global_command(cmd)
```

---

## Benefits

* 🔌 **Extensibility** — Anyone can build and publish mcl plugins.
* 🧩 **Isolation** — Plugins are independent Python packages.
* 🧠 **Discoverability** — Plugins automatically register themselves via entry points.
* 💬 **Community-driven** — Developers can share tools that extend mcl without changing its core.

---

## Future Vision

* `mcl plugin list` → Show installed plugins
* `mcl plugin search <keyword>` → Fetch from a curated registry
* `mcl plugin install <name>` → Auto-install from PyPI
* `mcl plugin update` → Keep all extensions up to date

---

### Example Future Plugin Ideas

* `mcl docker` → Manage Docker containers from templates
* `mcl ai` → Generate commands or docs with LLMs
* `mcl git` → Smart Git shortcuts and hooks
* `mcl test` → Unified testing runner

---

## Conclusion

This plugin system would turn mcl into a **modular ecosystem** rather than a single-purpose tool.
It keeps the core minimal but allows infinite expansion through the community.
