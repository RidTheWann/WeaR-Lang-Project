# WeaR Lang Tests

The regression suite is split into two categories.

## Active baseline

`run_regression.sh` executes cases that the current Stage-0 compiler can compile deterministically:

- `basic.wr`
- `control_flow.wr`
- `functions.wr`

## Deferred compiler-surface cases

Some cases are checked into the repository before they become active CI cases. They document language behavior that must be supported once the compiler-core work is complete.

Currently deferred:

- `string_concat.wr` — deterministic string-type tracking and concatenation

A deferred case must not be marked active until Stage-0 and Stage-1 agree on its behavior and the generated C is warning-clean.
