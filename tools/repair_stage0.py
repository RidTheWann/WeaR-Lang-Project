#!/usr/bin/env python3
"""Apply the minimal M1 Stage-0 bootstrap repairs.

The current compiler.c is generated legacy Stage-0 code. This codemod keeps the
repair explicit and idempotent so source-level changes are reviewable.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "compiler.c"
RUNTIME = ROOT / "runtime.c"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new)
    if count == 0 and new in text:
        return text
    raise SystemExit(f"repair_stage0: expected exactly one {label} block, found {count}")


def repair_concat_legacy_runtime(source: str) -> str:
    old = '''char* __wear_concat(const char* a, const char* b) {\n    size_t len_a = strlen(a);\n    size_t len_b = strlen(b);\n    char* result = (char*)malloc(len_a + len_b + 1);\n    if (result == NULL) {\n        fprintf(stderr, "Error: Memory allocation failed\\n");\n        exit(1);\n    }\n    strcpy(result, a);\n    strcat(result, b);\n    return result;\n}\n'''
    new = '''char* __wear_concat2(const char* a, const char* b) {\n    if (a == NULL) a = "";\n    if (b == NULL) b = "";\n    size_t len_a = strlen(a);\n    size_t len_b = strlen(b);\n    if (len_a > SIZE_MAX - len_b - 1) {\n        fprintf(stderr, "Error: String size overflow\\n");\n        exit(1);\n    }\n    char* result = (char*)malloc(len_a + len_b + 1);\n    if (result == NULL) {\n        fprintf(stderr, "Error: Memory allocation failed\\n");\n        exit(1);\n    }\n    memcpy(result, a, len_a);\n    memcpy(result + len_a, b, len_b + 1);\n    return result;\n}\n\nchar* __wear_concat3(const char* a, const char* b, const char* c) {\n    char* first = __wear_concat2(a, b);\n    char* result = __wear_concat2(first, c);\n    free(first);\n    return result;\n}\n\n#define __wear_concat_pick(_1, _2, _3, NAME, ...) NAME\n#define __wear_concat(...) \\\n    __wear_concat_pick(__VA_ARGS__, __wear_concat3, __wear_concat2)(__VA_ARGS__)\n'''
    return replace_once(source, old, new, "embedded concat runtime")


def repair_compiler(source: str) -> str:
    if '#include <stdint.h>' not in source:
        source = source.replace('#include <string.h>\n', '#include <string.h>\n#include <stdint.h>\n', 1)

    source = repair_concat_legacy_runtime(source)

    old_returns = '''int returns_string(char* fn) {\n    if (__wear_streq(fn, "baca_file")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "char_at")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "quote_char")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "newline_char")) {\n        return 1;\n    }\n    return 0;\n}\n'''
    new_returns = '''int returns_string(char* fn) {\n    if (__wear_streq(fn, "baca_file")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "char_at")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "quote_char")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "newline_char")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "input")) {\n        return 1;\n    }\n    if (__wear_streq(fn, "process_imports")) {\n        return 1;\n    }\n    return 0;\n}\n'''
    source = replace_once(source, old_returns, new_returns, "returns_string")

    old_function_type = '''                    global_code = __wear_concat(global_code, "int ");\n                    global_code = __wear_concat(global_code, func_name);\n                    global_code = __wear_concat(global_code, "(");\n'''
    new_function_type = '''                    if (returns_string(func_name)) {\n                        global_code = __wear_concat(global_code, "char* ");\n                    }\n                    else {\n                        global_code = __wear_concat(global_code, "int ");\n                    }\n                    global_code = __wear_concat(global_code, func_name);\n                    global_code = __wear_concat(global_code, "(");\n'''
    source = replace_once(source, old_function_type, new_function_type, "function return type")
    return source


def repair_runtime(source: str) -> str:
    old = '''/* Generic string/int concatenation dispatch. */\n#define __wear_concat(a, b) _Generic((b), \\\n    int: __wear_concat_str_int, \\\n    char*: __wear_concat_impl, \\\n    const char*: __wear_concat_impl \\\n)(a, b)\n'''
    new = '''/* Three-operand string concatenation helper for legacy generated code. */\nchar* __wear_concat3(const char* a, const char* b, const char* c) {\n    char* first = __wear_concat_impl(a, b);\n    char* result = __wear_concat_impl(first, c);\n    free(first);\n    return result;\n}\n\n#define __wear_concat2(a, b) _Generic((b), \\\n    int: __wear_concat_str_int, \\\n    char*: __wear_concat_impl, \\\n    const char*: __wear_concat_impl \\\n)(a, b)\n\n#define __wear_concat_pick(_1, _2, _3, NAME, ...) NAME\n#define __wear_concat(...) \\\n    __wear_concat_pick(__VA_ARGS__, __wear_concat3, __wear_concat2)(__VA_ARGS__)\n'''
    return replace_once(source, old, new, "runtime concat dispatch")


def main() -> int:
    compiler = COMPILER.read_text(encoding="utf-8")
    runtime = RUNTIME.read_text(encoding="utf-8")

    repaired_compiler = repair_compiler(compiler)
    repaired_runtime = repair_runtime(runtime)

    if repaired_compiler != compiler:
        COMPILER.write_text(repaired_compiler, encoding="utf-8")
        print(f"updated {COMPILER.relative_to(ROOT)}")
    else:
        print(f"unchanged {COMPILER.relative_to(ROOT)}")

    if repaired_runtime != runtime:
        RUNTIME.write_text(repaired_runtime, encoding="utf-8")
        print(f"updated {RUNTIME.relative_to(ROOT)}")
    else:
        print(f"unchanged {RUNTIME.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
