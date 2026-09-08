# WeaR Lang M1 Architecture Notes

## Current compiler model

WeaR currently uses a transpilation model:

```text
WeaR source (.wr)
        |
        v
Stage-0 compiler (compiler.c)
        |
        v
C source (output.c)
        |
        v
native compiler (GCC/MinGW)
```

The intended bootstrap model is:

```text
compiler.c
   |
   | compiles canonical compiler.wr
   v
Stage-1 compiler
   |
   | compiles compiler.wr again
   v
Stage-2 compiler
```

M1 treats reproducibility as an explicit invariant. A successful build is not sufficient when Stage-0 and Stage-1 implement different language/compiler surfaces.

## Known drift categories

The current Stage-1 source already contains capabilities that the checked-in Stage-0 source does not implement equivalently, including import preprocessing, `input()`, `tapi_jika`, typed parameters, function prototypes, and underscore-aware identifiers.

These differences are tracked by `tools/audit_bootstrap.py` and GitHub issue #1. They must be resolved before bootstrap is promoted from an informational CI check to a required release gate.

## Design direction

The next compiler-core phase should move type decisions away from variable-name heuristics and toward explicit compiler state. Expression handling should likewise be centralized so string concatenation, integer arithmetic, comparisons, and function calls use deterministic operand/type information rather than filename or identifier naming conventions.
