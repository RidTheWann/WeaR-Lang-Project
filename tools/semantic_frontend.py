#!/usr/bin/env python3
"""Semantic compatibility frontend for the legacy Stage-0 compiler.

The historical compiler decides several C types from identifier spelling.
This frontend removes that dependency for user variables by deterministically
renaming declared variables to type-tagged internal identifiers before the
legacy backend sees the program. The transformation is source preserving for
strings/comments and does not rename keywords or function names.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from semantic_contract import INT, STR, UNKNOWN, expression_type

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
VAR_DECL = re.compile(r"^\s*var\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
ASSIGN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
FUNCTION = re.compile(r"^\s*fungsi\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)")

KEYWORDS = {
    "var", "cetak", "selama", "jika", "lainnya", "tapi_jika", "fungsi",
    "kembalikan", "benar", "salah", "impor",
}


@dataclass(frozen=True)
class Symbol:
    name: str
    type_name: str
    internal_name: str
    scope: str
    line: int


def _split_code_and_tail(line: str) -> tuple[str, str]:
    """Keep strings/comments untouched while exposing executable text."""
    in_string = False
    escaped = False
    for index, char in enumerate(line):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == '/' and index + 1 < len(line) and line[index + 1] == '/':
            return line[:index], line[index:]
    return line, ""


def _rename_identifiers(line: str, mapping: dict[str, str]) -> str:
    code, comment = _split_code_and_tail(line)
    out: list[str] = []
    pos = 0
    in_string = False
    escaped = False
    while pos < len(code):
        ch = code[pos]
        if ch == '"' and not escaped:
            in_string = not in_string
            out.append(ch)
            pos += 1
            continue
        if not in_string:
            match = IDENT.match(code, pos)
            if match:
                word = match.group(0)
                out.append(mapping.get(word, word))
                pos = match.end()
                continue
        out.append(ch)
        escaped = (ch == '\\' and not escaped)
        if ch != '\\':
            escaped = False
        pos += 1
    return ''.join(out) + comment


def _infer_type(expr: str, symbols: dict[str, Symbol]) -> str:
    return expression_type(expr, symbols)


def rewrite_source(text: str) -> str:
    symbols: dict[str, Symbol] = {}
    mapping: dict[str, str] = {}
    lines = text.splitlines(keepends=True)
    function_scope = "global"
    unique = 0

    for lineno, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("//"):
            continue

        fn = FUNCTION.match(raw)
        if fn:
            function_scope = fn.group(1)
            params = fn.group(2).strip()
            if params:
                for param in params.split(','):
                    param = param.strip()
                    if not param:
                        continue
                    parts = [part.strip() for part in param.split(':', 1)]
                    name = parts[0]
                    if not IDENT.fullmatch(name) or name in KEYWORDS:
                        continue
                    declared = parts[1] if len(parts) == 2 else ""
                    typ = STR if declared == "str" else INT if declared == "int" else UNKNOWN
                    unique += 1
                    internal = f"__wear_{'str' if typ == STR else 'int' if typ == INT else 'v'}_{function_scope}_{name}_{unique}"
                    symbols[name] = Symbol(name, typ, internal, function_scope, lineno)
                    mapping[name] = internal
            continue

        decl = VAR_DECL.match(raw)
        if decl:
            name, expr = decl.groups()
            typ = _infer_type(expr, symbols)
            unique += 1
            tag = "str" if typ == STR else "int" if typ == INT else "v"
            internal = f"__wear_{tag}_{function_scope}_{name}_{unique}"
            symbols[name] = Symbol(name, typ, internal, function_scope, lineno)
            mapping[name] = internal
            continue

        assignment = ASSIGN.match(raw)
        if assignment and not stripped.startswith(("jika", "tapi_jika", "selama", "fungsi")):
            name, expr = assignment.groups()
            symbol = symbols.get(name)
            if symbol:
                typ = _infer_type(expr, symbols)
                if typ != UNKNOWN:
                    symbols[name] = Symbol(name, typ, symbol.internal_name, symbol.scope, symbol.line)
            continue

    if not mapping:
        return text
    return ''.join(_rename_identifiers(line, mapping) for line in lines)


def rewrite_file(source: Path, destination: Path) -> None:
    destination.write_text(rewrite_source(source.read_text(encoding="utf-8")), encoding="utf-8")
