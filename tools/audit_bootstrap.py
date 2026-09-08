#!/usr/bin/env python3
"""Audit the checked-in Stage-0/Stage-1 bootstrap contract.

This is intentionally structural rather than semantic: the CI job uses it to
surface known capability drift before bootstrap verification becomes a hard
release gate.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE0 = ROOT / "compiler.c"
STAGE1 = ROOT / "compiler.wr"

REQUIRED_STAGE1_MARKERS = {
    "import preprocessing": "process_imports",
    "runtime input builtin": "input",
    "else-if keyword": "tapi_jika",
    "function prototypes": "global_protos",
    "typed parameter syntax": ": int",
    "identifier underscores": "_",
}

REQUIRED_STAGE0_MARKERS = {
    "runtime file reader": "__wear_read_file",
    "runtime file writer": "__wear_write_file",
    "string comparison": "__wear_streq",
    "newline runtime helper": "__wear_newline_char",
}


def main() -> int:
    stage0 = STAGE0.read_text(encoding="utf-8")
    stage1 = STAGE1.read_text(encoding="utf-8")

    print("WeaR bootstrap capability audit")
    print(f"Stage-0: {STAGE0.relative_to(ROOT)}")
    print(f"Stage-1: {STAGE1.relative_to(ROOT)}")
    print()

    failures = 0

    for name, marker in REQUIRED_STAGE1_MARKERS.items():
        present0 = marker in stage0
        present1 = marker in stage1
        state = "OK" if present0 else "DRIFT"
        print(f"[{state}] {name}: Stage-0={'yes' if present0 else 'no'}, Stage-1={'yes' if present1 else 'no'}")
        if not present1:
            print(f"       canonical Stage-1 marker missing: {marker!r}")
            failures += 1

    print()
    for name, marker in REQUIRED_STAGE0_MARKERS.items():
        present0 = marker in stage0
        present1 = marker in stage1
        state = "OK" if present0 and present1 else "DRIFT"
        print(f"[{state}] {name}: Stage-0={'yes' if present0 else 'no'}, Stage-1={'yes' if present1 else 'no'}")
        if not present0:
            failures += 1

    print()
    if failures:
        print(f"Bootstrap audit detected {failures} contract issue(s).")
        print("Resolve Stage-0/Stage-1 drift before making self-hosting a hard CI gate.")
        return 1

    print("Bootstrap capability audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
