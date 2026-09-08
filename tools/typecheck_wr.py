#!/usr/bin/env python3
"""Minimal deterministic semantic checker for the current WeaR syntax.

This checker intentionally focuses on the semantic contract needed by `cetak`
and variable declarations. It is independent from compiler heuristics so that
regressions in name-based string detection are reported explicitly.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


STRING = "str"
INT = "int"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class Symbol:
    name: str
    type_name: str
    line: int


VAR_RE = re.compile(r"^\s*var\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
CETAK_RE = re.compile(r"^\s*cetak\s+(.+?)\s*$")
ASSIGN_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")


def expression_type(expr: str, symbols: dict[str, Symbol]) -> str:
    expr = expr.strip()
    if len(expr) >= 2 and expr[0] == '"' and expr[-1] == '"':
        return STRING
    if re.fullmatch(r"-?\d+", expr):
        return INT
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expr):
        symbol = symbols.get(expr)
        return symbol.type_name if symbol else UNKNOWN
    if "input()" in expr or "baca_file(" in expr or "char_at(" in expr:
        return STRING
    if "panjang(" in expr or "sama(" in expr or "is_" in expr:
        return INT
    if "+" in expr:
        parts = [part.strip() for part in expr.split("+")]
        types = [expression_type(part, symbols) for part in parts]
        if STRING in types:
            return STRING
        if all(item == INT for item in types):
            return INT
    return UNKNOWN


def check(path: Path) -> list[str]:
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
                symbols[name] = Symbol(name, value_type if value_type != UNKNOWN else old_type, symbols[name].line)
            continue

        match = CETAK_RE.match(raw)
        if match:
            expr = match.group(1)
            value_type = expression_type(expr, symbols)
            if value_type == UNKNOWN:
                errors.append(f"{path}:{lineno}: cannot determine type of cetak expression: {expr}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic WeaR source type checker")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    failed = False
    for path in args.files:
        errors = check(path)
        if errors:
            failed = True
            for error in errors:
                print(error, file=sys.stderr)
        else:
            print(f"PASS {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
