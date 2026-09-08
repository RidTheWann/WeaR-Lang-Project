#!/usr/bin/env python3
"""Shared deterministic semantic contract for WeaR Lang tooling.

This module intentionally stays independent from compiler.c. It defines the
small primitive type/signature vocabulary used by the CLI frontend so future
compiler stages have one canonical contract instead of duplicating ad-hoc
name heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

INT = "int"
STR = "str"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class FunctionSignature:
    return_type: str
    params: tuple[str, ...] = ()


BUILTINS: dict[str, FunctionSignature] = {
    "panjang": FunctionSignature(INT, (STR,)),
    "sama": FunctionSignature(INT, (STR, STR)),
    "is_quote": FunctionSignature(INT, (STR,)),
    "is_newline": FunctionSignature(INT, (STR,)),
    "is_digit": FunctionSignature(INT, (STR,)),
    "is_letter": FunctionSignature(INT, (STR,)),
    "is_space": FunctionSignature(INT, (STR,)),
    "baca_file": FunctionSignature(STR, (STR,)),
    "char_at": FunctionSignature(STR, (STR, INT)),
    "quote_char": FunctionSignature(STR),
    "newline_char": FunctionSignature(STR),
    "input": FunctionSignature(STR),
}

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
INTEGER_RE = re.compile(r"^-?[0-9]+$")


def is_identifier(value: str) -> bool:
    return bool(IDENTIFIER_RE.match(value))


def literal_type(expr: str) -> str:
    value = expr.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return STR
    if INTEGER_RE.match(value):
        return INT
    return UNKNOWN


def builtin_signature(name: str) -> FunctionSignature | None:
    return BUILTINS.get(name)
