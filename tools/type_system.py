#!/usr/bin/env python3
"""Canonical primitive type and symbol metadata definitions for WeaR Lang.

This module intentionally contains only semantic data definitions so the
symbol table, semantic analyzer, and compatibility frontend can share one
source of truth without creating import cycles.
"""

from __future__ import annotations

from dataclasses import dataclass

INT = "int"
STR = "str"
UNKNOWN = "unknown"
ERROR = "error"


@dataclass(frozen=True)
class FunctionSignature:
    return_type: str
    params: tuple[str, ...] = ()
    line: int = 0


@dataclass(frozen=True)
class Symbol:
    name: str
    type_name: str
    line: int
    scope: str = "global"
    internal_name: str = ""


__all__ = ["ERROR", "FunctionSignature", "INT", "STR", "Symbol", "UNKNOWN"]
