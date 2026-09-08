# M1 Bootstrap Findings

## Current reproducibility result

The real CI bootstrap runner now reaches Stage-1 generation successfully, but Stage-1 does not compile yet.

The first concrete compiler-generation blockers observed on 2026-09-08 are:

1. **String-returning function definitions are emitted with the wrong return type.**
   The generated Stage-1 source contains a `char* process_imports(char* src);` declaration while the generated function definition is emitted as `int process_imports(char* src)`. GCC correctly rejects the conflicting types.

2. **Chained string concatenation is emitted as a three-argument runtime call.**
   Expressions equivalent to `a + ";" + nl` currently become `__wear_concat(a, ";", nl)`, but the runtime concatenation primitive is defined for two operands. The code generator must construct nested concatenations instead.

## Interpretation

These failures confirm that the bootstrap harness is exercising the actual compiler pipeline rather than stopping at repository-level marker checks.

The correct fix belongs in the Stage-0/Stage-1 compiler implementation, not in a CI-only workaround. Temporary warning suppression in `tools/bootstrap_smoke.sh` is diagnostic-only and must be removed when `compiler.c` becomes warning-clean.

## Exit criteria for this finding

- Stage-1 builds successfully without code-generation type conflicts.
- Chained string concatenation compiles into valid nested runtime calls.
- Stage-1 successfully generates Stage-2.
- Stage-1 and Stage-2 are byte-identical for the canonical `compiler.wr` source.
