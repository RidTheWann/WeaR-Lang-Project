#!/usr/bin/env python3
"""One-shot migration to add deterministic string symbol tracking.

The current compiler defaults unknown variables to int. This migration adds a
small delimiter-based symbol table for variables proven to be strings by the
existing declaration inference paths, then makes `cetak` consult that table
before falling back to legacy heuristics.

The transformation is intentionally exact and idempotent so it can be applied
once to both Stage-0 (compiler.c) and Stage-1 (compiler.wr).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE0 = ROOT / "compiler.c"
STAGE1 = ROOT / "compiler.wr"


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count == 0:
        if new in source:
            return source
        raise RuntimeError(f"{label}: anchor not found")
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


def patch_stage0(source: str) -> str:
    helper = '''\nint is_tracked_string_var(char* name, char* string_vars) {\n    int len = __wear_strlen(string_vars);\n    int name_len = __wear_strlen(name);\n    if (len < name_len + 2) {\n        return 0;\n    }\n    int i = 0;\n    while (i <= len - name_len - 2) {\n        if (__wear_streq(__wear_char_at(string_vars, i), ",")) {\n            int j = 0;\n            int match = 1;\n            while (j < name_len) {\n                if (!__wear_streq(__wear_char_at(string_vars, i + 1 + j), __wear_char_at(name, j))) {\n                    match = 0;\n                    j = name_len;\n                } else {\n                    j = j + 1;\n                }\n            }\n            if (match == 1 && __wear_streq(__wear_char_at(string_vars, i + name_len + 1), ",")) {\n                return 1;\n            }\n        }\n        i = i + 1;\n    }\n    return 0;\n}\n'''
    if "int is_tracked_string_var(char* name, char* string_vars)" not in source:
        source = replace_once(
            source,
            "int is_string_varname(char* name) {",
            helper + "\nint is_string_varname(char* name) {",
            "stage0 helper insertion",
        )

    source = replace_once(
        source,
        '    char* var_name = "";\n',
        '    char* var_name = "";\n    char* string_vars = ",";\n',
        "stage0 symbol table state",
    )

    source = replace_once(
        source,
        '                        global_code = __wear_concat(global_code, q);\n                        global_code = __wear_concat(global_code, str_content);\n                        global_code = __wear_concat(global_code, q);\n                    }\n                    else {\n                        main_code = __wear_concat(main_code, "char* ");',
        '                        global_code = __wear_concat(global_code, q);\n                        global_code = __wear_concat(global_code, str_content);\n                        global_code = __wear_concat(global_code, q);\n                    }\n                    string_vars = __wear_concat(string_vars, var_name);\n                    string_vars = __wear_concat(string_vars, ",");\n                    if (inside_func==0) {\n                    }\n                    else {\n                        main_code = __wear_concat(main_code, "char* ");',
        "stage0 literal tracking anchor",
    )
    # The exact replacement above intentionally leaves the existing branch body intact;
    # remove the empty conditional introduced as a stable insertion point.
    source = source.replace('                    if (inside_func==0) {\n                    }\n', '')

    source = source.replace(
        '                            in_var_decl = 0;\n                        }\n                        else {\n                            if (inside_func==1) {\n                                global_code = __wear_concat(global_code, "char* ");',
        '                            in_var_decl = 0;\n                            string_vars = __wear_concat(string_vars, var_name);\n                            string_vars = __wear_concat(string_vars, ",");\n                        }\n                        else {\n                            if (inside_func==1) {\n                                global_code = __wear_concat(global_code, "char* ");',
        1,
    )

    source = replace_once(
        source,
        '                        if (returns_string(peek_word)) {\n                            if (inside_func==1) {',
        '                        if (is_tracked_string_var(peek_word, string_vars)==1 || returns_string(peek_word)) {\n                            if (inside_func==1) {',
        "stage0 print dispatch",
    )
    source = source.replace(
        '                    else                     if (is_string_varname(peek_word)) {',
        '                    else                     if (is_tracked_string_var(peek_word, string_vars)==1 || is_string_varname(peek_word)) {',
        1,
    )
    return source


def patch_stage1(source: str) -> str:
    helper = '''\nfungsi is_tracked_string_var(name: str, string_vars: str) {\n    var len = panjang(string_vars)\n    var name_len = panjang(name)\n    jika (len < name_len + 2) { kembalikan 0 }\n    var i = 0\n    selama (i <= len - name_len - 2) {\n        jika (sama(char_at(string_vars, i), ",")) {\n            var j = 0\n            var match = 1\n            selama (j < name_len) {\n                jika (bukan(sama(char_at(string_vars, i + 1 + j), char_at(name, j)))) {\n                    match = 0\n                    j = name_len\n                } lainnya {\n                    j = j + 1\n                }\n            }\n            jika (match == 1) {\n                jika (sama(char_at(string_vars, i + name_len + 1), ",")) {\n                    kembalikan 1\n                }\n            }\n        }\n        i = i + 1\n    }\n    kembalikan 0\n}\n'''
    if "fungsi is_tracked_string_var(name: str, string_vars: str)" not in source:
        source = replace_once(
            source,
            "fungsi is_string_varname(name: str) {",
            helper + "\nfungsi is_string_varname(name: str) {",
            "stage1 helper insertion",
        )

    source = replace_once(
        source,
        'var var_name = ""\n',
        'var var_name = ""\nvar string_vars = ","\n',
        "stage1 symbol table state",
    )

    source = replace_once(
        source,
        '                    global_code = global_code + q\n                    global_code = global_code + str_content\n                    global_code = global_code + q\n                }\n                in_var_decl = 0',
        '                    global_code = global_code + q\n                    global_code = global_code + str_content\n                    global_code = global_code + q\n                }\n                string_vars = string_vars + var_name\n                string_vars = string_vars + ","\n                in_var_decl = 0',
        "stage1 string literal tracking",
    )

    source = replace_once(
        source,
        '                        jika (returns_string(peek_word)) {',
        '                        jika (is_tracked_string_var(peek_word, string_vars) == 1 || returns_string(peek_word)) {',
        "stage1 print dispatch",
    )
    source = source.replace(
        '                    } lainnya jika (is_string_varname(peek_word)) {',
        '                    } lainnya jika (is_tracked_string_var(peek_word, string_vars) == 1 || is_string_varname(peek_word)) {',
        1,
    )
    return source


def main() -> int:
    stage0 = STAGE0.read_text(encoding="utf-8")
    stage1 = STAGE1.read_text(encoding="utf-8")
    patched0 = patch_stage0(stage0)
    patched1 = patch_stage1(stage1)
    if patched0 != stage0:
        STAGE0.write_text(patched0, encoding="utf-8")
        print("updated compiler.c")
    else:
        print("unchanged compiler.c")
    if patched1 != stage1:
        STAGE1.write_text(patched1, encoding="utf-8")
        print("updated compiler.wr")
    else:
        print("unchanged compiler.wr")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
