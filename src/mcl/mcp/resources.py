"""MCP resource providers for MCL."""

from typing import List

from mcp.types import Resource

# Resource implementations will be added in M3


async def read_global_config() -> str:
    """Read global MCL configuration (M3)."""
    raise NotImplementedError("Resource not yet implemented")


async def read_local_config() -> str:
    """Read local MCL configuration (M3)."""
    raise NotImplementedError("Resource not yet implemented")


async def read_scripts_list() -> str:
    """Read list of all scripts (M3)."""
    raise NotImplementedError("Resource not yet implemented")


async def read_usage_docs() -> str:
    """Read MCL usage documentation (M3)."""
    raise NotImplementedError("Resource not yet implemented")


def get_resource_definitions() -> List[Resource]:
    """Get all resource definitions (will be populated in M3)."""
    return []
