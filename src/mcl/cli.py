"""Command-line interface for mcl."""

from __future__ import annotations

import logging
import sys
from typing import Any, cast

import click
import questionary

from .commands import extract_script_maps, list_script_paths
from .config import edit_global, init_local as init_local_config, load_config
from .executor import execute


class ScriptGroup(click.Group):
    """Custom Click group that falls back to the `run` command."""

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command

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

        # Show interactive menu or script list
        try:
            config = load_config(local=True)
            global_scripts, local_scripts = extract_script_maps(config)
            local_paths = list_script_paths(local_scripts) if local_scripts else []
            global_paths_all = (
                list_script_paths(global_scripts) if global_scripts else []
            )
            local_set = set(local_paths)
            global_paths = [path for path in global_paths_all if path not in local_set]
            all_paths = local_paths + global_paths

            if not all_paths:
                click.echo("⚡ mcl - My Command Line\n")
                click.echo("No scripts configured yet. Try `mcl init`.")
                click.echo("Use `mcl --help` for detailed usage information.")
                return

            # Interactive menu in TTY, text list otherwise
            if sys.stdin.isatty() and sys.stdout.isatty():
                # Build choices with visual separation
                choices: list[Any] = []
                if local_paths:
                    choices.append(questionary.Separator("=== Local Scripts ==="))
                    choices.extend(local_paths)
                if global_paths:
                    choices.append(questionary.Separator("=== Global Scripts ==="))
                    choices.extend(global_paths)

                try:
                    selected = questionary.select(
                        "⚡ Select a script to run:",
                        choices=choices,
                    ).ask()

                    if selected is None:  # User cancelled
                        return

                    # Execute the selected script
                    # Split space-separated path into script name and args
                    parts = selected.split()
                    if parts:
                        script_name = parts[0]
                        script_args = tuple(parts[1:])
                        ctx.invoke(run, cmd_name=script_name, args=script_args)
                except KeyboardInterrupt:
                    return
            else:
                # Non-TTY: show text list
                click.echo("⚡ mcl - My Command Line\n")
                if local_paths:
                    click.echo("Local scripts:")
                    for path in local_paths:
                        click.echo(f"  • {path}")
                if global_paths:
                    if local_paths:
                        click.echo("")
                    click.echo("Global scripts:")
                    for path in global_paths:
                        click.echo(f"  • {path}")
                click.echo("\nRun a script: mcl <script> [args...]")
                click.echo("Use `mcl --help` for detailed usage information.")
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


def _configure_logging() -> None:
    """Initialize root logging once for the CLI session."""

    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
        )
