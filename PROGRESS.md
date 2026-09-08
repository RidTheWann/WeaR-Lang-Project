# WeaR Lang — Development Progress

> Living roadmap and engineering log for the `development` branch.
> Update this file whenever a meaningful compiler, runtime, tooling, CI, documentation, or release milestone is completed.

## Current Status

**Project:** WeaR Lang

**Stable branch:** `main`

**Engineering branch:** `development`

**Feature branch:** `feature/m1-type-system`

**Current phase:** M1 compiler stabilization / M2 bootstrap hardening

**Current engineering focus:** Finish compiler/runtime/tooling implementation first. Testing and release-gate promotion happen after the planned engineering changes are substantially complete.

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
- [x] Restrict PR/test workflow permissions to read-only repository access.
- [x] Document the development/stable branch model.
- [x] Add an explicit opt-in `WEAR_RUN_DEFERRED=1` mode for exercising semantic regression fixtures without weakening the baseline suite.
- [x] Add deterministic semantic static checks independent of compiler naming heuristics.
- [x] Add `tools/wear.py`, a portable command-line frontend with compile/run/version support and explicit input/output paths.
- [x] Add a semantic compatibility frontend that lowers typed variables to deterministic backend-safe identifiers before Stage-0 transpilation.
- [x] Add localized frontend normalization for Indonesian/English source while keeping a single canonical backend dialect.

### Compiler core
- [x] Extend Stage-0 string-return detection for `input()` and `process_imports()`.
- [x] Make Stage-0 user-function return type generation consult `returns_string()` instead of hard-coding `int`.
- [x] Upgrade the legacy embedded Stage-0 string concatenation helper to accept both two- and three-operand generated calls.
- [x] Align the standalone runtime concatenation dispatcher with the legacy three-operand compatibility path.
- [x] Add typed parameter support for the current self-hosted compiler surface (`: int` / `: str`).
- [x] Add deterministic function prototype generation to Stage-0 output.
- [x] Make the canonical semantic layer preserve global-symbol visibility inside functions.
- [x] Make function return inference preserve `unknown` for no-return functions and `error` for incompatible mixed return types instead of silently defaulting to `int`.

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
- [x] Document the deterministic symbol/type-tracking contract.
- [x] Document the new CLI workflow in `README.md`.
- [x] Document the multilingual frontend architecture in `docs/multilingual-frontend.md`.

### Regression surface
- [x] Add deferred coverage fixtures for string concatenation, typed parameters, `tapi_jika`, `input()`, and imports.
- [x] Document the distinction between active baseline tests and deferred compiler-surface tests.
- [x] Add an arbitrary-name fixture for deterministic string symbol/type tracking.
- [x] Add a global-symbol visibility fixture for function semantic analysis.
- [x] Add a mixed-return fixture to prevent silent return-type fallback.

---

## In Progress

### Compiler core
- [ ] Audit remaining compiler.c/compiler.wr semantic drift.
- [ ] Replace heuristic string-type detection inside the self-hosted compiler with explicit compiler symbol/type tracking.
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
- [x] Add static semantic checking for declared variable types and `cetak` expressions.
- [ ] Hold broader testing/CI promotion until the implementation pass is complete.
- [ ] Verify the complete native regression suite in GitHub Actions.
- [ ] Promote `string_symbol_tracking` into active CI after deterministic type handling is complete.
- [ ] Promote string concatenation into active CI after deterministic type handling is complete.
- [ ] Promote typed functions, `tapi_jika`, `input()`, and imports after Stage-0 synchronization.
- [ ] Add tests for arrays and broader collection behavior.
- [ ] Add negative tests for syntax/type errors.
- [ ] Add generated-C compilation tests with a strict warning policy.

### CLI & developer experience
- [x] Design and implement a first proper CLI surface.
- [x] Support explicit input/output paths.
- [x] Add clear exit codes.
- [x] Add `--help` and `--version`.
- [x] Improve compiler command-line reporting.

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
2. **Implementation first:** complete meaningful compiler/runtime/tooling work before spending cycles on broad testing.
3. **Do not claim a feature is complete until the implementation itself is finished.**
4. **Keep `compiler.c` and `compiler.wr` behavior synchronized.**
5. **Prefer deterministic compiler logic over naming heuristics.**
6. **Do not commit secrets, local machine state, generated build artifacts, or temporary files.**
7. **After the implementation pass, run the focused and full validation suites.**
8. **Self-hosting must remain reproducible.**
9. **PR/test workflows should default to read-only permissions.**

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
- [ ] Deterministic type handling inside the self-hosted compiler
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
- [x] Deterministic semantic static-check surface added
- [x] First production-oriented CLI surface added
- [x] Semantic compatibility lowering integrated into the CLI backend path
- [x] Multilingual frontend normalization integrated into the CLI path

### M2 — Self-Hosting Hardening
- [x] First reproducible bootstrap generation pair
- [ ] Multi-generation verification
- [ ] Stage synchronization policy
- [ ] Self-hosting release gate

### M3 — Developer Tooling
- [x] First CLI foundation
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

### 2026-09-08
- Switched the engineering workflow to implementation-first mode per project direction; broad testing is deferred until the current implementation pass is substantially complete.
- Added `tools/wear.py` as the first production-oriented CLI surface with isolated build directories, explicit input/output paths, `run`, `compile`, `--help`, `--version`, and structured exit codes.
- Added `tools/semantic_contract.py` as the canonical frontend primitive type/signature layer.
- Added `tools/semantic_frontend.py` to lower typed variables to deterministic backend-safe identifiers before the legacy Stage-0 compiler.
- Integrated semantic lowering into `tools/wear.py`, so the supported CLI path no longer depends on user variable naming for string/int selection.
- Added localized frontend normalization for Indonesian and English keyword spellings while preserving strings/comments.
- Fixed semantic scope handling so functions resolve global symbols before local shadowing.
- Fixed function return inference so no-return functions remain `unknown` and incompatible mixed returns become `error` instead of silently defaulting to `int`.
- Added semantic regression fixtures for global visibility and mixed return types.
- Kept the native self-hosted compiler migration explicitly in progress; the Python semantic layer remains a compatibility bridge until `compiler.c` / `compiler.wr` receive native symbol-table tracking.

### 2026-09-06
- Added `PROGRESS.md` as the persistent development roadmap and engineering memory for WeaR Lang.
