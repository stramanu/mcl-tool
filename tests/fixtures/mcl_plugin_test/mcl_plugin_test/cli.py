"""CLI entry point for mcl test plugin."""

from __future__ import annotations


def main(args: list[str]) -> int:
    """Test plugin entry point for mcl.

    Args:
        args: Command-line arguments after plugin name

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print(f"TEST_PLUGIN_CALLED with args: {args}")

    # Support --fail flag for testing error handling
    if "--fail" in args:
        return 1

    # Support --echo flag to echo remaining args
    if "--echo" in args and len(args) > 1:
        echo_args = [a for a in args if a != "--echo"]
        print(f"ECHO: {' '.join(echo_args)}")

    return 0
