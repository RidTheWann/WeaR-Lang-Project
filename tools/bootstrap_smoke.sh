#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

CC="${CC:-gcc}"
CFLAGS="${CFLAGS:--std=c11 -Wall -Wextra -O2 -Wno-unused-parameter}"

log() {
    printf '[bootstrap] %s\n' "$*"
}

run_stage0() {
    local compiler="$1"
    local work="$2"
    (
        cd "$work"
        "$compiler" > stage0.log 2>&1
    )
}

log "Preparing isolated bootstrap workspace"
cp "$ROOT_DIR/compiler.c" "$WORK_DIR/compiler.c"
cp "$ROOT_DIR/compiler.wr" "$WORK_DIR/compiler.wr"
cp "$ROOT_DIR/runtime.c" "$WORK_DIR/runtime.c"

log "[1/5] Building Stage-0 native compiler"
$CC $CFLAGS "$WORK_DIR/compiler.c" -o "$WORK_DIR/stage0" 2>"$WORK_DIR/stage0-build-warnings.log"
if [ -s "$WORK_DIR/stage0-build-warnings.log" ]; then
    log "Stage-0 compiler warnings detected (non-gating during M1):"
    sed 's/^/[warning] /' "$WORK_DIR/stage0-build-warnings.log"
fi

log "[2/5] Generating Stage-1 from canonical compiler.wr"
cp "$WORK_DIR/compiler.wr" "$WORK_DIR/input.wr"
if ! run_stage0 "$WORK_DIR/stage0" "$WORK_DIR"; then
    cat "$WORK_DIR/stage0.log"
    printf '\nBootstrap failed during Stage-0 -> Stage-1 generation.\n' >&2
    exit 1
fi

test -s "$WORK_DIR/output.c"
mv "$WORK_DIR/output.c" "$WORK_DIR/stage1.c"

log "[3/5] Building Stage-1 compiler"
$CC $CFLAGS "$WORK_DIR/stage1.c" -o "$WORK_DIR/stage1" 2>"$WORK_DIR/stage1-build-warnings.log"
if [ -s "$WORK_DIR/stage1-build-warnings.log" ]; then
    log "Stage-1 compiler warnings detected (non-gating during M1):"
    sed 's/^/[warning] /' "$WORK_DIR/stage1-build-warnings.log"
fi

log "[4/5] Generating Stage-2 from the same canonical compiler.wr"
cp "$WORK_DIR/compiler.wr" "$WORK_DIR/input.wr"
(
    cd "$WORK_DIR"
    ./stage1 > stage1.log 2>&1
)

test -s "$WORK_DIR/output.c"
mv "$WORK_DIR/output.c" "$WORK_DIR/stage2.c"

log "[5/5] Comparing consecutive bootstrap generations"
if ! cmp -s "$WORK_DIR/stage1.c" "$WORK_DIR/stage2.c"; then
    printf '%s\n' 'Bootstrap reproducibility failure: Stage-1 and Stage-2 outputs differ.' >&2
    diff -u "$WORK_DIR/stage1.c" "$WORK_DIR/stage2.c" || true
    exit 1
fi

log "Bootstrap reproducibility check passed."
