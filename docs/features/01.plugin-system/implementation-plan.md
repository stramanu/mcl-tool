# Plugin System Implementation Plan

## Objective
Implement an extensible plugin system for mcl-tool while maintaining full backward compatibility.

---

## Milestone 1: Core Plugin Infrastructure
**Target**: Basic discovery and execution functionality

### Task 1.1: Plugin Discovery Module
**File**: `src/mcl/plugins.py`

```python
"""Plugin discovery and management for mcl."""

import importlib.metadata
import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)

PluginEntry = Callable[[list[str]], int]


def discover_plugins() -> Dict[str, PluginEntry]:
    """
    Discover all installed mcl plugins via entry points.
    
    Returns:
        Dictionary mapping plugin names to their entry point callables.
    """
    plugins: Dict[str, PluginEntry] = {}
    
    try:
        eps = importlib.metadata.entry_points()
        
        # Python 3.10+ uses select(), 3.8-3.9 uses dict-like access
        if hasattr(eps, 'select'):
            group = eps.select(group='mcl.plugins')
        else:
            group = eps.get('mcl.plugins', [])
        
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


def list_plugins() -> list[tuple[str, str]]:
    """
    List all available plugins with their metadata.
    
    Returns:
        List of (name, version/description) tuples.
    """
    plugins_info: list[tuple[str, str]] = []
    
    try:
        eps = importlib.metadata.entry_points()
        if hasattr(eps, 'select'):
            group = eps.select(group='mcl.plugins')
        else:
            group = eps.get('mcl.plugins', [])
        
        for ep in group:
            # Try to get package version
            try:
                dist = importlib.metadata.distribution(ep.value.split(':')[0].split('.')[0])
                version = dist.version
                plugins_info.append((ep.name, f"v{version}"))
            except Exception:
                plugins_info.append((ep.name, "unknown version"))
    
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
    
    return plugins_info
```

**Tests**: `tests/test_plugins.py`
- Mock entry points with pytest
- Test discovery with 0, 1, N plugins
- Test plugin loading error

**Estimate**: 2 hours

---

### Task 1.2: ScriptGroup Enhancement
**File**: `src/mcl/cli.py`

Modifications to `ScriptGroup` class:

```python
from .plugins import discover_plugins

class ScriptGroup(click.Group):
    """Custom Click group with plugin support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plugins = discover_plugins()
        if self._plugins:
            logger.debug(f"Loaded {len(self._plugins)} plugin(s)")

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        # 1. Check built-in commands first
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command

        # 2. Check if it's a registered plugin
        if cmd_name in self._plugins:
            return self._create_plugin_command(cmd_name)

        # 3. Fallback to script execution from mcl.json
        run_command = super().get_command(ctx, "run")
        if run_command is None:
            return None

        # ... existing ScriptAliasCommand logic ...

    def _create_plugin_command(self, name: str) -> click.Command:
        """Create a Click command wrapper for a plugin."""
        plugin_fn = self._plugins[name]

        class PluginCommand(click.Command):
            def __init__(self) -> None:
                super().__init__(name)
                self.allow_extra_args = True
                self.ignore_unknown_options = True

            def invoke(self, ctx: click.Context) -> Any:
                # Pass remaining args to plugin
                args = list(ctx.args)
                
                # Pass mcl context via env vars
                import os
                if ctx.obj:
                    if ctx.obj.get('dry_run'):
                        os.environ['MCL_DRY_RUN'] = '1'
                    if ctx.obj.get('share_vars'):
                        os.environ['MCL_SHARE_VARS'] = '1'
                
                try:
                    exit_code = plugin_fn(args)
                    if exit_code != 0:
                        raise click.Abort()
                except Exception as e:
                    logger.error(f"Plugin '{name}' failed: {e}")
                    raise click.Abort()

        return PluginCommand()
```

**Tests**: Update `tests/test_cli.py`
- Test plugin invocation
- Test precedence: plugin > script
- Test context propagation

**Estimate**: 3 hours

---

### Task 1.3: Example Test Plugin
**Directory**: `tests/fixtures/mcl_plugin_test/`

Structure:
```
tests/fixtures/mcl_plugin_test/
├── mcl_plugin_test/
│   ├── __init__.py
│   └── cli.py
└── setup.py
```

**setup.py**:
```python
from setuptools import setup, find_packages

setup(
    name='mcl-plugin-test',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'mcl.plugins': [
            'test-plugin = mcl_plugin_test.cli:main',
        ],
    },
)
```

**cli.py**:
```python
import sys

def main(args: list[str]) -> int:
    """Test plugin for mcl integration tests."""
    print(f"TEST_PLUGIN_CALLED with args: {args}")
    
    if '--fail' in args:
        return 1
    
    return 0
```

**Tests**: Integration test that installs plugin in test venv

**Estimate**: 1 hour

---

## Milestone 2: Plugin Management Commands
**Target**: Commands to manage installed plugins

### Task 2.1: `mcl plugin list`
**File**: `src/mcl/cli.py`

```python
@cli.group()
def plugin() -> None:
    """Manage mcl plugins."""
    pass


@plugin.command(name='list')
def plugin_list() -> None:
    """List all installed mcl plugins."""
    from .plugins import list_plugins
    
    plugins = list_plugins()
    
    if not plugins:
        click.echo("No plugins installed.")
        click.echo("\nInstall plugins with: pip install mcl-plugin-<name>")
        return
    
    click.echo("Installed plugins:")
    for name, version in plugins:
        click.echo(f"  • {name} ({version})")
```

**Tests**: `tests/test_cli.py`

**Estimate**: 1 hour

---

### Task 2.2: `mcl plugin info`
**File**: `src/mcl/cli.py`

```python
@plugin.command(name='info')
@click.argument('name')
def plugin_info(name: str) -> None:
    """Show detailed information about a plugin."""
    import importlib.metadata
    
    try:
        eps = importlib.metadata.entry_points()
        if hasattr(eps, 'select'):
            group = eps.select(group='mcl.plugins')
        else:
            group = eps.get('mcl.plugins', [])
        
        for ep in group:
            if ep.name == name:
                click.echo(f"Plugin: {ep.name}")
                click.echo(f"Entry Point: {ep.value}")
                
                # Try to get package metadata
                try:
                    pkg_name = ep.value.split(':')[0].split('.')[0]
                    dist = importlib.metadata.distribution(pkg_name)
                    click.echo(f"Package: {dist.name}")
                    click.echo(f"Version: {dist.version}")
                    if dist.metadata.get('Summary'):
                        click.echo(f"Description: {dist.metadata['Summary']}")
                    if dist.metadata.get('Home-page'):
                        click.echo(f"Homepage: {dist.metadata['Home-page']}")
                except Exception:
                    pass
                
                return
        
        click.echo(f"Plugin '{name}' not found.", err=True)
        raise click.Abort()
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
```

**Tests**: `tests/test_cli.py`

**Estimate**: 1.5 hours

---

## Milestone 3: Documentation & Examples
**Target**: Guides for developers and users

### Task 3.1: Plugin Development Guide
**File**: `docs/features/01.plugin-system/developer-guide.md`

Content:
- Minimal plugin structure
- Entry point configuration
- Best practices
- Testing
- Publishing to PyPI

**Estimate**: 2 hours

---

### Task 3.2: Example Plugin Repository
**Repository**: `mcl-plugin-example` (separate)

Complete example plugin with:
- Click-based CLI
- Config integration
- Tests
- Documentation
- GitHub Actions for CI/CD

**Estimate**: 3 hours

---

### Task 3.3: User Documentation
**File**: `docs/plugins.md`

Content:
- How to install plugins
- List of official plugins (curated)
- Troubleshooting

**Estimate**: 1 hour

---

## Milestone 4: Advanced Features
**Target**: Optional advanced functionality

### Task 4.1: Plugin Configuration Support
**File**: `src/mcl/config.py`

Add support for `plugins` section in config:
```json
{
  "plugins": {
    "docker": {
      "default_image": "ubuntu:latest"
    }
  }
}
```

Plugins access via: `os.environ['MCL_PLUGIN_CONFIG_DOCKER']` (JSON string)

**Estimate**: 2 hours

---

### Task 4.2: Plugin Template Generator
**Command**: `mcl plugin create <name>`

Generate scaffolding for new plugin:
```
mcl-plugin-<name>/
├── mcl_plugin_<name>/
│   ├── __init__.py
│   └── cli.py
├── tests/
│   └── test_cli.py
├── setup.py
├── README.md
└── LICENSE
```

**Estimate**: 3 hours

---

## Timeline Estimate

| Milestone | Tasks | Estimated Hours | Priority |
|-----------|-------|-----------------|----------|
| M1: Core Infrastructure | 1.1, 1.2, 1.3 | 6h | **CRITICAL** |
| M2: Management Commands | 2.1, 2.2 | 2.5h | **HIGH** |
| M3: Documentation | 3.1, 3.2, 3.3 | 6h | **HIGH** |
| M4: Advanced Features | 4.1, 4.2 | 5h | MEDIUM |
| **TOTAL** | | **19.5h** | |

---

## Testing Strategy

### Unit Tests
- `tests/test_plugins.py`: Discovery, listing
- `tests/test_cli.py`: Command routing with plugin

### Integration Tests
- `tests/integration/test_plugin_execution.py`: End-to-end with test plugin
- Install fixture plugin in test venv
- Verify invocation and output

### Manual Testing Checklist
- [ ] Plugin called without args
- [ ] Plugin called with args
- [ ] Plugin with error doesn't crash mcl
- [ ] `--dry-run` passed correctly
- [ ] `--share-vars` passed correctly
- [ ] Plugin vs script collision (plugin wins)
- [ ] `mcl plugin list` shows plugins
- [ ] `mcl plugin info` shows details

---

## Deployment

### Version Bump
- `0.2.0` → `0.3.0` (minor bump, nuova feature)

### Changelog Entry
```markdown
## [0.3.0] - 2025-XX-XX

### Added
- Plugin system via Python entry points
- `mcl plugin list` command to show installed plugins
- `mcl plugin info <name>` command for plugin details
- Plugin development documentation

### Changed
- Command resolution now prioritizes plugins over scripts
```

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Example plugin published
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Git tag created
- [ ] PyPI release

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing scripts | LOW | HIGH | Extensive testing, plugin priority below built-ins |
| Plugin crashes mcl | MEDIUM | MEDIUM | Try-catch wrapping, graceful degradation |
| Python version compatibility | LOW | MEDIUM | Test matrix 3.8-3.12 |
| Entry point API changes | LOW | LOW | Conditional code for legacy API |

---

## Success Criteria

- ✅ Existing mcl commands work unchanged
- ✅ Test plugin installable and invocable
- ✅ `mcl plugin list` shows plugins
- ✅ Plugin failure doesn't crash mcl
- ✅ Complete documentation for devs and users
- ✅ Zero breaking changes for existing users

---

## Next Actions

1. **Setup Branch**: `git checkout -b feature/plugin-system`
2. **Start M1.1**: Implement `plugins.py`
3. **Write Tests First**: TDD approach
4. **Iterate**: Small commits, test often
5. **Review**: Self-review before merge

See [progress-tracker.md](./progress-tracker.md) for detailed tracking.
