"""MCP tool implementations for MCL."""

from typing import Any, Dict, List

from mcp.types import Tool

# Tool implementations will be added in M2


async def list_scripts_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """List all available MCL scripts (M2)."""
    raise NotImplementedError("Tool not yet implemented")


async def run_script_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCL script (M2)."""
    raise NotImplementedError("Tool not yet implemented")


async def get_script_info_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get detailed information about a script (M2)."""
    raise NotImplementedError("Tool not yet implemented")


async def update_config_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Update or add a script to local mcl.json (M4)."""
    raise NotImplementedError("Tool not yet implemented")


async def init_config_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize a new mcl.json in a directory (M4)."""
    raise NotImplementedError("Tool not yet implemented")


def get_tool_definitions() -> List[Tool]:
    """Get all tool definitions (will be populated in M2)."""
    return []
