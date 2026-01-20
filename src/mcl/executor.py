"""Command execution utilities for mcl."""

from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
from typing import Any, List, Mapping, MutableMapping, Optional, Sequence, Match

import questionary

logger = logging.getLogger(__name__)

_ARG_PATTERN = re.compile(r"(?<!\$)\$(\d+)")
_OPTIONAL_PATTERN = re.compile(r"(?<!\$)\?\$(\d+)")
_VAR_PATTERN = re.compile(r"(?<!\$)\$(?P<name>[A-Za-z_][A-Za-z0-9_]*)")


def _format_path(script_name: str, fragments: Sequence[str]) -> str:
    """Return a dotted representation of the script path."""

    if not fragments:
        return script_name
    return f"{script_name}." + ".".join(fragments)


def _coerce_steps(payload: Any, script_name: str, path: Sequence[str]) -> List[str]:
    """Normalize payloads into a list of shell fragments."""

    if isinstance(payload, str):
        return [payload]

    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        steps = list(payload)
        if not all(isinstance(step, str) for step in steps):
            raise ValueError(
                f"Script '{_format_path(script_name, path)}' must contain only string steps"
            )
        return steps

    raise ValueError(
        f"Script '{_format_path(script_name, path)}' has unsupported payload type {type(payload)!r}"
    )


def _resolve_script_definition(
    raw_script: Any,
    all_args: Sequence[str],
    script_name: str,
) -> tuple[List[str], List[str]]:
    """Resolve nested script structures returning shell fragments and remaining args."""

    current = raw_script
    remaining = list(all_args)
    path: List[str] = []

    while isinstance(current, Mapping):
        if not remaining:
            available_options = sorted(str(key) for key in current.keys())

            # If not in a TTY (e.g., piped input/output), fallback to error message
            if not sys.stdin.isatty() or not sys.stdout.isatty():
                available = ", ".join(available_options)
                raise ValueError(
                    f"Script '{_format_path(script_name, path)}' requires a subcommand. "
                    f"Available options: {available}"
                )

            # Interactive menu selection
            try:
                choice = questionary.select(
                    f"Select a subcommand for '{_format_path(script_name, path)}':",
                    choices=available_options,
                ).ask()

                if choice is None:  # User cancelled (Ctrl+C)
                    raise ValueError("Command cancelled by user")

                remaining.append(choice)
            except KeyboardInterrupt:
                raise ValueError("Command cancelled by user") from None

        key = remaining.pop(0)
        if key not in current:
            available = ", ".join(sorted(str(opt) for opt in current.keys()))
            raise ValueError(
                f"Script '{_format_path(script_name, path)}' has no subcommand '{key}'. "
                f"Available options: {available}"
            )

        path.append(key)
        current = current[key]

    steps = _coerce_steps(current, script_name, path)
    return steps, remaining


def render_script(
    script_steps: Sequence[str],
    args: Sequence[str],
    vars_dict: Mapping[str, Any],
) -> List[str]:
    """Return the list of executable command strings after substitution.

    Comment-only or empty steps are dropped.
    Supports double-dollar escape syntax: $$ becomes literal $.
    """

    rendered: List[str] = []
    for raw_step in script_steps:
        stripped = raw_step.lstrip()
        if not stripped or stripped.startswith("#"):
            continue

        step = _replace_optional(raw_step, args)
        step = _replace_positional(step, args)
        step = _replace_vars(step, vars_dict)
        step = _unescape_dollars(step)
        final_step = step.strip()
        if final_step:
            rendered.append(final_step)

    return rendered


def _unescape_dollars(command: str) -> str:
    """Convert double-dollar escape sequences back to single dollar signs.

    This is the final step after all substitutions, converting $$ to $.
    """
    return command.replace("$$", "$")


def execute(
    config: Mapping[str, Any],
    cmd_name: str,
    args: Sequence[str],
    dry_run: bool,
    share_vars: bool,
) -> None:
    """Execute the script named ``cmd_name`` using ``config`` and ``args``.

    Raises ``ValueError`` for missing scripts or substitution failures.
    """

    scripts = config.get("scripts")
    if not isinstance(scripts, MutableMapping):
        raise ValueError("Configuration must contain a 'scripts' object")

    raw_script = scripts.get(cmd_name)
    if raw_script is None:
        # Check if the script exists as a nested script under "run" key.
        # This handles the case where users have scripts like:
        #   {"scripts": {"run": {"service": "echo example"}}}
        # and invoke them as "mcl run service", but cli intercepts "run" as command.
        run_scripts = scripts.get("run")
        if isinstance(run_scripts, Mapping) and cmd_name in run_scripts:
            raw_script = run_scripts
            args = [cmd_name] + list(args)
            cmd_name = "run"
        else:
            raise ValueError(f"Script '{cmd_name}' is not defined")

    steps_list, call_args = _resolve_script_definition(raw_script, args, cmd_name)

    vars_dict = config.get("vars", {})
    if not isinstance(vars_dict, Mapping):
        raise ValueError("Configuration key 'vars' must be an object")

    steps = render_script(steps_list, call_args, vars_dict)
    if not steps:
        logger.info("No executable steps for script '%s'", cmd_name)
        return

    env: Optional[dict[str, str]] = None
    if share_vars:
        env = os.environ.copy()
        for key, value in vars_dict.items():
            env[str(key)] = str(value)
        for index, arg in enumerate(call_args, start=1):
            env[f"MCL_ARG_{index}"] = arg

    for step in steps:
        logger.info("Executing step: %s", step)
        if dry_run:
            logger.info("Dry-run enabled; skipping execution")
            continue

        try:
            # Always use shell=True to support environment variables and complex shell syntax.
            # When share_vars is True, pass the environment dict; otherwise use the current environment.
            subprocess.run(step, shell=True, check=True, env=env)
        except subprocess.CalledProcessError as exc:  # pragma: no cover - safety net
            raise ValueError(f"Command failed with exit code {exc.returncode}") from exc


def _replace_optional(command: str, args: Sequence[str]) -> str:
    """Replace optional positional placeholders like `?$1`."""

    def repl(match: Match[str]) -> str:
        index = int(match.group(1)) - 1
        if 0 <= index < len(args):
            return args[index]
        return ""

    return _OPTIONAL_PATTERN.sub(repl, command)


def _replace_positional(command: str, args: Sequence[str]) -> str:
    """Replace required positional placeholders like `$1`."""

    def repl(match: Match[str]) -> str:
        index = int(match.group(1)) - 1
        if index >= len(args):
            raise ValueError(f"Missing positional argument ${index + 1}")
        return args[index]

    return _ARG_PATTERN.sub(repl, command)


def _replace_vars(command: str, vars_dict: Mapping[str, Any]) -> str:
    """Replace variable placeholders using config vars."""

    def repl(match: Match[str]) -> str:
        name = match.group("name")
        if name.isdigit():
            return match.group(0)
        if name not in vars_dict:
            raise ValueError(f"Unknown variable '${name}'")
        return str(vars_dict[name])

    return _VAR_PATTERN.sub(repl, command)
