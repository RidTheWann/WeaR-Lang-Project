#!/usr/bin/env python3
"""Canonical deterministic semantic contract for the current WeaR syntax.

This module is the frontend semantic layer used before the legacy Stage-0
compiler. It deliberately tracks declared types rather than variable names.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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
VAR_RE = re.compile(r"^\s*var\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
ASSIGN_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
CETAK_RE = re.compile(r"^\s*cetak\s+(.+?)\s*$")


@dataclass(frozen=True)
class Symbol:
    name: str
    type_name: str
    line: int


def is_identifier(value: str) -> bool:
    return bool(IDENTIFIER_RE.fullmatch(value.strip()))


def literal_type(expr: str) -> str:
    value = expr.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return STR
    if INTEGER_RE.fullmatch(value):
        return INT
    return UNKNOWN


def builtin_signature(name: str) -> FunctionSignature | None:
    return BUILTINS.get(name)


def expression_type(expr: str, symbols: dict[str, Symbol]) -> str:
    value = expr.strip()
    direct = literal_type(value)
    if direct != UNKNOWN:
        return direct

    if is_identifier(value):
        symbol = symbols.get(value)
        if symbol:
            return symbol.type_name
        builtin = builtin_signature(value)
        return builtin.return_type if builtin else UNKNOWN

    call = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(", value)
    if call:
        builtin = builtin_signature(call.group(1))
        if builtin:
            return builtin.return_type

    if "+" in value:
        parts = [part.strip() for part in value.split("+")]
        types = [expression_type(part, symbols) for part in parts]
        if STR in types:
            return STR
        if types and all(item == INT for item in types):
            return INT

    if any(op in value for op in ("==", "<=", ">=", "<", ">")):
        return INT

    return UNKNOWN


def check_source(path: Path) -> list[str]:
    symbols: dict[str, Symbol] = {}
    errors: list[str] = []

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue

        match = VAR_RE.match(raw)
        if match:
            name, expr = match.groups()
            value_type = expression_type(expr, symbols)
            if value_type == UNKNOWN:
                errors.append(f"{path}:{lineno}: cannot determine type of initializer for '{name}'")
            symbols[name] = Symbol(name, value_type, lineno)
            continue

        match = ASSIGN_RE.match(raw)
        if match and not line.startswith(("jika", "lainnya", "selama", "fungsi")):
            name, expr = match.groups()
            if name in symbols:
                value_type = expression_type(expr, symbols)
                old_type = symbols[name].type_name
                if value_type != UNKNOWN and old_type != UNKNOWN and value_type != old_type:
                    errors.append(
                        f"{path}:{lineno}: assignment type mismatch for '{name}': "
                        f"declared {old_type}, assigned {value_type}"
                    )
            continue

        match = CETAK_RE.match(raw)
        if match:
            expr = match.group(1)
            value_type = expression_type(expr, symbols)
            if value_type == UNKNOWN:
                errors.append(f"{path}:{lineno}: cannot determine type of cetak expression: {expr}")

    return errors
