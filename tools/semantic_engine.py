#!/usr/bin/env python3
"""Canonical semantic engine for deterministic WeaR Lang type resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from type_system import ERROR, INT, STR, UNKNOWN, FunctionSignature, Symbol


@dataclass(frozen=True)
class Diagnostic:
    line: int
    column: int
    message: str

    def render(self, source: Path) -> str:
        return f"{source}:{self.line}:{self.column}: {self.message}"


BUILTINS = {
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
FUNCTION_RE = re.compile(r"^\s*fungsi\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*\{?\s*$")
VAR_RE = re.compile(r"^\s*var\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
ASSIGN_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
CETAK_RE = re.compile(r"^\s*cetak\s+(.+?)\s*$")
RETURN_RE = re.compile(r"^\s*kembalikan(?:\s+(.*?))?\s*$")


def is_identifier(value: str) -> bool:
    return bool(IDENTIFIER_RE.fullmatch(value.strip()))


def literal_type(expr: str) -> str:
    value = expr.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return STR
    if INTEGER_RE.fullmatch(value):
        return INT
    if value in {"benar", "salah", "true", "false"}:
        return INT
    return UNKNOWN


def _strip_comment(line: str) -> str:
    in_string = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if not in_string and line[index:index + 2] == "//":
            return line[:index]
    return line


def _unwrap_parentheses(expr: str) -> str:
    value = expr.strip()
    while len(value) >= 2 and value[0] == "(" and value[-1] == ")":
        depth = 0
        in_string = False
        escaped = False
        encloses = True
        for index, char in enumerate(value):
            if escaped:
                escaped = False
            elif char == "\\" and in_string:
                escaped = True
            elif char == '"':
                in_string = not in_string
            elif not in_string:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0 and index != len(value) - 1:
                        encloses = False
                        break
        if encloses and depth == 0:
            value = value[1:-1].strip()
        else:
            break
    return value


def _split_top_level(expr: str, operator: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    in_string = False
    escaped = False
    index = 0
    while index < len(expr):
        char = expr[index]
        if escaped:
            escaped = False
        elif char == "\\" and in_string:
            escaped = True
        elif char == '"':
            in_string = not in_string
        elif not in_string:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and expr.startswith(operator, index):
                parts.append(expr[start:index].strip())
                start = index + len(operator)
                index += len(operator) - 1
        index += 1
    if parts:
        parts.append(expr[start:].strip())
    return parts


def _split_call(expr: str) -> tuple[str, str] | None:
    value = _unwrap_parentheses(expr)
    opening = value.find("(")
    if opening <= 0 or not value.endswith(")"):
        return None
    name = value[:opening].strip()
    if not is_identifier(name):
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(opening, len(value)):
        char = value[index]
        if escaped:
            escaped = False
        elif char == "\\" and in_string:
            escaped = True
        elif char == '"':
            in_string = not in_string
        elif not in_string:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and index != len(value) - 1:
                    return None
    return (name, value[opening + 1:-1].strip()) if depth == 0 else None


def _split_arguments(arguments: str) -> list[str]:
    if not arguments.strip():
        return []
    parts: list[str] = []
    start = 0
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(arguments):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
        elif not in_string:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif char == "," and depth == 0:
                parts.append(arguments[start:index].strip())
                start = index + 1
    parts.append(arguments[start:].strip())
    return parts


def expression_type(expr: str, symbols: dict[str, Symbol], functions: dict[str, FunctionSignature] | None = None) -> str:
    value = _unwrap_parentheses(expr)
    direct = literal_type(value)
    if direct != UNKNOWN:
        return direct
    if is_identifier(value):
        symbol = symbols.get(value)
        return symbol.type_name if symbol else UNKNOWN

    functions = functions or BUILTINS
    call = _split_call(value)
    if call:
        name, arguments = call
        signature = functions.get(name) or BUILTINS.get(name)
        if signature is None:
            return UNKNOWN
        args = _split_arguments(arguments)
        if len(args) != len(signature.params):
            return ERROR
        for argument, expected in zip(args, signature.params):
            actual = expression_type(argument, symbols, functions)
            if actual == ERROR or (actual not in {UNKNOWN, expected}):
                return ERROR
        return signature.return_type

    for operator in ("==", "<=", ">=", "<", ">"):
        parts = _split_top_level(value, operator)
        if len(parts) == 2:
            left = expression_type(parts[0], symbols, functions)
            right = expression_type(parts[1], symbols, functions)
            return ERROR if ERROR in {left, right} else INT

    for operator in ("+", "-", "*", "/"):
        parts = _split_top_level(value, operator)
        if len(parts) >= 2:
            types = [expression_type(part, symbols, functions) for part in parts]
            if ERROR in types:
                return ERROR
            if operator == "+" and STR in types and all(item in {STR, INT, UNKNOWN} for item in types):
                return STR
            if all(item == INT for item in types):
                return INT
            return UNKNOWN
    return UNKNOWN


def _parameter_types(text: str) -> tuple[str, ...]:
    result: list[str] = []
    for raw in _split_arguments(text):
        if not raw:
            continue
        pieces = raw.split(":", 1)
        type_name = pieces[1].strip() if len(pieces) == 2 else UNKNOWN
        result.append(type_name if type_name in {INT, STR} else UNKNOWN)
    return tuple(result)


def _collect_functions(lines: list[str]) -> dict[str, FunctionSignature]:
    functions = dict(BUILTINS)
    declarations: dict[str, tuple[int, str]] = {}
    for lineno, raw in enumerate(lines, 1):
        match = FUNCTION_RE.match(_strip_comment(raw).strip())
        if match:
            name, params = match.groups()
            functions[name] = FunctionSignature(UNKNOWN, _parameter_types(params), lineno)
            declarations[name] = (lineno, params)

    for name, (start_line, params) in declarations.items():
        signature = functions[name]
        parameter_names = [p.split(":", 1)[0].strip() for p in _split_arguments(params) if p.strip()]
        local = {
            parameter_names[i]: Symbol(parameter_names[i], signature.params[i], start_line, name)
            for i in range(min(len(parameter_names), len(signature.params)))
        }
        depth = 0
        saw_body = False
        return_types: set[str] = set()
        for index in range(start_line - 1, len(lines)):
            text = _strip_comment(lines[index]).strip()
            depth += text.count("{") - text.count("}")
            if "{" in text:
                saw_body = True
            if saw_body:
                match = RETURN_RE.match(text)
                if match:
                    expr = match.group(1) or ""
                    result = INT if not expr else expression_type(expr, local, functions)
                    if result in {INT, STR, ERROR}:
                        return_types.add(result)
            if saw_body and depth <= 0:
                break
        if ERROR in return_types or len(return_types) > 1:
            inferred = ERROR
        elif len(return_types) == 1:
            inferred = next(iter(return_types))
        else:
            inferred = UNKNOWN
        functions[name] = FunctionSignature(inferred, signature.params, start_line)
    return functions


def _visible(global_symbols: dict[str, Symbol], local_symbols: dict[str, Symbol] | None) -> dict[str, Symbol]:
    visible = dict(global_symbols)
    if local_symbols is not None:
        visible.update(local_symbols)
    return visible


def _store(global_symbols: dict[str, Symbol], local_symbols: dict[str, Symbol] | None, function: str | None, name: str, type_name: str, line: int) -> None:
    symbol = Symbol(name, type_name, line, function or "global")
    if function and local_symbols is not None:
        local_symbols[name] = symbol
    else:
        global_symbols[name] = symbol


def check_source(path: str | Path) -> list[str]:
    source = Path(path)
    lines = source.read_text(encoding="utf-8").splitlines()
    functions = _collect_functions(lines)
    diagnostics: list[Diagnostic] = []
    global_symbols: dict[str, Symbol] = {}
    local_symbols: dict[str, Symbol] | None = None
    active_function: str | None = None
    brace_depth = 0

    for lineno, raw in enumerate(lines, 1):
        line = _strip_comment(raw)
        stripped = line.strip()
        if not stripped:
            continue

        function_match = FUNCTION_RE.match(stripped)
        if function_match:
            active_function = function_match.group(1)
            local_symbols = {}
            signature = functions.get(active_function, FunctionSignature(UNKNOWN))
            params = _split_arguments(function_match.group(2))
            for index, raw_param in enumerate(params):
                if not raw_param.strip():
                    continue
                pieces = raw_param.split(":", 1)
                name = pieces[0].strip()
                type_name = pieces[1].strip() if len(pieces) == 2 else UNKNOWN
                if type_name not in {INT, STR}:
                    diagnostics.append(Diagnostic(lineno, max(1, line.find(name) + 1), f"parameter '{name}' requires : int or : str"))
                local_symbols[name] = Symbol(name, type_name, lineno, active_function)
            brace_depth = stripped.count("{") - stripped.count("}")
            continue

        symbols = _visible(global_symbols, local_symbols if active_function else None)
        if active_function:
            brace_depth += stripped.count("{") - stripped.count("}")

        match = VAR_RE.match(stripped)
        if match:
            name, expr = match.groups()
            value_type = expression_type(expr, symbols, functions)
            if value_type == UNKNOWN:
                diagnostics.append(Diagnostic(lineno, max(1, line.find(expr) + 1), f"cannot infer type of initializer for '{name}'"))
            elif value_type == ERROR:
                diagnostics.append(Diagnostic(lineno, max(1, line.find(expr) + 1), f"invalid initializer expression for '{name}'"))
            _store(global_symbols, local_symbols, active_function, name, value_type, lineno)
            continue

        match = ASSIGN_RE.match(stripped)
        if match and not stripped.startswith(("jika", "lainnya", "selama", "fungsi")):
            name, expr = match.groups()
            symbol = symbols.get(name)
            if symbol is None:
                diagnostics.append(Diagnostic(lineno, max(1, line.find(name) + 1), f"assignment to undeclared variable '{name}'"))
            else:
                value_type = expression_type(expr, symbols, functions)
                if value_type == ERROR:
                    diagnostics.append(Diagnostic(lineno, max(1, line.find(expr) + 1), f"invalid assignment expression for '{name}'"))
                elif value_type != UNKNOWN and symbol.type_name != UNKNOWN and value_type != symbol.type_name:
                    diagnostics.append(Diagnostic(lineno, max(1, line.find(expr) + 1), f"type mismatch for '{name}': declared {symbol.type_name}, assigned {value_type}"))
            continue

        match = CETAK_RE.match(stripped)
        if match:
            expr = match.group(1)
            value_type = expression_type(expr, symbols, functions)
            if value_type in {UNKNOWN, ERROR}:
                diagnostics.append(Diagnostic(lineno, max(1, line.find(expr) + 1), f"cannot resolve type of cetak expression: {expr}"))
            continue

        match = RETURN_RE.match(stripped)
        if match and active_function:
            expr = match.group(1) or ""
            value_type = INT if not expr else expression_type(expr, symbols, functions)
            expected = functions.get(active_function, FunctionSignature(INT)).return_type
            if value_type in {UNKNOWN, ERROR}:
                diagnostics.append(Diagnostic(lineno, max(1, line.find("kembalikan") + 1), f"cannot resolve return expression type in '{active_function}'"))
            elif expected not in {UNKNOWN, ERROR} and value_type != expected:
                diagnostics.append(Diagnostic(lineno, max(1, line.find("kembalikan") + 1), f"return type mismatch in '{active_function}': expected {expected}, got {value_type}"))

        if active_function and brace_depth <= 0:
            active_function = None
            local_symbols = None
            brace_depth = 0

    return [item.render(source) for item in diagnostics]


__all__ = ["BUILTINS", "Diagnostic", "ERROR", "FunctionSignature", "INT", "STR", "Symbol", "UNKNOWN", "check_source", "expression_type"]
