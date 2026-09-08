#!/usr/bin/env python3
"""Audit the checked-in Stage-0/Stage-1 bootstrap contract.

The self-hosted compiler in ``compiler.wr`` is the canonical language/compiler
source. ``compiler.c`` is the native Stage-0 bootstrap implementation and must
support every construct required to compile the canonical source.

The capability list lives in ``tools/bootstrap_contract.json`` so the audit is
extensible without changing the Python implementation for every new feature.
The audit is intentionally structural, not semantic: real bootstrap execution
remains the authoritative check once the Stage-0 implementation catches up.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "tools" / "bootstrap_contract.json"


def read_contract() -> dict[str, Any]:
    try:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read bootstrap contract: {exc}") from exc

    if not isinstance(data, dict):
        raise RuntimeError("bootstrap contract must be a JSON object")
    if data.get("version") != 1:
        raise RuntimeError("unsupported bootstrap contract version")
    if data.get("canonical_source") != "compiler.wr":
        raise RuntimeError("canonical_source must be compiler.wr")
    if data.get("stage0_source") != "compiler.c":
        raise RuntimeError("stage0_source must be compiler.c")
    if not isinstance(data.get("checks"), list) or not data["checks"]:
        raise RuntimeError("bootstrap contract must contain a non-empty checks list")
    return data


def has_all(source: str, markers: list[str]) -> bool:
    return all(marker in source for marker in markers)


def main() -> int:
    stage0_path = ROOT / "compiler.c"
    stage1_path = ROOT / "compiler.wr"

    if not stage0_path.is_file() or not stage1_path.is_file():
        print("error: compiler.c and compiler.wr must both exist")
        return 2

    try:
        contract = read_contract()
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 2

    stage0 = stage0_path.read_text(encoding="utf-8")
    stage1 = stage1_path.read_text(encoding="utf-8")

    print("WeaR bootstrap capability audit")
    print(f"Contract: {CONTRACT.relative_to(ROOT)}")
    print(f"Stage-0: {stage0_path.relative_to(ROOT)}")
    print(f"Stage-1: {stage1_path.relative_to(ROOT)}")
    print()

    drift = 0
    for raw_check in contract["checks"]:
        if not isinstance(raw_check, dict):
            print("[INVALID] contract entry is not an object")
            drift += 1
            continue

        name = raw_check.get("name")
        stage0_markers = raw_check.get("stage0")
        stage1_markers = raw_check.get("stage1")

        if (
            not isinstance(name, str)
            or not isinstance(stage0_markers, list)
            or not all(isinstance(item, str) for item in stage0_markers)
            or not isinstance(stage1_markers, list)
            or not all(isinstance(item, str) for item in stage1_markers)
        ):
            print("[INVALID] malformed contract entry")
            drift += 1
            continue

        present0 = has_all(stage0, stage0_markers)
        present1 = has_all(stage1, stage1_markers)

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
            f"[{state}] {name}: "
            f"Stage-0={'yes' if present0 else 'no'}, "
            f"Stage-1={'yes' if present1 else 'no'}"
        )

        if not present0:
            print(
                "       Stage-0 markers required: "
                + ", ".join(repr(item) for item in stage0_markers)
            )
        if not present1:
            print(
                "       Stage-1 markers required: "
                + ", ".join(repr(item) for item in stage1_markers)
            )

    print()
    if drift:
        print(f"Bootstrap audit detected {drift} contract issue(s).")
        print("Stage-0 must catch up with the canonical Stage-1 compiler before bootstrap becomes a hard CI gate.")
        return 1

    print("Bootstrap capability audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
