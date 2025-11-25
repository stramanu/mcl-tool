"""Tests for plugin generator (mcl plugin new)."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from mcl.cli import cli
from mcl.templates import generate_plugin, get_template_list, TEMPLATES


def test_get_template_list() -> None:
    """Test retrieving available templates."""
    templates = get_template_list()

    assert isinstance(templates, dict)
    assert "simple" in templates
    assert "click" in templates
    assert "api-client" in templates

    assert templates["simple"]["name"] == "Simple Plugin"
    assert templates["click"]["name"] == "Click-based Plugin"


def test_generate_simple_plugin(tmp_path: Path) -> None:
    """Test generating a simple plugin."""
    plugin_name = "test"
    description = "A test plugin"
    output_dir = tmp_path / "mcl-plugin-test"

    generate_plugin(plugin_name, description, "simple", output_dir)

    # Check structure
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "README.md").exists()
    assert (output_dir / ".gitignore").exists()
    assert (output_dir / "src" / "mcl_plugin_test" / "__init__.py").exists()
    assert (output_dir / "src" / "mcl_plugin_test" / "cli.py").exists()
    assert (output_dir / "tests" / "test_test.py").exists()

    # Check content
    pyproject = (output_dir / "pyproject.toml").read_text()
    assert "mcl-plugin-test" in pyproject
    assert description in pyproject
    assert 'test = "mcl_plugin_test:main"' in pyproject

    cli_py = (output_dir / "src" / "mcl_plugin_test" / "cli.py").read_text()
    assert "def main(args: List[str]) -> int:" in cli_py
    assert "MCL_DRY_RUN" in cli_py


def test_generate_click_plugin(tmp_path: Path) -> None:
    """Test generating a Click-based plugin."""
    plugin_name = "docker"
    description = "Docker utilities"
    output_dir = tmp_path / "mcl-plugin-docker"

    generate_plugin(plugin_name, description, "click", output_dir)

    # Check Click dependency
    pyproject = (output_dir / "pyproject.toml").read_text()
    assert "click>=8.0" in pyproject

    # Check Click usage in code
    cli_py = (output_dir / "src" / "mcl_plugin_docker" / "cli.py").read_text()
    assert "import click" in cli_py
    assert "@click.group()" in cli_py
    assert "@cli.command()" in cli_py


def test_generate_api_client_plugin(tmp_path: Path) -> None:
    """Test generating an API client plugin."""
    plugin_name = "github"
    description = "GitHub API client"
    output_dir = tmp_path / "mcl-plugin-github"

    generate_plugin(plugin_name, description, "api-client", output_dir)

    # Check requests dependency
    pyproject = (output_dir / "pyproject.toml").read_text()
    assert "requests>=2.28" in pyproject

    # Check API client code
    cli_py = (output_dir / "src" / "mcl_plugin_github" / "cli.py").read_text()
    assert "import requests" in cli_py
    assert "class APIClient" in cli_py
    assert "API_KEY" in cli_py


def test_generate_plugin_invalid_template(tmp_path: Path) -> None:
    """Test error handling for invalid template."""
    with pytest.raises(ValueError, match="Unknown template"):
        generate_plugin("test", "Test", "invalid", tmp_path)


def test_plugin_new_command_help() -> None:
    """Test 'mcl plugin new --help' command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["plugin", "new", "--help"])

    assert result.exit_code == 0
    assert "Create a new plugin from template" in result.output
    assert "--name" in result.output
    assert "--description" in result.output
    assert "--template" in result.output
    assert "simple" in result.output
    assert "click" in result.output
    assert "api-client" in result.output


def test_plugin_new_command_non_interactive(tmp_path: Path) -> None:
    """Test 'mcl plugin new' with all options provided."""
    runner = CliRunner()
    output_dir = tmp_path / "test-output"

    result = runner.invoke(
        cli,
        [
            "plugin",
            "new",
            "--name",
            "hello",
            "--description",
            "A hello plugin",
            "--template",
            "simple",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Plugin created successfully" in result.output
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "src" / "mcl_plugin_hello" / "cli.py").exists()


def test_plugin_new_command_directory_exists(tmp_path: Path) -> None:
    """Test error when output directory already exists."""
    runner = CliRunner()
    output_dir = tmp_path / "existing"
    output_dir.mkdir()

    # Create a file to ensure directory is not empty
    (output_dir / "existing.txt").write_text("test")

    result = runner.invoke(
        cli,
        [
            "plugin",
            "new",
            "--name",
            "test",
            "--description",
            "Test",
            "--template",
            "simple",
            "--output",
            str(output_dir),
        ],
        input="n\n",  # Answer "no" to overwrite prompt
    )

    assert result.exit_code == 1
    assert "already exists" in result.output


def test_plugin_new_command_overwrite_confirm(tmp_path: Path) -> None:
    """Test overwriting existing directory when user confirms."""
    runner = CliRunner()
    output_dir = tmp_path / "existing"
    output_dir.mkdir()

    result = runner.invoke(
        cli,
        [
            "plugin",
            "new",
            "--name",
            "test",
            "--description",
            "Test",
            "--template",
            "simple",
            "--output",
            str(output_dir),
        ],
        input="y\n",  # Answer "yes" to overwrite prompt
    )

    assert result.exit_code == 0
    assert "Plugin created successfully" in result.output
    assert (output_dir / "pyproject.toml").exists()


def test_plugin_new_empty_name() -> None:
    """Test error when plugin name is empty."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "plugin",
            "new",
            "--name",
            "",
            "--description",
            "Test",
            "--template",
            "simple",
        ],
    )

    assert result.exit_code == 1
    assert "Plugin name cannot be empty" in result.output


def test_generated_plugin_structure_simple(tmp_path: Path) -> None:
    """Test that generated simple plugin has correct structure."""
    output_dir = tmp_path / "mcl-plugin-mytest"
    generate_plugin("mytest", "My test plugin", "simple", output_dir)

    # Verify all expected files exist
    expected_files = [
        "pyproject.toml",
        "README.md",
        ".gitignore",
        "src/mcl_plugin_mytest/__init__.py",
        "src/mcl_plugin_mytest/cli.py",
        "tests/test_mytest.py",
    ]

    for file_path in expected_files:
        full_path = output_dir / file_path
        assert full_path.exists(), f"Missing file: {file_path}"

    # Verify pyproject.toml has correct entry point
    pyproject_content = (output_dir / "pyproject.toml").read_text()
    assert '[project.entry-points."mcl.plugins"]' in pyproject_content
    assert 'mytest = "mcl_plugin_mytest:main"' in pyproject_content

    # Verify __init__.py exports main
    init_content = (
        output_dir / "src" / "mcl_plugin_mytest" / "__init__.py"
    ).read_text()
    assert "from .cli import main" in init_content
    assert '__all__ = ["main"]' in init_content
