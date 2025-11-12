# MCP Server Architecture

**Feature**: MCP Server for MCL
**Version**: 1.0.0
**Last Updated**: 2025-11-12

---

## Overview

The MCL MCP Server is a standalone server that implements the Model Context Protocol to expose MCL functionality to AI assistants. It runs as a separate process and communicates with clients (like VS Code Copilot) via stdio transport.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code + GitHub Copilot                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           MCP Client (Copilot Extension)           │    │
│  └─────────────────┬──────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────┘
                     │ stdio (JSON-RPC)
                     │
┌────────────────────▼───────────────────────────────────────┐
│                  MCL MCP Server Process                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              MCP Protocol Handler                     │  │
│  │  - initialize / ping                                  │  │
│  │  - tools/list, tools/call                            │  │
│  │  - resources/list, resources/read                    │  │
│  │  - prompts/list, prompts/get                         │  │
│  └────────┬──────────────────────────┬──────────────────┘  │
│           │                          │                      │
│  ┌────────▼─────────┐    ┌──────────▼────────────┐        │
│  │  MCL Core Logic  │    │  Config Manager       │        │
│  │  - Script exec   │    │  - Load global/local  │        │
│  │  - Var subst     │    │  - Merge configs      │        │
│  │  - Dry-run       │    │  - JSON validation    │        │
│  └──────────────────┘    └───────────────────────┘        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                     │
                     │ Reads/Writes
                     │
         ┌───────────▼────────────┐
         │   File System          │
         │  ~/.mcl/global-mcl.json │
         │  ./mcl.json             │
         └─────────────────────────┘
```

---

## MCP Components

### 1. Tools (Callable Actions)

Tools are functions that the AI can invoke to perform actions.

#### `mcl_run_script`
Execute an MCL script with optional arguments.

**Input Schema:**
```json
{
  "script_name": "string",
  "args": ["string"],
  "dry_run": "boolean (optional)",
  "cwd": "string (optional)"
}
```

**Output:**
```json
{
  "success": true,
  "stdout": "...",
  "stderr": "...",
  "exit_code": 0
}
```

**Example:**
```
User: "Run the build script"
Copilot: <calls mcl_run_script with script_name="build">
```

---

#### `mcl_list_scripts`
List all available scripts from global and local configs.

**Input Schema:**
```json
{
  "include_global": "boolean (default: true)",
  "include_local": "boolean (default: true)"
}
```

**Output:**
```json
{
  "scripts": [
    {
      "name": "build",
      "source": "local",
      "path": "build.prod",
      "description": "Build production version"
    }
  ]
}
```

---

#### `mcl_get_script_info`
Get detailed information about a specific script.

**Input Schema:**
```json
{
  "script_name": "string"
}
```

**Output:**
```json
{
  "name": "build",
  "commands": ["go build -o bin/app"],
  "source": "local",
  "variables_used": ["$1"],
  "nested": false
}
```

---

#### `mcl_update_config`
Update or add a script to local mcl.json.

**Input Schema:**
```json
{
  "script_name": "string",
  "commands": "string | array",
  "create_if_missing": "boolean (default: false)"
}
```

**Output:**
```json
{
  "success": true,
  "message": "Script 'deploy' updated in mcl.json"
}
```

---

#### `mcl_init_config`
Initialize a new mcl.json in a directory.

**Input Schema:**
```json
{
  "directory": "string (optional, defaults to cwd)"
}
```

**Output:**
```json
{
  "success": true,
  "path": "/path/to/mcl.json"
}
```

---

### 2. Resources (Readable Content)

Resources provide context and documentation to the AI.

#### `config://global`
The global MCL configuration file content.

**URI:** `config://global`
**MIME Type:** `application/json`

**Content:**
```json
{
  "scripts": { ... },
  "vars": { ... }
}
```

---

#### `config://local`
The local MCL configuration file content (if exists).

**URI:** `config://local`
**MIME Type:** `application/json`

---

#### `scripts://all`
List of all available scripts with metadata.

**URI:** `scripts://all`
**MIME Type:** `application/json`

---

#### `docs://usage`
MCL usage documentation and examples.

**URI:** `docs://usage`
**MIME Type:** `text/markdown`

---

### 3. Prompts (Reusable Instructions)

Prompts provide pre-configured AI instructions for common tasks.

#### `create-script`
Help user create a new MCL script.

**Arguments:**
- `script_name`: Name for the new script
- `description`: What the script should do

**Prompt Template:**
```
Create an MCL script called "{script_name}" that {description}.

Guidelines:
1. Use appropriate shell commands
2. Support arguments with $1, $2, etc.
3. Add to local mcl.json
4. Include error handling
5. Consider using variables from mcl config
```

---

#### `optimize-script`
Suggest improvements for an existing script.

**Arguments:**
- `script_name`: Name of the script to optimize

---

#### `debug-script`
Help troubleshoot a failing script.

**Arguments:**
- `script_name`: Name of the script with issues
- `error_message`: The error encountered

---

## Implementation Details

### Server Entry Point

The MCP server will be implemented as a separate module:

```
src/
  mcl/
    __init__.py
    cli.py          # Existing CLI
    config.py
    executor.py
    mcp/
      __init__.py
      server.py     # MCP server implementation
      tools.py      # Tool implementations
      resources.py  # Resource providers
      prompts.py    # Prompt templates
```

### Server Startup

```python
# src/mcl/mcp/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server

async def main():
    server = Server("mcl-mcp-server")
    
    # Register tools
    @server.list_tools()
    async def list_tools():
        return [...]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "mcl_run_script":
            return await run_script_tool(arguments)
        # ...
    
    # Register resources
    @server.list_resources()
    async def list_resources():
        return [...]
    
    # Run server
    async with stdio_server() as (read, write):
        await server.run(read, write)
```

### CLI Integration

Add new command to mcl CLI:

```bash
# Start MCP server
mcl mcp start

# Test MCP server
mcl mcp test
```

---

## Configuration

### VS Code Integration

Users configure the server in VS Code settings:

```json
{
  "mcp.servers": {
    "mcl": {
      "command": "mcl",
      "args": ["mcp", "start"],
      "description": "MCL command runner"
    }
  }
}
```

### Environment Variables

- `MCL_CONFIG_DIR`: Override default ~/.mcl directory
- `MCL_MCP_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `MCL_MCP_TIMEOUT`: Execution timeout in seconds (default: 300)

---

## Security Considerations

1. **Script Execution**: Only execute scripts defined in mcl.json configs
2. **Path Traversal**: Validate all file paths to prevent directory traversal
3. **Command Injection**: Scripts are already defined; no user input in command construction
4. **Dry Run**: Default to dry-run mode for destructive operations
5. **Permissions**: Server runs with user permissions, no elevation

---

## Error Handling

### Tool Execution Errors

```json
{
  "error": {
    "code": "SCRIPT_NOT_FOUND",
    "message": "Script 'deploy' not found in any config",
    "details": {
      "available_scripts": ["build", "test"]
    }
  }
}
```

### Common Error Codes

- `SCRIPT_NOT_FOUND`: Requested script doesn't exist
- `CONFIG_INVALID`: mcl.json parsing error
- `EXECUTION_FAILED`: Script execution error
- `TIMEOUT`: Script exceeded timeout
- `PERMISSION_DENIED`: Insufficient permissions

---

## Performance Considerations

1. **Lazy Loading**: Load configs only when needed
2. **Caching**: Cache parsed configs with file watching for invalidation
3. **Async Execution**: Use asyncio for non-blocking script execution
4. **Resource Limits**: Set maximum execution time and output size

---

## Future Enhancements

### Phase 2 (Post-MVP)
- **Plugin Integration**: Expose MCL plugins as MCP tools
- **Script Templates**: MCP prompts for common script patterns
- **Execution History**: Resource showing recent executions
- **Script Validation**: Tool to validate script syntax before saving

### Phase 3
- **Remote Execution**: Execute scripts on remote machines via SSH
- **Environment Management**: Manage environment variables through MCP
- **Monitoring**: Real-time execution status through resources
- **Webhooks**: Trigger MCL scripts from external events

---

## Testing Strategy

1. **Unit Tests**: Test individual tool/resource implementations
2. **Integration Tests**: Test MCP protocol communication
3. **E2E Tests**: Test VS Code Copilot integration
4. **Manual Testing**: Real-world usage scenarios with Copilot

---

## Dependencies

### Required
- `mcp` >= 0.9.0 - MCP Python SDK
- `click` >= 8.0 - Already in mcl-tool

### Development
- `pytest-asyncio` - Async test support
- `mcp-client` - Testing MCP server locally

---

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK Docs](https://github.com/modelcontextprotocol/python-sdk)
- [VS Code MCP Guide](https://code.visualstudio.com/docs/copilot/copilot-mcp)
