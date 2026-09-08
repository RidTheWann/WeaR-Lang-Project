# WeaR Lang Bootstrap Contract

WeaR has two compiler stages:

- **Stage-0**: the checked-in native C compiler in `compiler.c`.
- **Stage-1**: the self-hosted compiler source in `compiler.wr`.

## Canonical source

`compiler.wr` is the canonical language-level implementation. `compiler.c` is a bootstrap artifact and must be capable of compiling the canonical Stage-1 source without silently dropping or changing supported language behavior.

## Required invariant

A release candidate must satisfy:

1. Stage-0 compiles with the repository's supported C toolchain.
2. Stage-0 transpiles `compiler.wr` successfully.
3. The resulting Stage-1 compiler compiles the regression suite.
4. A second bootstrap generation is byte-for-byte identical to the first generated compiler output, after any explicitly documented normalization.

## Known M1 drift

The current `development` branch is not yet considered bootstrap-reproducible. The Stage-1 source contains capabilities that are not represented consistently in the checked-in Stage-0 compiler, including import preprocessing, `input()`, `tapi_jika`, function-prototype generation, typed parameter annotations, and newer identifier handling.

This drift is tracked in GitHub Issue #1. The structural audit lives at `tools/audit_bootstrap.py` and is intentionally visible during CI while Stage-0 synchronization is being completed.

## Gate policy

The bootstrap audit may report failures during M1, but a stable release must never ship with unresolved audit failures. Once Issue #1 is closed, the audit and two-generation bootstrap comparison become required CI gates.
