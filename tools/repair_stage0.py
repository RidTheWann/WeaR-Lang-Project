#!/usr/bin/env python3
"""Apply deterministic M1 bootstrap repairs to Stage-0 and Stage-1 sources.

The current compiler.c is generated legacy Stage-0 code. These repairs remain
small and idempotent so the resulting source changes are reviewable.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "compiler.c"
STAGE1 = ROOT / "compiler.wr"
RUNTIME = ROOT / "runtime.c"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new)
    if count == 0 and new in text:
        return text
    raise SystemExit(f"repair_stage0: expected exactly one {label} block, found {count}")


def repair_stage1_source(source: str) -> str:
    declarations = {
        "is_digit": "c",
        "is_letter": "c",
        "is_space": "c",
        "returns_int": "fn",
        "returns_string": "fn",
        "is_string_varname": "name",
        "process_imports": "src",
    }
    for name, param in declarations.items():
        old = f"fungsi {name}({param}) {{"
        new = f"fungsi {name}({param}: str) {{"
        source = replace_once(source, old, new, f"typed parameter annotation for {name}")

    source = replace_once(
        source,
        'global_proto = global_proto + ");" + nl',
        'global_proto = global_proto + ");"\nglobal_proto = global_proto + nl',
        "prototype concatenation",
    )
    source = replace_once(
        source,
        'final_output = final_output + "/* Function Prototypes */" + nl',
        'final_output = final_output + "/* Function Prototypes */"\nfinal_output = final_output + nl',
        "prototype header concatenation",
    )
    source = replace_once(
        source,
        'final_output = final_output + "/* Function Definitions */" + nl',
        'final_output = final_output + "/* Function Definitions */"\nfinal_output = final_output + nl',
        "definition header concatenation",
    )
    return source


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

    source = replace_once(
        source,
        'char* global_code = "";\n    char* main_code = "";',
        'char* global_protos = "";\n    char* global_code = "";\n    char* main_code = "";',
        "prototype output buffer",
    )

    old_function_prefix = '''                    if (returns_string(func_name)) {\n                        global_code = __wear_concat(global_code, "char* ");\n                    }\n                    else {\n                        global_code = __wear_concat(global_code, "int ");\n                    }\n                    global_code = __wear_concat(global_code, func_name);\n                    global_code = __wear_concat(global_code, "(");\n                    int skip_to_paren = 1;\n'''
    new_function_prefix = '''                    if (returns_string(func_name)) {\n                        global_code = __wear_concat(global_code, "char* ");\n                    }\n                    else {\n                        global_code = __wear_concat(global_code, "int ");\n                    }\n                    global_code = __wear_concat(global_code, func_name);\n                    global_code = __wear_concat(global_code, "(");\n                    char* global_proto = "";\n                    if (returns_string(func_name)) {\n                        global_proto = __wear_concat(global_proto, "char* ");\n                    }\n                    else {\n                        global_proto = __wear_concat(global_proto, "int ");\n                    }\n                    global_proto = __wear_concat(global_proto, func_name);\n                    global_proto = __wear_concat(global_proto, "(");\n                    int skip_to_paren = 1;\n'''
    source = replace_once(source, old_function_prefix, new_function_prefix, "function prototype initialization")

    old_param_tail = '''                                if (first_param==1) {\n                                    global_code = __wear_concat(global_code, "char* ");\n                                    global_code = __wear_concat(global_code, param_name);\n                                    first_param = 0;\n                                }\n                                else {\n                                    global_code = __wear_concat(global_code, ", char* ");\n                                    global_code = __wear_concat(global_code, param_name);\n                                }\n'''
    new_param_tail = '''                                char* param_type = "char* ";\n                                int skip_type_ws = 1;\n                                while (skip_type_ws==1) {\n                                    if (i>=len) {\n                                        skip_type_ws = 0;\n                                    }\n                                    else {\n                                        char* type_ws = __wear_char_at(source, i);\n                                        if (is_space(type_ws)) {\n                                            i = i+1;\n                                        }\n                                        else {\n                                            skip_type_ws = 0;\n                                        }\n                                    }\n                                }\n                                char* colon = __wear_char_at(source, i);\n                                if (__wear_streq(colon, ":")) {\n                                    i = i+1;\n                                    int skip_type_ws2 = 1;\n                                    while (skip_type_ws2==1) {\n                                        if (i>=len) {\n                                            skip_type_ws2 = 0;\n                                        }\n                                        else {\n                                            char* type_ws2 = __wear_char_at(source, i);\n                                            if (is_space(type_ws2)) {\n                                                i = i+1;\n                                            }\n                                            else {\n                                                skip_type_ws2 = 0;\n                                            }\n                                        }\n                                    }\n                                    char* type_name = "";\n                                    int read_type = 1;\n                                    while (read_type==1) {\n                                        if (i>=len) {\n                                            read_type = 0;\n                                        }\n                                        else {\n                                            char* type_char = __wear_char_at(source, i);\n                                            if (is_letter(type_char)) {\n                                                type_name = __wear_concat(type_name, type_char);\n                                                i = i+1;\n                                            }\n                                            else {\n                                                read_type = 0;\n                                            }\n                                        }\n                                    }\n                                    if (__wear_streq(type_name, "int")) {\n                                        param_type = "int ";\n                                    }\n                                    else {\n                                        param_type = "char* ";\n                                    }\n                                }\n\n                                if (first_param==1) {\n                                    global_code = __wear_concat(global_code, param_type);\n                                    global_code = __wear_concat(global_code, param_name);\n                                    global_proto = __wear_concat(global_proto, param_type);\n                                    global_proto = __wear_concat(global_proto, param_name);\n                                    first_param = 0;\n                                }\n                                else {\n                                    global_code = __wear_concat(global_code, ", ");\n                                    global_code = __wear_concat(global_code, param_type);\n                                    global_code = __wear_concat(global_code, param_name);\n                                    global_proto = __wear_concat(global_proto, ", ");\n                                    global_proto = __wear_concat(global_proto, param_type);\n                                    global_proto = __wear_concat(global_proto, param_name);\n                                }\n'''
    source = replace_once(source, old_param_tail, new_param_tail, "typed parameter handling")

    old_function_close = '''                    global_code = __wear_concat(global_code, ")");\n                    need_semi = 0;\n'''
    new_function_close = '''                    global_code = __wear_concat(global_code, ")");\n                    global_proto = __wear_concat(global_proto, ");");\n                    global_proto = __wear_concat(global_proto, nl);\n                    global_protos = __wear_concat(global_protos, global_proto);\n                    need_semi = 0;\n'''
    source = replace_once(source, old_function_close, new_function_close, "function prototype finalization")

    old_assembly = '''    final_output = __wear_concat(final_output, runtime_code);\n    final_output = __wear_concat(final_output, nl);\n    final_output = __wear_concat(final_output, nl);\n    final_output = __wear_concat(final_output, global_code);\n'''
    new_assembly = '''    final_output = __wear_concat(final_output, runtime_code);\n    final_output = __wear_concat(final_output, nl);\n    final_output = __wear_concat(final_output, nl);\n    final_output = __wear_concat(final_output, "/* Function Prototypes */");\n    final_output = __wear_concat(final_output, nl);\n    final_output = __wear_concat(final_output, global_protos);\n    final_output = __wear_concat(final_output, nl);\n    final_output = __wear_concat(final_output, "/* Function Definitions */");\n    final_output = __wear_concat(final_output, nl);\n    final_output = __wear_concat(final_output, global_code);\n'''
    source = replace_once(source, old_assembly, new_assembly, "prototype-aware final assembly")
    return source


def repair_runtime(source: str) -> str:
    old = '''/* Generic string/int concatenation dispatch. */\n#define __wear_concat(a, b) _Generic((b), \\\n    int: __wear_concat_str_int, \\\n    char*: __wear_concat_impl, \\\n    const char*: __wear_concat_impl \\\n)(a, b)\n'''
    new = '''/* Three-operand string concatenation helper for legacy generated code. */\nchar* __wear_concat3(const char* a, const char* b, const char* c) {\n    char* first = __wear_concat_impl(a, b);\n    char* result = __wear_concat_impl(first, c);\n    free(first);\n    return result;\n}\n\n#define __wear_concat2(a, b) _Generic((b), \\\n    int: __wear_concat_str_int, \\\n    char*: __wear_concat_impl, \\\n    const char*: __wear_concat_impl \\\n)(a, b)\n\n#define __wear_concat_pick(_1, _2, _3, NAME, ...) NAME\n#define __wear_concat(...) \\\n    __wear_concat_pick(__VA_ARGS__, __wear_concat3, __wear_concat2)(__VA_ARGS__)\n'''
    return replace_once(source, old, new, "runtime concat dispatch")


def main() -> int:
    compiler = COMPILER.read_text(encoding="utf-8")
    stage1 = STAGE1.read_text(encoding="utf-8")
    runtime = RUNTIME.read_text(encoding="utf-8")

    repaired_compiler = repair_compiler(compiler)
    repaired_stage1 = repair_stage1_source(stage1)
    repaired_runtime = repair_runtime(runtime)

    if repaired_compiler != compiler:
        COMPILER.write_text(repaired_compiler, encoding="utf-8")
        print(f"updated {COMPILER.relative_to(ROOT)}")
    else:
        print(f"unchanged {COMPILER.relative_to(ROOT)}")

    if repaired_stage1 != stage1:
        STAGE1.write_text(repaired_stage1, encoding="utf-8")
        print(f"updated {STAGE1.relative_to(ROOT)}")
    else:
        print(f"unchanged {STAGE1.relative_to(ROOT)}")

    if repaired_runtime != runtime:
        RUNTIME.write_text(repaired_runtime, encoding="utf-8")
        print(f"updated {RUNTIME.relative_to(ROOT)}")
    else:
        print(f"unchanged {RUNTIME.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
