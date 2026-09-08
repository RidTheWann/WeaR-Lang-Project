#!/usr/bin/env python3
"""CLI adapter for the canonical WeaR Lang semantic engine."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from semantic_engine import check_source


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic WeaR source semantic checker")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    failed = False
    for path in args.files:
        try:
            errors = check_source(path)
        except (OSError, UnicodeError) as exc:
            print(f"{path}: cannot read source: {exc}", file=sys.stderr)
            failed = True
            continue
        if errors:
            failed = True
            for error in errors:
                print(error, file=sys.stderr)
        else:
            print(f"PASS {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
