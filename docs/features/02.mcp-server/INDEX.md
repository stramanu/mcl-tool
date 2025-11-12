# MCP Server Feature - Documentation Index

**Feature**: Model Context Protocol (MCP) Server for MCL
**Branch**: `feature/mcp-server`
**Start Date**: 2025-11-12
**Status**: 🟡 PLANNING

---

## Overview

This feature adds a Model Context Protocol (MCP) server to expose MCL functionality to AI assistants like GitHub Copilot. The MCP server will allow Copilot to:

- Discover and list available MCL scripts from global and local configs
- Execute MCL scripts directly through MCP tools
- Read and modify `mcl.json` configuration files
- Provide script documentation and examples as resources

---

## Documentation Files

### Core Documentation
- **[architecture.md](architecture.md)** - System design, MCP tools/resources/prompts, integration architecture
- **[implementation-plan.md](implementation-plan.md)** - Detailed milestones, tasks, and technical specifications
- **[progress-tracker.md](progress-tracker.md)** - Real-time implementation status and blockers

### Reference
- **[mcp-protocol.md](mcp-protocol.md)** - MCP protocol reference and best practices
- **[usage-examples.md](usage-examples.md)** - Usage examples for end users and Copilot integration

---

## Key Benefits

1. **Seamless Integration**: Use MCL scripts directly from Copilot chat
2. **Discovery**: AI can discover available scripts and their usage
3. **Automation**: Execute complex workflows through conversational interface
4. **Context-Aware**: Server has access to both global and local MCL configs
5. **Extensibility**: Future plugin system can expose additional MCP tools

---

## Quick Links

- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [VS Code MCP Integration](https://code.visualstudio.com/docs/copilot/copilot-mcp)

---

## Related Features

- **01.plugin-system**: Future integration to expose plugins as MCP tools
