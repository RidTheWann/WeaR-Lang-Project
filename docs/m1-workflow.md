# M1 Engineering Workflow

This document defines how M1 compiler hardening is developed without destabilizing `main`.

## Branch flow

```text
development
    |
    +--> feature/*
             |
             +--> pull request --> development
                                      |
                                      +--> stable release --> main
```

Feature work starts from `development`. The feature branch is disposable and is never treated as a release branch.

## Required validation

Before a feature branch is merged into `development`:

1. Native regression tests must pass.
2. Repository-hygiene checks must pass.
3. Bootstrap capability audit must be reviewed.
4. Any known Stage-0/Stage-1 drift must remain explicitly tracked.
5. Generated binaries and compiler output must remain untracked.

## Bootstrap policy

`compiler.wr` is the canonical self-hosted compiler source. `compiler.c` is the Stage-0 bootstrap compiler. Self-hosting is not considered release-safe until Stage-0 can compile the canonical Stage-1 source and consecutive bootstrap generations are reproducible.

Until that point, the bootstrap audit is intentionally visible but non-gating.

## Current feature batch

`feature/m1-regression-hardening` is branched from `development` and contains the M1 regression/audit hardening work. Its target is `development`, not `main`.
