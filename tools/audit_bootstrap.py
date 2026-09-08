#!/usr/bin/env python3
"""Audit the checked-in Stage-0/Stage-1 bootstrap contract.

The self-hosted compiler in ``compiler.wr`` is the canonical language/compiler
source. ``compiler.c`` is the native Stage-0 bootstrap implementation and must
support every construct needed to compile the canonical source.

This audit is intentionally structural, not semantic. It makes drift visible
and deterministic in CI without pretending that the current compiler pair is
already bootstrap-safe.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE0 = ROOT / "compiler.c"
STAGE1 = ROOT / "compiler.wr"


@dataclass(frozen=True)
class ContractCheck:
    name: str
    stage0_markers: tuple[str, ...]
    stage1_markers: tuple[str, ...]


CHECKS = (
    ContractCheck(
        "import preprocessing",
        ("process_imports",),
        ("process_imports", "impor"),
    ),
    ContractCheck(
        "runtime input builtin",
        ("__wear_input",),
        ("__wear_input", "input"),
    ),
    ContractCheck(
        "else-if keyword",
        ('"tapi_jika"', "else if"),
        ('"tapi_jika"', "tapi_jika"),
    ),
    ContractCheck(
        "function prototypes",
        ("Function Prototypes", "global_protos"),
        ("global_protos", "global_proto"),
    ),
    ContractCheck(
        "typed parameter syntax",
        (': int', ': str'),
        (": int", ": str", "ctype_str"),
    ),
    ContractCheck(
        "underscore-aware identifiers",
        ('"_"',),
        ('"_"',),
    ),
    ContractCheck(
        "runtime file reader",
        ("__wear_read_file",),
        ("baca_file",),
    ),
    ContractCheck(
        "runtime file writer",
        ("__wear_write_file",),
        ("tulis_file",),
    ),
    ContractCheck(
        "string comparison",
        ("__wear_streq",),
        ("sama",),
    ),
    ContractCheck(
        "newline runtime helper",
        ("__wear_newline_char",),
        ("newline_char",),
    ),
)


def has_all(source: str, markers: tuple[str, ...]) -> bool:
    return all(marker in source for marker in markers)


def main() -> int:
    if not STAGE0.is_file() or not STAGE1.is_file():
        print("error: compiler.c and compiler.wr must both exist")
        return 2

    stage0 = STAGE0.read_text(encoding="utf-8")
    stage1 = STAGE1.read_text(encoding="utf-8")

    print("WeaR bootstrap capability audit")
    print(f"Stage-0: {STAGE0.relative_to(ROOT)}")
    print(f"Stage-1: {STAGE1.relative_to(ROOT)}")
    print()

    drift = 0
    for check in CHECKS:
        present0 = has_all(stage0, check.stage0_markers)
        present1 = has_all(stage1, check.stage1_markers)

        if present0 and present1:
            state = "OK"
        elif present1 and not present0:
            state = "DRIFT"
            drift += 1
        elif present0 and not present1:
            state = "INCOMPLETE"
            drift += 1
        else:
            state = "MISSING"
            drift += 1

        print(
            f"[{state}] {check.name}: "
            f"Stage-0={'yes' if present0 else 'no'}, "
            f"Stage-1={'yes' if present1 else 'no'}"
        )

        if not present0:
            print(f"       Stage-0 markers required: {', '.join(repr(x) for x in check.stage0_markers)}")
        if not present1:
            print(f"       Stage-1 markers required: {', '.join(repr(x) for x in check.stage1_markers)}")

    print()
    if drift:
        print(f"Bootstrap audit detected {drift} contract issue(s).")
        print("Stage-0 must catch up with the canonical Stage-1 compiler before bootstrap becomes a hard CI gate.")
        return 1

    print("Bootstrap capability audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
