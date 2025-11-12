# Plugin System Architecture

## Overview
Proposed architecture for mcl-tool's plugin system enabling modular extension via Python entry points.

## Design Goals
1. **Backward Compatibility**: Existing commands from `mcl.json` must continue to work
2. **Priority**: Plugins > Local Commands > Global Commands
3. **Isolation**: Independent plugins without core modifications
4. **Discoverability**: Auto-registration via entry points

---

## Current Architecture

### CLI Entry Point
- `cli.py`: Uses `ScriptGroup` (custom Click.Group) for routing
- Automatic fallback to `run` command for non-command scripts
- Context object shares `dry_run` and `share_vars`

### Command Resolution Flow
```
mcl <cmd> <args...>
  ↓
ScriptGroup.get_command(cmd)
  ↓
Built-in command? → Execute (init, edit, run)
  ↓
No → Create ScriptAliasCommand → Invoke `run` with cmd_name
  ↓
load_config() → Resolve script from JSON → execute()
```

---

## Proposed Plugin Architecture

### Entry Point Namespace
```python
# setup.py / pyproject.toml
[project.entry-points."mcl.plugins"]
pippo = "mcl_plugin_pippo.cli:main"
docker = "mcl_plugin_docker.cli:main"
```

### Plugin Discovery Module
New module: `src/mcl/plugins.py`

```python
import importlib.metadata
from typing import Dict, Callable

def discover_plugins() -> Dict[str, Callable]:
    """Load all installed mcl plugins via entry points."""
    plugins = {}
    eps = importlib.metadata.entry_points()
    
    # Python 3.10+ uses select(), 3.8-3.9 uses dict-like access
    group = eps.select(group='mcl.plugins') if hasattr(eps, 'select') else eps.get('mcl.plugins', [])
    
    for ep in group:
        try:
            plugins[ep.name] = ep.load()
        except Exception as e:
            # Log warning but don't block startup
            pass
    
    return plugins
```

### Modified Command Resolution Flow
```
mcl <cmd> <args...>
  ↓
ScriptGroup.get_command(cmd)
  ↓
Built-in command? → Execute (init, edit, run, plugin)
  ↓
Registered plugin? → Invoke plugin entry point
  ↓
Script in mcl.json? → Execute as before
  ↓
Not found → Error
```

---

## Integration Points

### 1. ScriptGroup Enhancement
```python
class ScriptGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plugins = discover_plugins()  # Cache at init
    
    def get_command(self, ctx, cmd_name):
        # 1. Built-in commands
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command
        
        # 2. Plugin commands
        if cmd_name in self._plugins:
            return self._create_plugin_command(cmd_name)
        
        # 3. Fallback to script execution
        return self._create_script_alias(cmd_name)
```

### 2. Plugin Command Wrapper
```python
def _create_plugin_command(self, name: str) -> click.Command:
    """Wrap plugin entry point as Click command."""
    plugin_fn = self._plugins[name]
    
    class PluginCommand(click.Command):
        def __init__(self):
            super().__init__(name)
            self.allow_extra_args = True
            self.ignore_unknown_options = True
        
        def invoke(self, ctx):
            # Pass control to plugin
            # Plugin receives sys.argv or ctx.args
            return plugin_fn(ctx.args)
    
    return PluginCommand()
```

---

## Plugin Interface Contract

### Minimal Plugin Structure
```python
# mcl_plugin_example/cli.py

def main(args: list[str]) -> int:
    """
    Plugin entry point.
    
    Args:
        args: Command-line arguments after plugin name
    
    Returns:
        Exit code (0 for success)
    """
    print(f"Plugin called with: {args}")
    return 0
```

### Advanced Plugin (Click-based)
```python
import click

@click.command()
@click.argument('name')
@click.option('--greeting', default='Hello')
def main(name: str, greeting: str) -> int:
    click.echo(f"{greeting}, {name}!")
    return 0
```

---

## Plugin Management Commands

### Phase 1 (Core System)
- Plugin discovery and execution
- No management commands

### Phase 2 (Management CLI)
```bash
mcl plugin list         # List installed plugins
mcl plugin info <name>  # Details about a plugin
```

### Phase 3 (Package Management)
```bash
mcl plugin search <keyword>  # Search PyPI with mcl-plugin- prefix
mcl plugin install <name>    # pip install mcl-plugin-<name>
mcl plugin uninstall <name>  # pip uninstall mcl-plugin-<name>
mcl plugin update [<name>]   # pip install --upgrade
```

---

## Compatibility Matrix

| Scenario | Python 3.8 | Python 3.9 | Python 3.10+ |
|----------|------------|------------|--------------|
| Entry point discovery | ✓ (legacy API) | ✓ (legacy API) | ✓ (select API) |
| Plugin execution | ✓ | ✓ | ✓ |
| Type hints | ✓ | ✓ | ✓ |

---

## Security Considerations

1. **Code Execution**: Plugins execute arbitrary code → only from trusted sources
2. **Namespace Isolation**: Plugin name must match entry point to avoid collisions
3. **Error Handling**: Plugin failure must not crash mcl core
4. **Sandboxing**: Future phase, currently plugins have full system access

---

## Testing Strategy

1. **Unit Tests**: `tests/test_plugins.py`
   - Discovery with mock entry points
   - Command resolution with fake plugin
   
2. **Integration Tests**: `tests/integration/test_plugin_execution.py`
   - Install test plugin in venv
   - Verify end-to-end invocation
   
3. **Fixture Plugin**: `tests/fixtures/mcl_plugin_test/`
   - Minimal plugin for testing

---

## Migration Path

### Step 1: Core Plugin System
- [ ] Create `src/mcl/plugins.py`
- [ ] Modify `ScriptGroup` in `cli.py`
- [ ] Test discovery and execution

### Step 2: Documentation
- [ ] Plugin development guide
- [ ] Example plugin repository

### Step 3: Management Commands
- [ ] `mcl plugin list`
- [ ] `mcl plugin info`

### Step 4: Ecosystem
- [ ] Template repository for new plugins
- [ ] Curated list on GitHub/docs

---

## Open Questions

1. **Context Sharing**: How to pass `--dry-run` and `--share-vars` to plugins?
   - Option A: Via environment variables
   - Option B: Via ctx object (requires Click-aware plugins)
   - **Decision**: Environment variables for simplicity

2. **Plugin Config**: Can plugins have their own configuration in `mcl.json`?
   ```json
   {
     "plugins": {
       "docker": {
         "default_image": "ubuntu:latest"
       }
     }
   }
   ```
   - **Decision**: Yes, `plugins` section in config

3. **Version Constraints**: How to manage dependencies between mcl version and plugin?
   - **Decision**: Plugins declare in setup.py: `install_requires=['mcl-tool>=0.2.0']`

---

## Next Steps
See [implementation-plan.md](./implementation-plan.md) for detailed roadmap.
