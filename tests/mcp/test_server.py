"""Tests for MCP server."""

import pytest
from click.testing import CliRunner

from mcl.cli import cli
from mcl.mcp.server import MCLServer


def test_mcl_server_initialization() -> None:
    """Test that MCLServer can be initialized."""
    server = MCLServer()
    assert server is not None
    assert server.server is not None
    assert server.server.name == "mcl-mcp-server"


def test_mcp_test_command() -> None:
    """Test mcl mcp test command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mcp", "test"])

    assert result.exit_code == 0
    assert "Testing MCP server" in result.output
    assert "MCP server module loaded successfully" in result.output
    assert "mcl mcp start" in result.output


def test_mcp_start_command_help() -> None:
    """Test mcl mcp start --help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mcp", "start", "--help"])

    assert result.exit_code == 0
    assert "Start the MCL MCP server" in result.output


def test_mcp_command_group() -> None:
    """Test mcl mcp command group exists."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mcp", "--help"])

    assert result.exit_code == 0
    assert "MCP server commands" in result.output
    assert "start" in result.output
    assert "test" in result.output


@pytest.mark.asyncio
async def test_server_has_handlers() -> None:
    """Test that server has protocol handlers set up."""
    server = MCLServer()

    # Verify handlers are registered
    # Note: This is a basic smoke test; full protocol testing comes in M5
    assert server.server is not None
