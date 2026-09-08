#!/usr/bin/env python3
"""Idempotent migration for deterministic string-symbol tracking.

This deliberately keeps the existing parser architecture intact. It adds a
small compiler-owned symbol set for variables initialized from string literals
and makes `cetak` consult that set before the legacy naming heuristic.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE0 = ROOT / "compiler.c"
STAGE1 = ROOT / "compiler.wr"


def insert_after_once(source: str, anchor: str, insertion: str, label: str) -> str:
    if insertion in source:
        return source
    count = source.count(anchor)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return source.replace(anchor, anchor + insertion, 1)


def replace_once(source: str, anchor: str, replacement: str, label: str) -> str:
    if anchor not in source:
        if replacement in source:
            return source
        raise RuntimeError(f"{label}: anchor not found")
    if source.count(anchor) != 1:
        raise RuntimeError(f"{label}: anchor is not unique")
    return source.replace(anchor, replacement, 1)


def patch_stage0(source: str) -> str:
    helper = r'''
int is_tracked_string_var(char* name, char* string_vars) {
    int len = __wear_strlen(string_vars);
    int name_len = __wear_strlen(name);
    int i = 0;
    while (i + name_len + 1 < len) {
        if (__wear_streq(__wear_char_at(string_vars, i), ",")) {
            int j = 0;
            int match = 1;
            while (j < name_len) {
                if (!__wear_streq(__wear_char_at(string_vars, i + 1 + j), __wear_char_at(name, j))) {
                    match = 0;
                    j = name_len;
                } else {
                    j = j + 1;
                }
            }
            if (match == 1 && __wear_streq(__wear_char_at(string_vars, i + name_len + 1), ",")) {
                return 1;
            }
        }
        i = i + 1;
    }
    return 0;
}
'''
    source = insert_after_once(
        source,
        "int is_string_varname(char* name) {",
        helper,
        "stage0 helper",
    )

    source = insert_after_once(
        source,
        '    char* var_name = "";\n',
        '    char* string_vars = ",";\n',
        "stage0 symbol state",
    )

    source = replace_once(
        source,
        '                    in_var_decl = 0;\n                }\n                else {',
        '                    in_var_decl = 0;\n                    string_vars = __wear_concat(string_vars, var_name);\n                    string_vars = __wear_concat(string_vars, ",");\n                }\n                else {',
        "stage0 literal tracking",
    )

    source = replace_once(
        source,
        '                        if (returns_string(peek_word)) {',
        '                        if (is_tracked_string_var(peek_word, string_vars)==1 || returns_string(peek_word)) {',
        "stage0 tracked print",
    )
    source = replace_once(
        source,
        '                        else                         if (is_string_varname(peek_word)) {',
        '                        else                         if (is_tracked_string_var(peek_word, string_vars)==1 || is_string_varname(peek_word)) {',
        "stage0 legacy print fallback",
    )
    return source


def patch_stage1(source: str) -> str:
    helper = '''
fungsi is_tracked_string_var(name, string_vars) {
    var len = panjang(string_vars)
    var name_len = panjang(name)
    var i = 0
    selama (i + name_len + 1 < len) {
        jika (sama(char_at(string_vars, i), ",")) {
            var j = 0
            var match = 1
            selama (j < name_len) {
                jika (sama(char_at(string_vars, i + 1 + j), char_at(name, j)) == 0) {
                    match = 0
                    j = name_len
                } lainnya {
                    j = j + 1
                }
            }
            jika (match == 1) {
                jika (sama(char_at(string_vars, i + name_len + 1), ",")) {
                    kembalikan 1
                }
            }
        }
        i = i + 1
    }
    kembalikan 0
}
'''
    source = insert_after_once(
        source,
        "fungsi is_string_varname(name: str) {",
        helper,
        "stage1 helper",
    )

    source = insert_after_once(
        source,
        'var var_name = ""\n',
        'var string_vars = ","\n',
        "stage1 symbol state",
    )

    source = replace_once(
        source,
        '                in_var_decl = 0\n            } lainnya {',
        '                in_var_decl = 0\n                string_vars = string_vars + var_name\n                string_vars = string_vars + ","\n            } lainnya {',
        "stage1 literal tracking",
    )

    source = replace_once(
        source,
        '                        jika (returns_string(peek_word)) {',
        '                        jika (is_tracked_string_var(peek_word, string_vars) == 1 || returns_string(peek_word)) {',
        "stage1 tracked print",
    )
    source = replace_once(
        source,
        '                    } lainnya jika (is_string_varname(peek_word)) {',
        '                    } lainnya jika (is_tracked_string_var(peek_word, string_vars) == 1 || is_string_varname(peek_word)) {',
        "stage1 legacy print fallback",
    )
    return source


def main() -> int:
    if not STAGE0.is_file() or not STAGE1.is_file():
        raise SystemExit("compiler.c and compiler.wr are required")
    old0 = STAGE0.read_text(encoding="utf-8")
    old1 = STAGE1.read_text(encoding="utf-8")
    new0 = patch_stage0(old0)
    new1 = patch_stage1(old1)
    if new0 != old0:
        STAGE0.write_text(new0, encoding="utf-8")
        print("updated compiler.c")
    else:
        print("unchanged compiler.c")
    if new1 != old1:
        STAGE1.write_text(new1, encoding="utf-8")
        print("updated compiler.wr")
    else:
        print("unchanged compiler.wr")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
