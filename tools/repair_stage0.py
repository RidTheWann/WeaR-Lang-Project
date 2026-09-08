#!/usr/bin/env python3
"""One-shot bootstrap cleanup for the M1 feature branch.

This codemod is intentionally narrow and fully idempotent. It repairs only
known source inconsistencies discovered by the real bootstrap test.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "compiler.c"
STAGE1 = ROOT / "compiler.wr"


def collapse_line_duplicates(source: str, exact_line: str) -> str:
    lines = source.splitlines(keepends=True)
    seen = False
    result: list[str] = []
    for line in lines:
        if line.strip() == exact_line:
            if seen:
                continue
            seen = True
        result.append(line)
    return "".join(result)


def patch_stage1(source: str) -> str:
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
        source = source.replace(
            f"fungsi {name}({param}) {{",
            f"fungsi {name}({param}: str) {{",
        )

    source = source.replace(
        'global_proto = global_proto + ");" + nl',
        'global_proto = global_proto + ");"\nglobal_proto = global_proto + nl',
    )
    source = source.replace(
        'final_output = final_output + "/* Function Prototypes */" + nl',
        'final_output = final_output + "/* Function Prototypes */"\nfinal_output = final_output + nl',
    )
    source = source.replace(
        'final_output = final_output + "/* Function Definitions */" + nl',
        'final_output = final_output + "/* Function Definitions */"\nfinal_output = final_output + nl',
    )
    return source


def patch_stage0(source: str) -> str:
    return collapse_line_duplicates(source, 'char* global_protos = "";')


def main() -> int:
    if not COMPILER.is_file() or not STAGE1.is_file():
        raise SystemExit("repair_stage0: compiler.c and compiler.wr are required")

    compiler = COMPILER.read_text(encoding="utf-8")
    stage1 = STAGE1.read_text(encoding="utf-8")

    repaired_compiler = patch_stage0(compiler)
    repaired_stage1 = patch_stage1(stage1)

    if repaired_compiler != compiler:
        COMPILER.write_text(repaired_compiler, encoding="utf-8")
        print("updated compiler.c")
    else:
        print("unchanged compiler.c")

    if repaired_stage1 != stage1:
        STAGE1.write_text(repaired_stage1, encoding="utf-8")
        print("updated compiler.wr")
    else:
        print("unchanged compiler.wr")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
