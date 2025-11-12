# Plugin System - Ideas & Brainstorming

This document collects ideas, considerations, and possible future evolutions of the plugin system.

---

## 🎯 Core Ideas (Already Planned)

### Plugin Discovery via Entry Points
- ✅ Standard Python mechanism
- ✅ Automatic registration
- ✅ No manual config needed
- ✅ Works with pip/poetry/uv

### Priority System
Built-in Commands > Plugins > Local Scripts > Global Scripts

**Rationale**: Allows progressive override while keeping core stable.

---

## 💡 Future Enhancement Ideas

### 1. Plugin Aliases
Allow aliases for plugins in `mcl.json`:

```json
{
  "plugin_aliases": {
    "d": "docker",
    "g": "git",
    "k": "kubectl"
  }
}
```

**Use Case**: `mcl d ps` invece di `mcl docker ps`  
**Complexity**: LOW  
**Value**: MEDIUM  
**Status**: 🟡 CONSIDER

---

### 2. Plugin Hooks System
Plugin possono registrare hook per eventi mcl:

```python

### 2. Plugin Hooks System
Plugins can register hooks for mcl events:

```python
# In plugin
@mcl_hook('before_script')
def log_execution(script_name: str, args: list[str]) -> None:
```

@mcl_hook('after_script')
def notify_completion(script_name: str, exit_code: int) -> None:
    if exit_code != 0:
        send_notification(f"Script {script_name} failed!")
```

**Possible Hooks**:
- `before_script` / `after_script`
- `config_loaded`
- `plugin_discovered`

**Use Cases**:
- Logging plugin
- Notification plugin
- Telemetry plugin
- Script wrapper plugin

**Complexity**: HIGH  
**Value**: HIGH  
**Status**: 🔵 FUTURE (v0.5+)

---

### 3. Plugin Dependencies
Plugins declare dependencies on other plugins:

```toml
[project]
name = "mcl-plugin-advanced"
dependencies = ["mcl-plugin-docker>=1.0"]
```

mcl verifies compatibility and loading order.

**Complexity**: MEDIUM  
**Value**: MEDIUM  
**Status**: 🔵 FUTURE

---

### 4. Plugin Configuration Schema
Plugins declare schema for their config:

```python
# In plugin
def get_config_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "default_image": {"type": "string"},
            "registry": {"type": "string", "format": "uri"}
        },
        "required": ["default_image"]
    }
```

mcl validates config at load time.

**Complexity**: MEDIUM  
**Value**: MEDIUM  
**Status**: 🟡 CONSIDER

---

### 5. Interactive Plugin Discovery
Command to discover and install plugins:

```bash
$ mcl plugin search docker
Found 3 plugins:

  1. mcl-plugin-docker (★ 245)
     Docker container management
     Author: @johndoe
     
  2. mcl-plugin-docker-compose (★ 89)
     Docker Compose shortcuts
     Author: @janedoe
  
  3. mcl-plugin-docker-deploy (★ 12)
     Production deployment tools
     Author: @acme-corp

Install with: mcl plugin install <name>
```

**Data Source**:
- PyPI search API
- Custom registry (GitHub repo)
- Package name convention: `mcl-plugin-*`

**Complexity**: MEDIUM  
**Value**: HIGH  
**Status**: 🟢 PLANNED (M4?)

---

### 6. Plugin Sandbox/Permissions
Limit plugin capabilities:

```toml
[tool.mcl.plugin]
permissions = [
    "filesystem:read",
    "network:http",
    "subprocess:execute"
]
```

mcl asks for confirmation before executing plugins with sensitive permissions.

**Complexity**: VERY HIGH  
**Value**: HIGH (security)  
**Status**: 🔵 FUTURE (v1.0+)

---

### 7. Web-based Plugin UI
Plugins expose optional web interface:

```bash
$ mcl docker ui --port 8080
Starting Docker plugin UI at http://localhost:8080
```

**Use Cases**:
- Dashboard for status monitoring
- Visual configuration editor
- Log viewer
- Interactive command builder

**Complexity**: HIGH  
**Value**: MEDIUM  
**Status**: 🔵 FUTURE (nice-to-have)

---

### 8. Plugin Templates Library
Beyond generator, library of templates:

```bash
$ mcl plugin create my-tool --template click-app
$ mcl plugin create my-wrapper --template simple-wrapper
$ mcl plugin create my-api --template api-client
```

**Templates**:
- `simple-wrapper`: Single command wrapper
- `click-app`: Multi-command Click application
- `api-client`: REST API wrapper with auth
- `config-driven`: Load commands from YAML/JSON

**Complexity**: MEDIUM  
**Value**: MEDIUM  
**Status**: 🟡 CONSIDER

---

### 9. Plugin Marketplace/Registry
Curated list of official + community plugins:

Website: `mcltools.dev/plugins`

Categories:
- Cloud & Infrastructure (AWS, GCP, Azure, Terraform)
- Containers (Docker, Kubernetes, Podman)
- Development (Git, GitHub, GitLab)
- Databases (Postgres, MySQL, Redis)
- AI/ML (OpenAI, Anthropic, HuggingFace)
- Utilities (Notifications, Logging, Backups)

**Features**:
- Star ratings
- Download stats
- Compatibility matrix
- Security badges
- Official vs Community badge

**Complexity**: HIGH (infra required)  
**Value**: HIGH (ecosystem growth)  
**Status**: 🔵 FUTURE (post-v1.0)

---

## 🛠️ Implementation Ideas

### Plugin Context Object
Invece di solo `args`, passare ricco context object:

```python
from mcl.plugin import PluginContext

def main(ctx: PluginContext) -> int:
    # Access mcl config
    config = ctx.config
    plugin_config = ctx.get_plugin_config('my-plugin')
    
    # Access flags
    if ctx.dry_run:
        print("Dry run mode")
    
    # Access args
    args = ctx.args
    
    # Logging
    ctx.logger.info("Plugin started")
    
    # Access mcl API
    ctx.run_script('deploy')  # Run another mcl script
    
    return 0
```

**Complexity**: MEDIUM  
**Value**: HIGH  
**Status**: 🟢 CONSIDER for v0.3

---

### 10. Plugin Auto-update
Notify when plugin has available update:

```bash
$ mcl docker ps
⚠️  Update available: mcl-plugin-docker 1.2.0 → 1.3.0
   Run: mcl plugin update docker

[docker output...]
```

**Complexity**: LOW  
**Value**: MEDIUM  
**Status**: 🟡 CONSIDER

---

### Plugin Telemetry (Opt-in)
Plugins can send usage stats (anonymous):

```python
from mcl.plugin import track_event

def main(args):
    track_event('command_executed', {'subcommand': args[0]})
    # ...
```

Helps plugin authors understand usage patterns.

**Privacy**: Must be opt-in, completely anonymous  
**Complexity**: MEDIUM  
**Value**: LOW (for ecosystem)  
**Status**: 🔴 CONTROVERSIAL - needs discussion

---

## 🎨 Plugin Ideas for Ecosystem

### Official Plugins (by mcl team)

1. **mcl-plugin-git**
   - Smart git shortcuts
   - Interactive rebase helper
   - Conventional commits helper
   - PR creation

2. **mcl-plugin-docker**
   - Container management
   - Image building from templates
   - Compose shortcuts
   - Registry operations

3. **mcl-plugin-k8s**
   - Kubectl shortcuts
   - Context switching
   - Pod log tailing
   - Port forwarding helper

4. **mcl-plugin-notify**
   - Desktop notifications
   - Slack/Discord webhooks
   - Email alerts
   - SMS via Twilio

5. **mcl-plugin-ai**
   - Generate shell commands from natural language
   - Explain command output
   - Code review bot
   - Documentation generator

---

### Community Plugin Ideas

6. **mcl-plugin-aws**
   - AWS CLI shortcuts
   - Profile management
   - S3 operations
   - EC2 instance management

7. **mcl-plugin-gcp**
   - gcloud shortcuts
   - Project switching
   - GCS operations

8. **mcl-plugin-terraform**
   - Plan/apply shortcuts
   - Workspace management
   - State inspection

9. **mcl-plugin-dotenv**
   - Environment variable management
   - .env file switching
   - Secret encryption

10. **mcl-plugin-tmux**
    - Session management
    - Window/pane creation
    - Script execution in panes

11. **mcl-plugin-backup**
    - Automated backups
    - Multiple destinations
    - Encryption support

12. **mcl-plugin-monitor**
    - System monitoring dashboard
    - Process management
    - Log aggregation

---

## 🔬 Technical Experiments

### Idea: WASM Plugins
Support plugins written in any language via WebAssembly:

```bash
mcl my-rust-plugin  # Compiled to WASM
```

**Pros**: 
- Language agnostic
- Sandboxed by default
- Fast

**Cons**:
- High complexity
- Limited ecosystem
- Debugging harder

**Status**: 🔴 RESEARCH (very future)

---

### Idea: Remote Plugins
Execute plugins on remote servers:

```toml
[tool.mcl.plugins.remote]
production-deploy = "ssh://prod-server/opt/mcl-plugins/deploy"
```

**Use Cases**:
- Run on jump host
- Execute in specific environment
- Security (credentials stay on server)

**Complexity**: HIGH  
**Value**: MEDIUM  
**Status**: 🔵 FUTURE

---

### Idea: Plugin Composition
Chain multiple plugins:

```bash
mcl docker ps | mcl format table | mcl notify slack
```

Each plugin implements stdin/stdout interface.

**Complexity**: MEDIUM  
**Value**: HIGH  
**Status**: 🟡 CONSIDER

---

## 🤔 Open Questions

1. **Plugin versioning**: Should mcl enforce plugin version compatibility?
   - Option A: Require plugin to declare `mcl-tool>=0.3.0`
   - Option B: Runtime capability detection
   - Option C: No enforcement (YOLO)
   - **Leaning toward**: Option A

2. **Plugin namespacing**: Prevent command collisions?
   - Option A: Strict namespace (no collisions allowed)
   - Option B: Priority system (plugin > script)
   - Option C: User chooses via config
   - **Current approach**: Option B

3. **Plugin distribution**: Only PyPI or custom registry?
   - Option A: PyPI only (simple)
   - Option B: Custom registry (controlled)
   - Option C: Both (flexible)
   - **Leaning toward**: Option A initially, Option C future

4. **Plugin API stability**: When to lock plugin API?
   - Option A: v0.3.0 (first plugin release)
   - Option B: v1.0.0 (stable release)
   - **Leaning toward**: Option B (allow experimentation)

5. **Plugin config location**: In `mcl.json` or separate file?
   - Option A: Embedded in `mcl.json` under `plugins` key
   - Option B: Separate `mcl-plugins.json`
   - **Current approach**: Option A (simpler)

---

## 📊 Priority Matrix

| Idea | Value | Complexity | Priority | Phase |
|------|-------|------------|----------|-------|
| Plugin Hooks | HIGH | HIGH | MEDIUM | v0.5 |
| Plugin Discovery CLI | HIGH | MEDIUM | HIGH | v0.4 |
| Plugin Context Object | HIGH | MEDIUM | HIGH | v0.3 |
| Plugin Aliases | MEDIUM | LOW | MEDIUM | v0.4 |
| Configuration Schema | MEDIUM | MEDIUM | LOW | v0.5 |
| Plugin Marketplace | HIGH | HIGH | LOW | v1.0+ |
| Plugin Sandbox | HIGH | VERY HIGH | LOW | v1.0+ |
| Web UI | MEDIUM | HIGH | LOW | Future |
| WASM Support | LOW | VERY HIGH | LOW | Research |

---

## 💬 Community Feedback

_This section will be updated as we gather feedback from users and contributors._

### Requested Features
- (None yet - plugin system not released)

### Pain Points
- (TBD)

### Success Stories
- (TBD)

---

## 📝 Notes

### Design Philosophy
- **Keep Core Minimal**: Plugin system should add zero overhead when unused
- **Progressive Enhancement**: Basic plugins are trivial, advanced features optional
- **Backwards Compatibility**: Existing scripts must never break
- **Developer Friendly**: Creating plugins should be joyful, not painful
- **Security Aware**: Think about security from day 1, even if not enforced yet

### Inspiration From
- pytest plugin system (entry points, hooks)
- Click plugin pattern (command groups)
- VS Code extensions (marketplace, discoverability)
- Homebrew taps (community distribution)
- kubectl plugins (binary approach, but we're Python)

---

**Last Updated**: 2025-10-27  
**Contributors**: AI Assistant (initial brainstorm)  
**Status**: 🟡 LIVING DOCUMENT - Add ideas as they come!
