#!/usr/bin/env python3
"""Lightweight source-structure guard for the WeaR Lang frontend.

Runs before semantic analysis and reports malformed lexical/structural
constructs with stable line/column locations.
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
    delimiters: list[tuple[str, int, int]] = []
    in_string = False
    escaped = False
    in_comment = False
    string_line = 0
    string_column = 0
    line = 1
    column = 0

    index = 0
    while index < len(text):
        char = text[index]
        column += 1

        if in_comment:
            if char == "\n":
                in_comment = False
                line += 1
                column = 0
            index += 1
            continue

        if in_string:
            if char == "\n":
                diagnostics.append(SyntaxDiagnostic(string_line, string_column, "unterminated string literal"))
                in_string = False
                escaped = False
                line += 1
                column = 0
                index += 1
                continue
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            escaped = False
            string_line = line
            string_column = column
        elif char == "/" and index + 1 < len(text) and text[index + 1] == "/":
            in_comment = True
            index += 1
            column += 1
        elif char in "({":
            delimiters.append((char, line, column))
        elif char in ")}":
            expected = "(" if char == ")" else "{"
            if not delimiters or delimiters[-1][0] != expected:
                diagnostics.append(SyntaxDiagnostic(line, column, f"unmatched '{char}'"))
            else:
                delimiters.pop()

        if char == "\n":
            line += 1
            column = 0
        index += 1

    if in_string:
        diagnostics.append(SyntaxDiagnostic(string_line, string_column, "unterminated string literal"))

    for opener, item_line, item_column in reversed(delimiters):
        diagnostics.append(SyntaxDiagnostic(item_line, item_column, f"unclosed '{opener}'"))

    diagnostics.sort(key=lambda item: (item.line, item.column, item.message))
    return [item.render(source) for item in diagnostics]


__all__ = ["SyntaxDiagnostic", "check_source"]
