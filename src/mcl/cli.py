"""Command-line interface for mcl."""

from __future__ import annotations

import logging
import os
from typing import Any, cast

import click

from .commands import extract_script_maps, list_script_paths
from .config import edit_global, init_local as init_local_config, load_config
from .executor import execute
from .plugins import discover_plugins, list_plugins


class ScriptGroup(click.Group):
    """Custom Click group with plugin support that falls back to the `run` command."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._plugins = discover_plugins()
        if self._plugins:
            logger = logging.getLogger(__name__)
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

        assert run_command is not None

        class ScriptAliasCommand(click.Command):
            def __init__(self, name: str) -> None:
                super().__init__(name)
                self.allow_extra_args = True
                self.ignore_unknown_options = True

            def invoke(self_alias, alias_ctx: click.Context) -> Any:
                remaining: list[str] = list(alias_ctx.args)
                alias_ctx.args = []
                return alias_ctx.invoke(
                    cast(click.Command, run_command),
                    cmd_name=cmd_name,
                    args=tuple(remaining),
                )

        return ScriptAliasCommand(name=cmd_name)

    def _create_plugin_command(self, name: str) -> click.Command:
        """Create a Click command wrapper for a plugin.

        Args:
            name: The plugin name

        Returns:
            A Click command that invokes the plugin entry point
        """
        plugin_fn = self._plugins[name]
        logger = logging.getLogger(__name__)

        class PluginCommand(click.Command):
            def __init__(self) -> None:
                super().__init__(name)
                self.allow_extra_args = True
                self.ignore_unknown_options = True

            def invoke(self, ctx: click.Context) -> Any:
                # Pass remaining args to plugin
                args = list(ctx.args)

                # Pass mcl context via environment variables
                if ctx.obj:
                    if ctx.obj.get("dry_run"):
                        os.environ["MCL_DRY_RUN"] = "1"
                    if ctx.obj.get("share_vars"):
                        os.environ["MCL_SHARE_VARS"] = "1"

                try:
                    exit_code = plugin_fn(args)
                    if exit_code != 0:
                        logger.error(f"Plugin '{name}' exited with code {exit_code}")
                        raise click.Abort()
                except Exception as e:
                    logger.error(f"Plugin '{name}' failed: {e}")
                    raise click.Abort()

        return PluginCommand()


@click.group(
    cls=ScriptGroup,
    invoke_without_command=True,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.version_option(package_name="mcl-tool")  # type: ignore[call-arg]
@click.option("--dry-run", is_flag=True, help="Print commands without executing them.")
@click.option(
    "--share-vars",
    is_flag=True,
    help="Expose config vars and args to subprocesses via the environment.",
)
@click.pass_context
def cli(ctx: click.Context, dry_run: bool, share_vars: bool) -> None:
    """Entry point for the mcl CLI."""

    _configure_logging()

    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["share_vars"] = share_vars

    if ctx.invoked_subcommand is None:
        if ctx.args:
            script_name = ctx.args[0]
            script_args = tuple(ctx.args[1:])
            ctx.args = []
            ctx.invoke(run, cmd_name=script_name, args=script_args)
            return

        click.echo(ctx.get_help())
        click.echo(
            "\nTip: use `mcl run <script>` or shorthand `mcl <script> [args...]`.\n"
        )
        try:
            config = load_config(local=True)
            global_scripts, local_scripts = extract_script_maps(config)
            local_paths = list_script_paths(local_scripts) if local_scripts else []
            global_paths_all = (
                list_script_paths(global_scripts) if global_scripts else []
            )
            local_set = set(local_paths)
            global_paths = [path for path in global_paths_all if path not in local_set]

            if local_paths:
                click.echo("Local scripts (override global when duplicated):")
                for path in local_paths:
                    click.echo(f"  • {path}")

            if global_paths:
                if local_paths:
                    click.echo("")
                click.echo("Global scripts:")
                for path in global_paths:
                    click.echo(f"  • {path}")

            if not local_paths and not global_paths:
                click.echo("No scripts configured yet. Try `mcl init`.\n")
        except ValueError as exc:
            click.echo(f"Warning: unable to load config ({exc})", err=True)


@cli.command(name="init")
@click.pass_context
def init_local(ctx: click.Context) -> None:
    """Create an empty `mcl.json` in the current directory."""

    init_local_config()
    click.secho("Local config ready at mcl.json", fg="green")


@cli.command(name="edit")
@click.pass_context
def edit_conf(ctx: click.Context) -> None:
    """Open the global configuration file in the configured editor."""

    try:
        edit_global()
    except ValueError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        raise click.Abort() from exc

    click.secho("Opened ~/.mcl/global-mcl.json", fg="green")


@cli.command()
@click.argument("cmd_name", metavar="SCRIPT")
@click.argument("args", metavar="[ARGS...]", nargs=-1)
@click.pass_context
def run(ctx: click.Context, cmd_name: str, args: tuple[str, ...]) -> None:
    """Execute the configured script named ``cmd_name`` with optional arguments."""

    dry_run = bool(ctx.obj.get("dry_run"))
    share_vars = bool(ctx.obj.get("share_vars"))

    try:
        config = load_config(local=True)
        execute(config, cmd_name, list(args), dry_run=dry_run, share_vars=share_vars)
        click.secho(f"Command '{cmd_name}' completed", fg="green")
    except ValueError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        raise click.Abort() from exc


@cli.group()
def plugin() -> None:
    """Manage mcl plugins."""
    pass


@plugin.command(name="list")
def plugin_list() -> None:
    """List all installed mcl plugins."""
    plugins = list_plugins()

    if not plugins:
        click.echo("No plugins installed.")
        click.echo("\nInstall plugins with: pip install mcl-plugin-<name>")
        click.echo("Example: pip install mcl-plugin-docker")
        return

    click.echo("Installed plugins:")
    for name, version in plugins:
        click.echo(f"  • {name} ({version})")

    click.echo(
        f"\nTotal: {len(plugins)} plugin{'s' if len(plugins) != 1 else ''} installed"
    )
    click.echo("\nUse 'mcl plugin info <name>' for details about a plugin.")


@plugin.command(name="info")
@click.argument("name")
def plugin_info(name: str) -> None:
    """Show detailed information about a plugin."""
    import importlib.metadata

    try:
        eps = importlib.metadata.entry_points()

        # Python 3.10+ uses select(), 3.8-3.9 uses dict-like access
        if hasattr(eps, "select"):
            group = eps.select(group="mcl.plugins")
        else:
            group = eps.get("mcl.plugins", [])  # type: ignore[arg-type]

        for ep in group:
            if ep.name == name:
                click.secho(f"Plugin: {name}", fg="cyan", bold=True)
                click.echo(f"Entry Point: {ep.value}")

                # Try to get package metadata
                try:
                    pkg_name = ep.value.split(":")[0].split(".")[0]
                    dist = importlib.metadata.distribution(pkg_name)
                    click.echo(f"Package: {dist.metadata['Name']}")
                    click.echo(f"Version: {dist.version}")

                    if "Summary" in dist.metadata:
                        click.echo(f"Description: {dist.metadata['Summary']}")
                    if "Home-page" in dist.metadata:
                        click.echo(f"Homepage: {dist.metadata['Home-page']}")
                    if "Author" in dist.metadata:
                        click.echo(f"Author: {dist.metadata['Author']}")
                    if "License" in dist.metadata:
                        click.echo(f"License: {dist.metadata['License']}")
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Could not load package metadata: {e}")

                return

        # Plugin not found
        click.secho(f"Plugin '{name}' not found.", fg="red", err=True)
        click.echo("\nAvailable plugins:")
        plugins = list_plugins()
        if plugins:
            for plugin_name, _ in plugins:
                click.echo(f"  • {plugin_name}")
        else:
            click.echo("  (none)")
        raise click.Abort()

    except click.Abort:
        raise
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        raise click.Abort() from e


@plugin.command(name="new")
@click.option(
    "--name",
    "-n",
    prompt="Plugin name (e.g., 'hello')",
    help="Name of the plugin (used as mcl subcommand)",
)
@click.option(
    "--description",
    "-d",
    prompt="Description",
    default="A custom MCL plugin",
    help="Short description of the plugin",
)
@click.option(
    "--template",
    "-t",
    type=click.Choice(["simple", "click", "api-client"], case_sensitive=False),
    prompt="Template type",
    default="simple",
    help="Plugin template to use",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output directory (default: mcl-plugin-<name>)",
)
def plugin_new(name: str, description: str, template: str, output: str | None) -> None:
    """Create a new plugin from template (interactive)."""
    from pathlib import Path
    from mcl.templates import generate_plugin, get_template_list

    # Validate and normalize plugin name
    plugin_name = name.lower().strip()
    if not plugin_name:
        click.secho("Error: Plugin name cannot be empty", fg="red", err=True)
        raise click.Abort()

    # Determine output directory
    if output:
        output_dir = Path(output)
    else:
        output_dir = Path(f"mcl-plugin-{plugin_name}")

    # Check if directory exists
    if output_dir.exists():
        if not click.confirm(
            f"Directory '{output_dir}' already exists. Overwrite?", default=False
        ):
            click.echo("Cancelled.")
            raise click.Abort()

    # Show template info
    templates = get_template_list()
    if template in templates:
        template_info = templates[template]
        click.echo(f"\n📦 Creating plugin with template: {template_info['name']}")
        click.echo(f"   {template_info['description']}")

    # Generate plugin
    try:
        click.echo(f"\n🔧 Generating plugin '{plugin_name}'...")
        generate_plugin(plugin_name, description, template, output_dir)

        click.secho(f"\n✅ Plugin created successfully!", fg="green", bold=True)
        click.echo(f"\n📁 Location: {output_dir.absolute()}")

        # Show next steps
        click.echo("\n📝 Next steps:")
        click.echo(f"   1. cd {output_dir}")
        click.echo("   2. pip install -e '.[dev]'")
        click.echo("   3. Edit src/mcl_plugin_*/cli.py to implement your logic")
        click.echo("   4. pytest")
        click.echo(f"   5. mcl {plugin_name}")

        click.echo("\n📚 Documentation:")
        click.echo("   docs/features/01.plugin-system/plugin-development-guide.md")

    except Exception as e:
        click.secho(f"\n❌ Error creating plugin: {e}", fg="red", err=True)
        raise click.Abort() from e


def _configure_logging() -> None:
    """Initialize root logging once for the CLI session."""

    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
        )
