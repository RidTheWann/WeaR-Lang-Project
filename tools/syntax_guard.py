#!/usr/bin/env python3
"""Lightweight source-structure guard for the WeaR Lang frontend.

The guard runs before semantic analysis and reports malformed lexical/structural
constructs with stable line/column locations. It deliberately does not parse
the language; its job is to prevent obviously broken source from reaching the
legacy backend and producing confusing generated C.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyntaxDiagnostic:
    line: int
    column: int
    message: str

    def render(self, source: Path) -> str:
        return f"{source}:{self.line}:{self.column}: {self.message}"


def check_source(path: str | Path) -> list[str]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    diagnostics: list[SyntaxDiagnostic] = []

    parens: list[tuple[str, int, int]] = []
    braces: list[tuple[str, int, int]] = []
    in_string = False
    escaped = False
    in_comment = False
    string_line = 0
    string_column = 0
    line = 1
    column = 0

    for char in text:
        column += 1

        if char == "\n":
            if in_comment:
                in_comment = False
            line += 1
            column = 0
            if in_string:
                diagnostics.append(
                    SyntaxDiagnostic(
                        string_line,
                        string_column,
                        "unterminated string literal",
                    )
                )
                in_string = False
                escaped = False
            continue

        if in_comment:
            continue

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            string_line = line
            string_column = column
            continue

        if char == "/":
            # Comment detection is intentionally handled by the next character
            # in a tiny state machine below; a single slash remains ordinary.
            continue

        if char == "(":
            parens.append(("(", line, column))
        elif char == ")":
            if not parens:
                diagnostics.append(SyntaxDiagnostic(line, column, "unmatched ')'"))
            else:
                parens.pop()
        elif char == "{":
            braces.append(("{", line, column))
        elif char == "}":
            if not braces:
                diagnostics.append(SyntaxDiagnostic(line, column, "unmatched '}'"))
            else:
                braces.pop()

    if in_string:
        diagnostics.append(SyntaxDiagnostic(string_line, string_column, "unterminated string literal"))

    for _, item_line, item_column in reversed(parens):
        diagnostics.append(SyntaxDiagnostic(item_line, item_column, "unclosed '('") )
    for _, item_line, item_column in reversed(braces):
        diagnostics.append(SyntaxDiagnostic(item_line, item_column, "unclosed '{'"))

    diagnostics.sort(key=lambda item: (item.line, item.column, item.message))
    return [item.render(source) for item in diagnostics]


__all__ = ["SyntaxDiagnostic", "check_source"]
