# WeaR Lang — Development Progress

> Living roadmap and engineering log for the `development` branch.
> Update this file whenever a meaningful compiler, runtime, tooling, CI, documentation, or release milestone is completed.

## Current Status

**Project:** WeaR Lang

**Stable branch:** `main`

**Engineering branch:** `development`

**Current phase:** Core compiler stabilization and self-hosting hardening

---

## Completed

### Repository & workflow
- [x] Establish `development` as the active engineering branch.
- [x] Verify GitHub read/write workflow for repository changes.
- [x] Keep `main` isolated from experimental development work.
- [x] Add repository security guidance.
- [x] Remove the tracked `rahasia.txt` test artifact from the active codebase.

### Tooling & CI
- [x] Add a native compiler smoke-test workflow.
- [x] Add a minimal WeaR smoke program under `tests/`.
- [x] Begin repository hygiene improvements for generated artifacts.
- [x] Document the development/stable branch model.

### Documentation
- [x] Improve README guidance for the native compiler workflow.
- [x] Create this persistent progress tracker.

---

## In Progress

### Compiler core
- [ ] Audit `compiler.c` and `compiler.wr` for semantic drift.
- [ ] Make Stage-0 and self-hosted Stage-1 behavior deterministic and reproducible.
- [ ] Improve expression parsing and operator handling.
- [ ] Replace heuristic string-type detection with explicit compiler type information.
- [ ] Improve diagnostics with source line/column information.
- [ ] Validate malformed syntax without crashing or generating invalid C.

### Self-hosting
- [ ] Prove bootstrap reproducibility across consecutive generations.
- [ ] Add automated comparison of generated compiler output between bootstrap stages.
- [ ] Reduce reliance on generated/manual synchronization between `compiler.c` and `compiler.wr`.

### Runtime
- [ ] Audit allocation ownership and temporary string lifetime.
- [ ] Harden file I/O error handling.
- [ ] Review array helpers and bounds behavior.
- [ ] Consolidate duplicated runtime helpers.

### Testing
- [ ] Expand smoke tests into a regression suite.
- [ ] Add tests for variables, arithmetic, strings, arrays, functions, conditionals, loops, imports, and input.
- [ ] Add negative tests for syntax/type errors.
- [ ] Add bootstrap/self-hosting tests.
- [ ] Add generated-C compilation tests with strict warnings.

### CLI & developer experience
- [ ] Design a proper CLI instead of relying on `input.wr`/`output.c` defaults.
- [ ] Support explicit input/output paths.
- [ ] Add clear exit codes.
- [ ] Add `--help` and `--version`.
- [ ] Improve compiler error messages and command-line reporting.

### Web playground
- [ ] Reconcile the web playground with the native language specification.
- [ ] Keep Indonesian and English syntax behavior consistent.
- [ ] Add clearer compiler/runtime error presentation.
- [ ] Add examples synchronized with the canonical language syntax.

---

## Planned Features

### Language
- [ ] Explicit primitive types.
- [ ] Safer string handling.
- [ ] Better arrays/collections.
- [ ] More complete boolean and comparison operators.
- [ ] Modular imports with deterministic path resolution.
- [ ] Standard library foundation.

### Compiler architecture
- [ ] Separate lexing, parsing, semantic analysis, and C code generation.
- [ ] Introduce an intermediate representation where practical.
- [ ] Centralize type inference/checking.
- [ ] Centralize source-location tracking.
- [ ] Make generated C portable and warning-clean.

### Quality
- [ ] Reproducible builds.
- [ ] Cross-platform CI where practical.
- [ ] Release checklist and versioning policy.
- [ ] Changelog for each stable release.

---

## Rules for Future Development

1. **Never modify `main` for experimental work.** Use `development` first.
2. **Do not claim a feature is complete until it has a test.**
3. **Keep `compiler.c` and `compiler.wr` behavior synchronized.**
4. **Prefer deterministic compiler logic over naming heuristics.**
5. **Do not commit secrets, local machine state, generated build artifacts, or temporary files.**
6. **Every major compiler change should include a regression test.**
7. **Self-hosting must remain reproducible.**

---

## Milestones

### M0 — Repository Stabilization
- [x] Development branch workflow
- [x] Basic CI smoke coverage
- [x] Security/repository hygiene baseline
- [ ] Clean documentation baseline

### M1 — Compiler Core Stabilization
- [ ] Compiler/parser audit
- [ ] Deterministic type handling
- [ ] Diagnostics with line/column
- [ ] Regression suite

### M2 — Self-Hosting Hardening
- [ ] Reproducible bootstrap
- [ ] Multi-generation verification
- [ ] Stage synchronization policy

### M3 — Developer Tooling
- [ ] Proper CLI
- [ ] Better errors
- [ ] Improved VS Code/web tooling

### M4 — Language Expansion
- [ ] Types
- [ ] Standard library
- [ ] Robust modules/imports
- [ ] Expanded collections

### M5 — v1.1 Release Candidate
- [ ] CI green
- [ ] Bootstrap verified
- [ ] Regression suite green
- [ ] Documentation complete
- [ ] Release artifacts reproducible

---

## Change Log

### 2026-09-06
- Added `PROGRESS.md` as the persistent development roadmap and engineering memory for WeaR Lang.
- Recorded repository stabilization work completed so far.
- Defined compiler, self-hosting, runtime, testing, CLI, playground, and release milestones.
