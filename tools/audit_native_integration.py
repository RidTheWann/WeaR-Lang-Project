#!/usr/bin/env python3
"""Verify that the native Stage-0 path is wired to the canonical symbol table.

This audit is intentionally structural. It does not replace runtime regression
or bootstrap execution; it prevents the integration seam from silently being
bypassed while the compiler migration is still in progress.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require_text(path: Path, markers: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing required file: {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing marker {marker!r}")
    return errors


def main() -> int:
    checks = {
        ROOT / "compiler.c": (
            '#include "tools/native_symbol_table.h"',
            "wear_symbol_declare(",
            "wear_function_declare(",
            "wear_symbol_lookup_type(",
            "wear_function_lookup_return_type(",
        ),
        ROOT / "tools/native_symbol_table.h": (
            "wear_symbol_declare(",
            "wear_symbol_update_type(",
            "wear_function_declare(",
        ),
        ROOT / "tools/native_symbol_table.c": (
            "wear_symbol_lookup_type(",
            "wear_symbol_declare(",
            "wear_symbol_update_type(",
            "wear_function_declare(",
        ),
        ROOT / "tests/run_regression.sh": (
            '"$ROOT_DIR/tools/native_symbol_table.c"',
            "string_symbol_tracking",
        ),
        ROOT / "tests/cases/string_symbol_tracking.wr": (
            'var caption = "WeaR symbol tracking OK"',
            "var total = 42",
            "cetak caption",
            "cetak total",
        ),
    }

    errors: list[str] = []
    for path, markers in checks.items():
        errors.extend(require_text(path, markers))

    print("WeaR native symbol integration audit")
    print(f"Root: {ROOT}")
    print()

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print()
        print(f"Native integration audit failed with {len(errors)} issue(s).")
        return 1

    print("[OK] compiler.c consumes the native symbol/function lookup contract")
    print("[OK] mutable native declarations are available")
    print("[OK] regression runner links native_symbol_table.c")
    print("[OK] arbitrary-name string/int regression fixture is wired")
    print()
    print("Native integration audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
