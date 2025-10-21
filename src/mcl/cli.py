"""Command-line interface for mcl."""

from __future__ import annotations

import logging
from typing import Any, cast

import click

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
@click.version_option()
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


def _configure_logging() -> None:
    """Initialize root logging once for the CLI session."""

    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
        )
