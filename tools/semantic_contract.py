#!/usr/bin/env python3
"""Backward-compatible semantic API facade.

The canonical implementation now lives in :mod:`semantic_engine`; this
module remains as a stable import path for existing tooling.
"""

from semantic_engine import *

__all__ = [
    "BUILTINS",
    "Diagnostic",
    "ERROR",
    "FunctionSignature",
    "INT",
    "STR",
    "Symbol",
    "UNKNOWN",
    "check_source",
    "expression_type",
]
