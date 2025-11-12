# MCP Server Implementation Plan

**Feature**: MCP Server for MCL
**Branch**: `feature/mcp-server`
**Start Date**: 2025-11-12
**Target Completion**: TBD

---

## Implementation Strategy

### Approach: Incremental Development
Build the MCP server in phases, testing each component before moving to the next. Start with minimal functionality and expand iteratively.

### Success Criteria
- ✅ Server starts and responds to MCP protocol initialization
- ✅ Can list and execute at least one MCL script via MCP tool
- ✅ VS Code Copilot can discover and call MCL scripts
- ✅ Proper error handling and logging
- ✅ Full test coverage (unit + integration)

---

## Milestones

### M1: MCP Server Foundation (Week 1)
**Goal**: Basic MCP server that responds to protocol handshake

**Tasks:**
1. Project structure and dependencies
2. Basic MCP server implementation
3. stdio transport setup
4. Protocol initialization handler
5. Health check/ping functionality

**Deliverable**: Server starts and responds to `initialize` requests

---

### M2: Core Tools Implementation (Week 1-2)
**Goal**: Implement essential MCL tools

**Tasks:**
1. `mcl_list_scripts` tool
2. `mcl_get_script_info` tool
3. `mcl_run_script` tool (with dry-run support)
4. Tool input validation
5. Error handling and responses

**Deliverable**: Copilot can list and execute MCL scripts

---

### M3: Resources & Documentation (Week 2)
**Goal**: Provide config access and documentation

**Tasks:**
1. `config://global` resource
2. `config://local` resource
3. `scripts://all` resource
4. `docs://usage` resource
5. Resource caching strategy

**Deliverable**: Copilot has context about MCL configs and usage

---

### M4: Configuration Management (Week 2-3)
**Goal**: Enable script creation and modification

**Tasks:**
1. `mcl_update_config` tool
2. `mcl_init_config` tool
3. Config validation
4. Backup mechanism
5. Atomic file writes

**Deliverable**: Copilot can create/modify MCL scripts

---

### M5: CLI Integration & Testing (Week 3)
**Goal**: Integrate server with MCL CLI and comprehensive testing

**Tasks:**
1. `mcl mcp start` command
2. `mcl mcp test` command
3. Unit tests for all tools
4. Integration tests for protocol
5. E2E tests with real Copilot

**Deliverable**: Production-ready server with full test coverage

---

### M6: Documentation & Polish (Week 3-4)
**Goal**: User documentation and deployment

**Tasks:**
1. User setup guide
2. VS Code configuration instructions
3. Troubleshooting guide
4. Example workflows
5. Release preparation

**Deliverable**: Ready for public release

---

## Detailed Task Breakdown

### M1.1: Project Structure Setup
**Estimated Time**: 1 hour

```bash
src/mcl/mcp/
├── __init__.py
├── server.py       # Main server implementation
├── tools.py        # Tool handlers
├── resources.py    # Resource providers
├── prompts.py      # Prompt templates
└── utils.py        # Helper functions

tests/mcp/
├── __init__.py
├── test_server.py
├── test_tools.py
├── test_resources.py
└── fixtures/
    └── test_configs/
```

**Checklist:**
- [ ] Create directory structure
- [ ] Add `__init__.py` files
- [ ] Create stub files for each module
- [ ] Update pyproject.toml with mcp dependency

---

### M1.2: Add MCP Dependencies
**Estimated Time**: 30 minutes

Update `pyproject.toml`:

```toml
[project]
dependencies = [
    "click>=8.0",
    "mcp>=0.9.0",  # Add MCP SDK
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21.0",  # For async tests
    "mypy>=1.0",
    "black>=23.0",
]
```

**Checklist:**
- [ ] Add mcp dependency
- [ ] Add pytest-asyncio for async testing
- [ ] Run `pip install -e '.[dev]'`
- [ ] Verify imports work

---

### M1.3: Basic Server Implementation
**Estimated Time**: 3 hours

`src/mcl/mcp/server.py`:

```python
"""MCL MCP Server implementation."""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource

logger = logging.getLogger(__name__)


class MCLServer:
    """MCP server for MCL tool."""
    
    def __init__(self) -> None:
        """Initialize MCL MCP server."""
        self.server = Server("mcl-mcp-server")
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available MCL tools."""
            return []  # Will implement in M2
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
            """Execute an MCL tool."""
            raise NotImplementedError(f"Tool {name} not implemented")
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources."""
            return []  # Will implement in M3
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI."""
            raise NotImplementedError(f"Resource {uri} not found")
    
    async def run(self) -> None:
        """Start the MCP server."""
        logger.info("Starting MCL MCP server")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main() -> None:
    """Main entry point for MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    server = MCLServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
```

**Checklist:**
- [ ] Implement MCLServer class
- [ ] Set up stdio transport
- [ ] Add logging
- [ ] Test server starts without errors
- [ ] Test protocol initialization

---

### M1.4: CLI Integration for MCP
**Estimated Time**: 2 hours

Add to `src/mcl/cli.py`:

```python
@cli.group()
def mcp() -> None:
    """MCP server commands."""
    pass


@mcp.command(name="start")
def mcp_start() -> None:
    """Start the MCL MCP server."""
    import asyncio
    from mcl.mcp.server import main as server_main
    
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        click.echo("Server stopped")
    except Exception as e:
        click.secho(f"Server error: {e}", fg="red", err=True)
        raise click.Abort() from e


@mcp.command(name="test")
def mcp_test() -> None:
    """Test MCP server connectivity."""
    click.echo("Testing MCP server...")
    # TODO: Implement simple connectivity test
    click.secho("✓ Server responds to initialize", fg="green")
```

**Checklist:**
- [ ] Add `mcp` command group
- [ ] Implement `mcp start` command
- [ ] Implement `mcp test` command stub
- [ ] Test `mcl mcp start` launches server
- [ ] Add to CLI help output

---

### M2.1: Implement mcl_list_scripts Tool
**Estimated Time**: 3 hours

`src/mcl/mcp/tools.py`:

```python
"""MCP tool implementations for MCL."""

from typing import Any
from mcp.types import Tool

from mcl.config import load_config
from mcl.commands import list_script_paths, extract_script_maps


async def list_scripts_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """
    List all available MCL scripts.
    
    Args:
        arguments: Tool arguments
            - include_global: Include global scripts (default: true)
            - include_local: Include local scripts (default: true)
    
    Returns:
        Dictionary with scripts list
    """
    include_global = arguments.get("include_global", True)
    include_local = arguments.get("include_local", True)
    
    try:
        config = load_config(local=include_local)
        global_scripts, local_scripts = extract_script_maps(config)
        
        scripts = []
        
        if include_local and local_scripts:
            local_paths = list_script_paths(local_scripts)
            for path in local_paths:
                scripts.append({
                    "name": path,
                    "source": "local",
                    "path": path
                })
        
        if include_global and global_scripts:
            global_paths = list_script_paths(global_scripts)
            # Filter out scripts overridden by local
            local_names = {s["name"] for s in scripts}
            for path in global_paths:
                if path not in local_names:
                    scripts.append({
                        "name": path,
                        "source": "global",
                        "path": path
                    })
        
        return {
            "success": True,
            "scripts": scripts,
            "count": len(scripts)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_list_scripts_tool_definition() -> Tool:
    """Get tool definition for mcl_list_scripts."""
    return Tool(
        name="mcl_list_scripts",
        description="List all available MCL scripts from global and local configs",
        inputSchema={
            "type": "object",
            "properties": {
                "include_global": {
                    "type": "boolean",
                    "description": "Include scripts from global config",
                    "default": True
                },
                "include_local": {
                    "type": "boolean",
                    "description": "Include scripts from local config",
                    "default": True
                }
            }
        }
    )
```

**Checklist:**
- [ ] Implement `list_scripts_tool` function
- [ ] Add tool definition
- [ ] Handle config loading errors
- [ ] Return structured response
- [ ] Write unit tests

---

### M2.2: Implement mcl_run_script Tool
**Estimated Time**: 4 hours

Continue in `src/mcl/mcp/tools.py`:

```python
async def run_script_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Execute an MCL script.
    
    Args:
        arguments: Tool arguments
            - script_name: Name of script to run
            - args: Optional list of arguments
            - dry_run: If true, show what would be executed
            - cwd: Optional working directory
    
    Returns:
        Execution result with stdout/stderr
    """
    script_name = arguments.get("script_name")
    script_args = arguments.get("args", [])
    dry_run = arguments.get("dry_run", False)
    cwd = arguments.get("cwd")
    
    if not script_name:
        return {
            "success": False,
            "error": "script_name is required"
        }
    
    try:
        from mcl.config import load_config
        from mcl.executor import execute
        import os
        
        # Change to specified directory if provided
        original_cwd = None
        if cwd:
            original_cwd = os.getcwd()
            os.chdir(cwd)
        
        try:
            config = load_config(local=True)
            
            # Capture output
            import io
            import sys
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            try:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
                
                execute(
                    config,
                    script_name,
                    script_args,
                    dry_run=dry_run,
                    share_vars=False
                )
                
                return {
                    "success": True,
                    "stdout": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue(),
                    "exit_code": 0
                }
            
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        finally:
            if original_cwd:
                os.chdir(original_cwd)
    
    except ValueError as e:
        return {
            "success": False,
            "error": f"Script error: {e}",
            "exit_code": 1
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Execution failed: {e}",
            "exit_code": 1
        }


def get_run_script_tool_definition() -> Tool:
    """Get tool definition for mcl_run_script."""
    return Tool(
        name="mcl_run_script",
        description="Execute an MCL script with optional arguments",
        inputSchema={
            "type": "object",
            "properties": {
                "script_name": {
                    "type": "string",
                    "description": "Name of the script to execute"
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Arguments to pass to the script",
                    "default": []
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, show commands without executing",
                    "default": False
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory for execution"
                }
            },
            "required": ["script_name"]
        }
    )
```

**Checklist:**
- [ ] Implement `run_script_tool` function
- [ ] Capture stdout/stderr
- [ ] Support dry-run mode
- [ ] Handle working directory changes
- [ ] Return structured output
- [ ] Write unit tests
- [ ] Test with real MCL scripts

---

### M3.1: Implement Config Resources
**Estimated Time**: 2 hours

`src/mcl/mcp/resources.py`:

```python
"""MCP resource providers for MCL."""

import json
from pathlib import Path
from typing import Any

from mcp.types import Resource

from mcl.config import load_config, get_config_path


async def read_global_config() -> str:
    """Read global MCL configuration."""
    try:
        config_path = get_config_path()
        if not config_path.exists():
            return json.dumps({"scripts": {}, "vars": {}}, indent=2)
        
        return config_path.read_text()
    except Exception as e:
        return json.dumps({"error": str(e)})


async def read_local_config() -> str:
    """Read local MCL configuration."""
    try:
        local_path = Path("mcl.json")
        if not local_path.exists():
            return json.dumps({"error": "No local mcl.json found"})
        
        return local_path.read_text()
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_resource_definitions() -> list[Resource]:
    """Get all resource definitions."""
    return [
        Resource(
            uri="config://global",
            name="Global MCL Configuration",
            description="The global MCL configuration file from ~/.mcl/global-mcl.json",
            mimeType="application/json"
        ),
        Resource(
            uri="config://local",
            name="Local MCL Configuration",
            description="The local MCL configuration file (mcl.json in current directory)",
            mimeType="application/json"
        )
    ]
```

**Checklist:**
- [ ] Implement config readers
- [ ] Add resource definitions
- [ ] Handle missing files gracefully
- [ ] Return proper JSON
- [ ] Write unit tests

---

### M4.1: Implement Config Update Tool
**Estimated Time**: 4 hours

```python
async def update_config_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Update or add a script to local mcl.json.
    
    Args:
        arguments:
            - script_name: Name of the script
            - commands: String or list of commands
            - create_if_missing: Create mcl.json if it doesn't exist
    
    Returns:
        Success status and message
    """
    script_name = arguments.get("script_name")
    commands = arguments.get("commands")
    create_if_missing = arguments.get("create_if_missing", False)
    
    if not script_name or not commands:
        return {
            "success": False,
            "error": "script_name and commands are required"
        }
    
    try:
        from pathlib import Path
        import json
        
        config_path = Path("mcl.json")
        
        # Load or create config
        if config_path.exists():
            config = json.loads(config_path.read_text())
        elif create_if_missing:
            config = {"scripts": {}, "vars": {}}
        else:
            return {
                "success": False,
                "error": "mcl.json not found. Use create_if_missing=true to create it."
            }
        
        # Update script
        if "scripts" not in config:
            config["scripts"] = {}
        
        config["scripts"][script_name] = commands
        
        # Write atomically with backup
        backup_path = config_path.with_suffix(".json.bak")
        if config_path.exists():
            config_path.rename(backup_path)
        
        try:
            config_path.write_text(json.dumps(config, indent=2) + "\n")
            if backup_path.exists():
                backup_path.unlink()
            
            return {
                "success": True,
                "message": f"Script '{script_name}' updated in mcl.json",
                "path": str(config_path.absolute())
            }
        except Exception as e:
            # Restore backup on failure
            if backup_path.exists():
                backup_path.rename(config_path)
            raise e
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update config: {e}"
        }
```

**Checklist:**
- [ ] Implement config update logic
- [ ] Add atomic write with backup
- [ ] Validate JSON structure
- [ ] Handle nested script paths
- [ ] Write unit tests
- [ ] Test with various script formats

---

### M5.1: Integration Testing
**Estimated Time**: 4 hours

`tests/mcp/test_integration.py`:

```python
"""Integration tests for MCP server."""

import pytest
import json
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_server_initialize():
    """Test server initialization."""
    async with stdio_client(["mcl", "mcp", "start"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Server should respond with capabilities
            assert session.server_capabilities is not None


@pytest.mark.asyncio
async def test_list_tools():
    """Test listing available tools."""
    async with stdio_client(["mcl", "mcp", "start"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            tool_names = [t.name for t in tools]
            
            assert "mcl_list_scripts" in tool_names
            assert "mcl_run_script" in tool_names


@pytest.mark.asyncio
async def test_call_list_scripts_tool(tmp_path):
    """Test calling mcl_list_scripts tool."""
    # Create test config
    config_file = tmp_path / "mcl.json"
    config_file.write_text(json.dumps({
        "scripts": {
            "test": "echo hello"
        }
    }))
    
    # TODO: Set up client with cwd=tmp_path
    # Call tool and verify response
```

**Checklist:**
- [ ] Write initialization tests
- [ ] Write tool listing tests
- [ ] Write tool execution tests
- [ ] Write resource reading tests
- [ ] Test error scenarios
- [ ] Document test setup

---

## Dependencies & Prerequisites

### Python Packages
```toml
mcp >= 0.9.0
click >= 8.0
pytest-asyncio >= 0.21.0
```

### External Tools
- VS Code with Copilot (for E2E testing)
- Node.js (if using MCP inspector for debugging)

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MCP SDK API changes | High | Medium | Pin SDK version, monitor changelog |
| VS Code integration issues | High | Low | Test with multiple VS Code versions |
| Script execution security | High | Low | Validate all inputs, sandboxing |
| Performance with large configs | Medium | Medium | Implement caching, lazy loading |
| Protocol version mismatch | Medium | Low | Support multiple protocol versions |

---

## Timeline Estimate

- **M1**: 2 days (Foundation)
- **M2**: 3 days (Core Tools)
- **M3**: 2 days (Resources)
- **M4**: 3 days (Config Management)
- **M5**: 3 days (Testing)
- **M6**: 2 days (Documentation)

**Total**: ~3 weeks (15 working days)

---

## Success Metrics

1. **Functionality**: All 5 core tools working
2. **Reliability**: >95% uptime in testing
3. **Performance**: <100ms tool execution latency
4. **Coverage**: >90% test coverage
5. **Usability**: Successfully used by 3+ beta testers

---

## Next Steps

1. Review and approve this implementation plan
2. Set up project structure (M1.1)
3. Add dependencies (M1.2)
4. Begin M1 implementation
5. Daily progress updates in progress-tracker.md
