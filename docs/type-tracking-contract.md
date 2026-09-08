# WeaR Lang — Deterministic Symbol/Type Tracking Contract

## Purpose

Stage-0 currently contains a legacy `is_string_varname()` heuristic. That is useful as a bootstrap-era fallback, but it is not a semantic type system: a variable's C type can change merely because its name changes.

The next compiler-core change must replace that decision with explicit symbol/type state while keeping `compiler.c` (Stage-0) and `compiler.wr` (Stage-1) behavior synchronized.

## Required semantics

For the current `var name = expression` surface, the compiler must record at least:

- `name -> str` when the initializer is a string literal.
- `name -> int` when the initializer is an integer literal.
- `name -> str` when the initializer is a known string-returning function.
- `name -> int` when the initializer is a known integer-returning function.

`cetak name` must consult recorded type information before any legacy naming fallback.

## Scope of the first implementation

The first implementation is deliberately small:

1. Track declaration type in the compiler while scanning one source file.
2. Use exact variable names with a delimiter-safe representation so `x` cannot match `xx`.
3. Prefer explicit tracked type over `is_string_varname()`.
4. Keep the legacy heuristic only as a temporary fallback for compiler-internal identifiers that predate the symbol table.
5. Do not claim general lexical scoping, reassignment typing, or expression inference until those behaviors have their own tests.

## Non-goals for this increment

This change does not attempt to redesign the parser, introduce heap-allocated AST nodes, or make the entire language statically typed. It is a narrow semantic correction for the current declaration/print pipeline.

## Acceptance criteria

The deferred fixture `tests/cases/string_symbol_tracking.wr` must compile and print, in order:

```text
WeaR symbol tracking OK
42
deterministic
7
```

The fixture is intentionally not part of the baseline regression suite until both Stage-0 and Stage-1 are synchronized and the bootstrap check passes with it available.

## Synchronization rule

Any semantic addition made to `compiler.c` must have an equivalent implementation in `compiler.wr`, and the resulting Stage-0 -> Stage-1 -> Stage-2 bootstrap must remain reproducible.
