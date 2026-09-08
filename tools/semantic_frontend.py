#!/usr/bin/env python3
"""Semantic compatibility frontend for the legacy Stage-0 compiler.

The historical compiler decides several C types from identifier spelling.
This frontend removes that dependency for typed user variables by
renaming them to backend-safe internal identifiers before the legacy backend
sees the program. The rewrite is scope-aware, keeps functions in their own
namespace, and preserves strings/comments.
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


def _rename_identifiers(
    line: str,
    mapping: dict[str, str],
    function_names: set[str] | None = None,
) -> str:
    """Rename variable references without rewriting the function namespace."""
    code, comment = _split_code_and_tail(line)
    functions = function_names or set()
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
                end = match.end()
                next_pos = end
                while next_pos < len(code) and code[next_pos].isspace():
                    next_pos += 1
                # Function definitions/calls live in a distinct namespace from
                # variables. Do not rewrite `foo(...)` merely because a local
                # variable named `foo` exists.
                is_function_reference = next_pos < len(code) and code[next_pos] == "(" and word in functions
                if is_function_reference:
                    out.append(word)
                else:
                    out.append(mapping.get(word, word))
                pos = end
                continue
        out.append(ch)
        escaped = ch == '\\' and not escaped
        if ch != '\\':
            escaped = False
        pos += 1
    return ''.join(out) + comment


def _infer_type(expr: str, symbols: dict[str, Symbol]) -> str:
    return expression_type(expr, symbols)


def _internal_name(tag: str, scope: str, name: str, unique: int) -> str:
    safe_scope = re.sub(r"[^A-Za-z0-9_]", "_", scope)
    safe_name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    # The legacy compiler recognizes str*/string-ish spellings, while int*
    # names intentionally sit outside those string-prefix patterns.
    if tag == STR:
        return f"str_{safe_scope}_{safe_name}_{unique}"
    return f"int_{safe_scope}_{safe_name}_{unique}"


def rewrite_source(text: str) -> str:
    lines = text.splitlines(keepends=True)
    symbols_by_scope: dict[str, dict[str, Symbol]] = {"global": {}}
    mappings_by_scope: dict[str, dict[str, str]] = {"global": {}}
    function_scope = "global"
    brace_depth = 0
    unique = 0
    function_names: set[str] = set()

    # Collect the function namespace first so a variable cannot accidentally
    # rewrite a function call during the lowering pass.
    for raw in lines:
        fn = FUNCTION.match(raw)
        if fn:
            function_names.add(fn.group(1))

    for lineno, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("//"):
            continue

        fn = FUNCTION.match(raw)
        if fn:
            function_scope = fn.group(1)
            symbols_by_scope.setdefault(function_scope, {})
            mappings_by_scope.setdefault(function_scope, {})
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
                    if typ == UNKNOWN:
                        continue
                    unique += 1
                    internal = _internal_name(typ, function_scope, name, unique)
                    symbols_by_scope[function_scope][name] = Symbol(name, typ, internal, function_scope, lineno)
                    mappings_by_scope[function_scope][name] = internal
            brace_depth = max(0, raw.count("{") - raw.count("}"))
            continue

        scope_symbols = symbols_by_scope.setdefault(function_scope, {})
        scope_mapping = mappings_by_scope.setdefault(function_scope, {})

        decl = VAR_DECL.match(raw)
        if decl:
            name, expr = decl.groups()
            visible = dict(symbols_by_scope.get("global", {}))
            visible.update(scope_symbols)
            typ = _infer_type(expr, visible)
            if typ in (STR, INT):
                unique += 1
                internal = _internal_name(typ, function_scope, name, unique)
                scope_symbols[name] = Symbol(name, typ, internal, function_scope, lineno)
                scope_mapping[name] = internal
            continue

        assignment = ASSIGN.match(raw)
        if assignment and not stripped.startswith(("jika", "tapi_jika", "selama", "fungsi")):
            name, expr = assignment.groups()
            visible = dict(symbols_by_scope.get("global", {}))
            visible.update(scope_symbols)
            symbol = scope_symbols.get(name) or symbols_by_scope.get("global", {}).get(name)
            if symbol:
                typ = _infer_type(expr, visible)
                if typ != UNKNOWN:
                    target_scope = symbol.scope
                    old_symbols = symbols_by_scope[target_scope]
                    old_symbols[name] = Symbol(name, typ, symbol.internal_name, target_scope, symbol.line)
            continue

        if function_scope != "global":
            brace_depth += raw.count("{") - raw.count("}")
            if brace_depth <= 0:
                function_scope = "global"
                brace_depth = 0

    # Apply the mapping in a second pass so declaration order, shadowing, and
    # the separate function namespace are resolved before source rewriting.
    output: list[str] = []
    function_scope = "global"
    brace_depth = 0
    global_mapping = mappings_by_scope.get("global", {})

    for raw in lines:
        fn = FUNCTION.match(raw)
        if fn:
            function_scope = fn.group(1)
            brace_depth = max(0, raw.count("{") - raw.count("}"))
            mapping = dict(global_mapping)
            mapping.update(mappings_by_scope.get(function_scope, {}))
            output.append(_rename_identifiers(raw, mapping, function_names))
            continue

        mapping = dict(global_mapping)
        mapping.update(mappings_by_scope.get(function_scope, {}))
        output.append(_rename_identifiers(raw, mapping, function_names))

        if function_scope != "global":
            brace_depth += raw.count("{") - raw.count("}")
            if brace_depth <= 0:
                function_scope = "global"
                brace_depth = 0

    return ''.join(output)


def rewrite_file(source: Path, destination: Path) -> None:
    destination.write_text(rewrite_source(source.read_text(encoding="utf-8")), encoding="utf-8")
