#!/usr/bin/env python3
"""Normalize localized WeaR source into the canonical compiler dialect.

The compiler core should not need a separate parser for every human language.
This frontend translates supported localized keywords into the canonical
Indonesian token spelling before semantic analysis and code generation.
Strings and comments are preserved verbatim.
"""

from __future__ import annotations

from pathlib import Path

SUPPORTED_LANGUAGES = ("auto", "id", "en")

KEYWORDS = {
    "en": {
        "function": "fungsi",
        "if": "jika",
        "else": "lainnya",
        "elif": "tapi_jika",
        "while": "selama",
        "return": "kembalikan",
        "print": "cetak",
        "import": "impor",
        "true": "benar",
        "false": "salah",
    },
    "id": {},
}


def _replace_code_tokens(code: str, mapping: dict[str, str]) -> str:
    out: list[str] = []
    index = 0
    length = len(code)

    while index < length:
        char = code[index]
        if char.isalpha() or char == "_":
            start = index
            index += 1
            while index < length and (code[index].isalnum() or code[index] == "_"):
                index += 1
            token = code[start:index]
            out.append(mapping.get(token, token))
            continue
        out.append(char)
        index += 1

    return "".join(out)


def normalize_source(text: str, language: str = "auto") -> str:
    """Normalize source keywords while preserving strings and comments."""
    language = language.lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"unsupported language dialect: {language}")

    if language == "auto":
        mapping: dict[str, str] = {}
        for aliases in KEYWORDS.values():
            mapping.update(aliases)
    else:
        mapping = KEYWORDS[language]

    if not mapping:
        return text

    output: list[str] = []
    for raw_line in text.splitlines(keepends=True):
        code: list[str] = []
        tail = ""
        in_string = False
        escaped = False
        comment_at = -1

        for index, char in enumerate(raw_line):
            if in_string:
                code.append(char)
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                code.append(char)
                continue

            if char == "/" and index + 1 < len(raw_line) and raw_line[index + 1] == "/":
                comment_at = index
                break

            code.append(char)

        if comment_at >= 0:
            tail = raw_line[comment_at:]

        output.append(_replace_code_tokens("".join(code), mapping) + tail)

    return "".join(output)


def normalize_file(source: Path, destination: Path, language: str = "auto") -> None:
    destination.write_text(
        normalize_source(source.read_text(encoding="utf-8"), language),
        encoding="utf-8",
    )


__all__ = ["KEYWORDS", "SUPPORTED_LANGUAGES", "normalize_file", "normalize_source"]
