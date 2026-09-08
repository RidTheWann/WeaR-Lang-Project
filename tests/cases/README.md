# Regression case policy

The canonical baseline is intentionally small until Stage-0 and Stage-1 are synchronized.

## Active

- `basic.wr`
- `control_flow.wr`
- `functions.wr`

## Deferred / compatibility surface

These cases describe capabilities already present or intended in the canonical Stage-1 compiler but not yet safe to promote into the Stage-0 baseline:

- `string_concat.wr`
- `typed_function.wr`
- `else_if.wr`
- `input.wr`
- `imports/main.wr`

The test runner must not silently skip such cases. They remain visible fixtures until their behavior is made deterministic and promoted into active CI coverage.
