# WeaR Lang — Development Progress

> Living roadmap and engineering log for the `development` branch.
> Update this file whenever a meaningful compiler, runtime, tooling, CI, documentation, or release milestone is completed.

## Current Status

**Project:** WeaR Lang

**Stable branch:** `main`

**Engineering branch:** `development`

**Feature branch:** `feature/m1-regression-hardening`

**Current phase:** M1 compiler stabilization / M2 bootstrap hardening

**Current engineering focus:** Keep Stage-0 → Stage-1 → Stage-2 reproducibility green, eliminate heuristic type decisions, and make the native regression suite pass in PR CI.

---

## Completed

### Repository & workflow
- [x] Establish `development` as the active engineering branch.
- [x] Verify GitHub read/write workflow for repository changes.
- [x] Keep `main` isolated from experimental development work.
- [x] Add repository security guidance.
- [x] Remove the tracked `rahasia.txt` test artifact from the active codebase.

### Tooling & CI
- [x] Add a native compiler regression workflow for `development` and `main`.
- [x] Add a maintainable regression runner under `tests/run_regression.sh`.
- [x] Add baseline regression cases for literals/variables, control flow, and functions.
- [x] Add repository hygiene checks for generated build artifacts and required project docs.
- [x] Add manual workflow dispatch support for CI.
- [x] Add a structural Stage-0/Stage-1 capability audit under `tools/audit_bootstrap.py`.
- [x] Make bootstrap capability drift visible in CI without turning the known M1 mismatch into a false-green release gate.
- [x] Strengthen the bootstrap audit so Stage-0 and Stage-1 requirements are checked bidirectionally.
- [x] Add an isolated multi-stage bootstrap runner for Stage-0 → Stage-1 → Stage-2 reproducibility checks.
- [x] Add a dedicated bootstrap workflow for feature branches and pull requests into `development`.
- [x] Add complete diagnostics when a bootstrap compiler stage fails to build.
- [x] Fix the isolated regression harness so Stage-0 receives its required `runtime.c` dependency.
- [x] Restrict PR/test workflow permissions to read-only repository access; write access is limited to the feature-push self-repair job.
- [x] Document the development/stable branch model.

### Compiler core
- [x] Extend Stage-0 string-return detection for `input()` and `process_imports()`.
- [x] Make Stage-0 user-function return type generation consult `returns_string()` instead of hard-coding `int`.
- [x] Upgrade the legacy embedded Stage-0 string concatenation helper to accept both two- and three-operand generated calls.
- [x] Align the standalone runtime concatenation dispatcher with the legacy three-operand compatibility path.
- [x] Add typed parameter support for the current self-hosted compiler surface (`: int` / `: str`).
- [x] Add deterministic function prototype generation to Stage-0 output.

### Runtime
- [x] Harden string allocation and concatenation against null inputs and size overflow.
- [x] Harden file reads/writes with seek, size, and I/O error checks.
- [x] Replace the fixed-size input buffer with dynamically growing input storage.
- [x] Improve runtime error reporting for allocation and I/O failures.

### Documentation
- [x] Improve README guidance for the native compiler workflow.
- [x] Create this persistent progress tracker.
- [x] Document the bootstrap contract and release gate policy.
- [x] Record the current Stage-0/Stage-1 synchronization blocker as GitHub issue #1.
- [x] Document the M1 feature-branch validation workflow.
- [x] Document the current compiler architecture and Stage-0/Stage-1 drift model.
- [x] Formalize the repository branching policy.

### Regression surface
- [x] Add deferred coverage fixtures for string concatenation, typed parameters, `tapi_jika`, `input()`, and imports.
- [x] Document the distinction between active baseline tests and deferred compiler-surface tests.

---

## In Progress

### Compiler core
- [ ] Audit remaining compiler.c/compiler.wr semantic drift.
- [ ] Replace heuristic string-type detection with explicit compiler symbol/type tracking.
- [ ] Fix remaining `cetak` type dispatch edge cases.
- [ ] Improve expression parsing and operator handling.
- [ ] Improve diagnostics with source line/column information.
- [ ] Validate malformed syntax without crashing or generating invalid C.

### Self-hosting
- [x] Capture a real reproducible Stage-0 → Stage-1 → Stage-2 result.
- [ ] Prove reproducibility across multiple consecutive CI runs.
- [ ] Add automated comparison of generated compiler output between bootstrap stages.
- [ ] Reduce reliance on generated/manual synchronization between `compiler.c` and `compiler.wr`.
- [ ] Re-enable self-hosting as a required CI gate after the native regression surface is stable.

### Testing
- [ ] Verify the complete native regression suite in GitHub Actions.
- [ ] Promote string concatenation into active CI after deterministic type handling is complete.
- [ ] Promote typed functions, `tapi_jika`, `input()`, and imports after Stage-0 synchronization.
- [ ] Add tests for arrays and broader collection behavior.
- [ ] Add negative tests for syntax/type errors.
- [ ] Add generated-C compilation tests with a strict warning policy.

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
8. **PR/test workflows should default to read-only permissions.**

## Branch Policy

- `main` is stable-only.
- `development` is the integration branch for completed engineering work.
- Short-lived feature branches may be created from `development` and must target `development` for review.
- Never create experimental branches from `main`.

---

## Milestones

### M0 — Repository Stabilization
- [x] Development branch workflow
- [x] Basic CI/regression coverage
- [x] Security/repository hygiene baseline
- [ ] Clean documentation baseline

### M1 — Compiler Core Stabilization
- [ ] Compiler/parser audit
- [ ] Deterministic type handling
- [ ] Diagnostics with line/column
- [ ] Regression suite verified in CI
- [x] Bootstrap capability drift is observable and tracked
- [x] Stage-0/Stage-1 audit is bidirectional
- [x] Deferred regression surface is documented
- [x] Real multi-stage bootstrap execution is wired into CI
- [x] Bootstrap failure diagnostics expose the first Stage-1 compilation blockers
- [x] Regression workspace dependency handling fixed
- [x] Stage-0 return-type and concatenation root-cause repairs applied
- [x] Stage-0 prototype generation stabilized
- [x] A real Stage-0 → Stage-1 → Stage-2 reproducibility check passed

### M2 — Self-Hosting Hardening
- [x] First reproducible bootstrap generation pair
- [ ] Multi-generation verification
- [ ] Stage synchronization policy
- [ ] Self-hosting release gate

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
- Replaced the previous CI bootstrap smoke flow with a maintainable native regression suite while Stage-0/Stage-1 synchronization remains unresolved.
- Added regression cases for basic variables/literals, control flow, and function return behavior.
- Hardened `runtime.c` memory, input, and file-I/O handling.
- Opened GitHub issue #1 to track Stage-0/Stage-1 semantic synchronization and bootstrap reproducibility.

### 2026-09-08
- Added `tools/audit_bootstrap.py` to make Stage-0/Stage-1 capability drift measurable.
- Added `docs/bootstrap-contract.md` defining the canonical-source and release-gate bootstrap invariants.
- Added a visible CI bootstrap-audit job with non-gating behavior until Issue #1 is resolved.
- Strengthened bootstrap auditing so both Stage-0 and Stage-1 capabilities are checked explicitly.
- Created `feature/m1-regression-hardening` from `development` for the next isolated engineering batch.
- Added M1 workflow and compiler architecture documentation.
- Formalized the repository branching policy.
- Added deferred regression fixtures for string concatenation, typed parameters, `tapi_jika`, `input()`, and imports.
- Added a real multi-stage bootstrap runner and CI workflow that attempt Stage-0 → Stage-1 → Stage-2 generation and reproducibility verification.
- Made feature-branch pushes run the standard CI suite.
- Added complete Stage-1 compiler diagnostics to the bootstrap runner.
- Confirmed the first concrete Stage-1 blockers: incorrect return type generation for `process_imports` and invalid three-operand `__wear_concat(...)` generation for chained concatenation.
- Fixed the regression harness so isolated test workspaces include the runtime dependency required by Stage-0.
- Applied Stage-0 root-cause repairs for string-returning functions and legacy three-operand concatenation compatibility.
- Added typed parameter synchronization and deterministic prototype generation.
- Fixed the codemod duplicate-declaration regression and made the repair path fully idempotent.
- Achieved the first real Stage-0 → Stage-1 → Stage-2 reproducibility pass.
- Tightened GitHub Actions permissions so PR/test workflows use read-only repository access by default.
