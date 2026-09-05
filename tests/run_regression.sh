#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

CC="${CC:-gcc}"
CFLAGS="${CFLAGS:--std=c11 -Wall -Wextra -O2 -Wno-unused-parameter}"

printf '%s\n' '[1/3] Building Stage-0 compiler...'
$CC $CFLAGS "$ROOT_DIR/compiler.c" -o "$WORK_DIR/wear-stage0"

run_case() {
    local case_name="$1"
    local expected="$2"

    printf '  - %-16s' "$case_name"
    rm -f "$WORK_DIR/input.wr" "$WORK_DIR/output.c" "$WORK_DIR/program" "$WORK_DIR/program.out"

    cp "$ROOT_DIR/tests/cases/${case_name}.wr" "$WORK_DIR/input.wr"
    (
        cd "$WORK_DIR"
        ./wear-stage0 >/dev/null
        test -s output.c
        $CC $CFLAGS output.c -o program
        ./program > program.out
    )

    diff -u <(printf '%s\n' "$expected") "$WORK_DIR/program.out"
    printf '%s\n' 'PASS'
}

printf '%s\n' '[2/3] Running compiler regression cases...'
run_case basic $'WeaR Lang regression: basic OK\n42'
run_case control_flow $'3\n2\n1\nWeaR Lang regression: control OK'
run_case functions '42'

printf '%s\n' '[3/3] Regression suite passed.'
