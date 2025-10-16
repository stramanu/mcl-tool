"""mcl - My Command Line: customizable CLI orchestration tool.

This package exposes the Click entry point and version metadata.
"""

from __future__ import annotations

__all__ = ["__version__", "__author__", "cli"]

__version__ = "0.1.0"
__author__ = "Your Name"

from .cli import cli  # re-export for `python -m mcl`
