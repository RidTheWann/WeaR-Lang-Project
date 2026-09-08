# WeaR Lang — Project Point / Original Vision

> Permanent project memory for the original direction of WeaR Lang.
>
> This document is based on an audit of the `main` branch at commit `ebdfe0fa769f43ed0f6edd33beff073c87bbe6c3` and the project's visible release history through v1.0, v1.1, v1.4, v1.4.1, and v1.5. It is intended to prevent future compiler work from drifting away from the project's original purpose.

## 1. The actual purpose of WeaR Lang

WeaR Lang is intended to be a **high-performance, statically compiled programming language with a Python-like level of simplicity and readability, while allowing programmers to write the language using the human language of their choice**.

The core idea is not to create an "Indonesian programming language".

Indonesian syntax is one dialect of the language. English is another. The architecture should allow additional human languages to be added without creating a separate compiler for each language.

The long-term product vision is therefore:

```text
                 WeaR Lang
                     |
          +----------+----------+
          |                     |
   Friendly syntax        Native compilation
   / human dialects       / high performance
          |                     |
          +----------+----------+
                     |
                Common Core
                     |
       Lexer / Parser / Semantics
                     |
              IR / Optimization
                     |
             Native Backend
```

## 2. Original design philosophy confirmed by project history

The project's earlier README explicitly described WeaR Lang as a **"Polyglot Programming Language"** built around the philosophy **"Low Floor, High Ceiling"**: easy for beginners, but capable enough for professional programming.

That README also defined the motivation as making programming more accessible to non-English speakers while retaining professional capabilities. It described localized keyword sets and specifically showed English and Indonesian forms such as `if` / `jika`, `function` / `fungsi`, `return` / `kembalikan`, `else` / `lainnya`, `while` / `selama`, and `print` / `cetak`.

Therefore, multilingual syntax is a **first-class design objective**, not a cosmetic feature.

## 3. Performance objective

The project evolved toward a native/static compilation model. The v1.0 release was explicitly labeled **Native**, described WeaR as a statically compiled language written in itself, and used a bootstrap compiler to generate C before compiling to a native executable with GCC/MinGW.

This establishes the implementation direction:

```text
WeaR source
    -> compiler
    -> native-oriented generated code
    -> system compiler/toolchain
    -> executable
```

The important point is that C is currently the **bootstrap/code-generation vehicle**, not the definition of what WeaR ultimately is.

The project should optimize for the runtime characteristics of compiled/native software rather than drifting into a permanently interpreter-first design.

## 4. What "Python-like" should mean for WeaR

The Python comparison is primarily about **developer experience**, not implementation technology.

WeaR should aim for:

- concise syntax;
- readable code;
- low ceremony for common tasks;
- straightforward control flow;
- approachable variable/function declarations;
- expressive standard-library APIs;
- useful diagnostics;
- a low barrier to entry for new programmers.

At the same time, the compiler must preserve the properties expected from a serious compiled language:

- deterministic semantics;
- explicit type information where required;
- strong semantic checking;
- predictable memory behavior;
- optimization opportunities;
- native execution;
- reproducible compilation;
- scalable compiler architecture.

## 5. Multilingual syntax architecture

Localization should happen in the **frontend language layer**, not by duplicating the backend compiler.

Conceptually:

```text
English source      Indonesian source      Other language source
      |                    |                       |
      +--------------------+-----------------------+
                           |
                    canonical tokens/AST
                           |
                    semantic analysis
                           |
                         IR/core
                           |
                    optimization/codegen
                           |
                    native executable
```

For example:

```text
English:      function greet(name) { return ... }
Indonesian:   fungsi sapa(nama) { kembalikan ... }
```

Both should converge to the same internal language semantics.

A new locale must therefore be mostly a **keyword/syntax mapping problem**, not a fork of the compiler backend.

## 6. The compiler must have a language core independent of wording

The compiler must never derive semantics from superficial spelling conventions such as variable names.

Bad architecture:

```text
name == "message"  -> probably string
name == "count"    -> probably integer
```

Correct architecture:

```text
source
  -> tokens
  -> AST
  -> symbol table
  -> declared/inferred type
  -> semantic checks
  -> IR
  -> code generation
```

This is why the current type-system work matters to the original vision. The removal of `is_string_varname()`-style heuristics is not a minor cleanup; it is a prerequisite for a language that is supposed to be deterministic, multilingual, and compiler-grade.

## 7. Self-hosting is part of the language's identity

The project already contains two compiler generations:

- `compiler.c` — Stage-0 native/bootstrap compiler;
- `compiler.wr` — Stage-1 self-hosted compiler written in WeaR.

The intended direction is:

```text
Stage-0
  |
  | compiles compiler.wr
  v
Stage-1
  |
  | compiles compiler.wr
  v
Stage-2
  |
  v
repeatable compiler generations
```

Self-hosting is important because it demonstrates that WeaR is capable of expressing and building a compiler substantial enough to define itself.

It should therefore be treated as an architectural milestone, not merely a build trick.

## 8. Historical feature progression observed on `main`

The release history shows a clear progression of language capability:

### v1.0 — Native / Self-hosted foundation

The project moved from the earlier high-level/polyglot description to a native, statically compiled release. The Stage-0 compiler and generated C path became the active implementation foundation.

### v1.1 — User input and strings

The compiler added the `input()` builtin and continued improving string concatenation. Runtime input support was added through a native C helper.

### v1.4 — Strong typing and annotations

The compiler introduced explicit parameter type annotations such as `: int` and `: str`. The same release line also added recursive import preprocessing, array runtime support, and additional compiler/runtime infrastructure.

### v1.4.1 — Forward declarations / multi-buffer generation

The compiler introduced a separate prototype buffer and improved generated function placement, allowing functions to be called before their definitions.

### v1.5 — Advanced control flow

The language gained `tapi_jika` for `else if`-style control flow and identifier scanning was extended to support underscores.

Together, these releases show that the project was moving toward a more complete compiled language rather than remaining a small scripting toy.

## 9. Current implementation architecture inherited from `main`

The audited main branch contains these important pieces:

- `compiler.c` — large Stage-0 bootstrap/transpiler implementation;
- `compiler.wr` — self-hosted compiler source;
- `runtime.c` — native runtime helpers for strings, arrays, I/O, and printing;
- `build_v1.bat` — Windows bootstrap/build workflow;
- `examples/*.wr` — language examples covering basic syntax, control flow, arrays, input, types, and modular/import usage;
- `docs/index.html` and `docs/wear-web.js` — browser playground implementation;
- `archive/stage0_bootstrap/` — historical bootstrap artifacts.

The main branch also contains generated/demo C files from the native workflow. These are useful historical artifacts but should not be confused with the canonical language source.

## 10. What the project should become

The final architecture should move beyond a large source-scanning/transpilation script and converge on a real compiler pipeline:

```text
                WeaR source
                     |
                     v
                Localization
                  frontend
                     |
                     v
                   Lexer
                     |
                     v
                  Parser
                     |
                     v
                   AST
                     |
                     v
             Semantic analysis
             / symbol table
             / type system
                     |
                     v
                    IR
                     |
               Optimization
                     |
                     v
             Native code generation
                     |
           +---------+---------+
           |                   |
        C backend        future native backends
           |
           v
      system toolchain
           |
           v
       executable
```

C can remain a practical bootstrap backend while the compiler architecture becomes backend-independent.

## 11. Performance direction

The project should measure performance against **native compiled-language workloads**, not only against interpreter execution.

The long-term objective is to make WeaR suitable for real software where performance matters while keeping the source language approachable.

Performance work should eventually cover:

- optimized generated code;
- efficient primitive operations;
- efficient string handling;
- predictable memory management;
- low-overhead function calls;
- better data structures and collections;
- compiler optimization passes;
- release builds with reproducible toolchains;
- benchmarks against appropriate compiled-language baselines.

The phrase "performance like C++" should be treated as a **design target / ambition**, not as a claim that the current implementation already achieves equivalent performance.

## 12. What must never happen

Future development must not reduce WeaR to any of these narrower interpretations:

```text
WeaR = Indonesian-only language
WeaR = Python interpreter clone
WeaR = C code generator with cosmetic syntax
WeaR = collection of unrelated localized keywords
WeaR = compiler that guesses types from variable names
```

Those directions would lose the central purpose of the project.

## 13. Non-negotiable principles for future engineering

1. **Native-first execution model.** WeaR should remain fundamentally a compiled language.
2. **Python-like usability.** Keep the source language concise and approachable.
3. **Polyglot frontend.** Human-language syntax belongs at the frontend layer.
4. **One semantic core.** Different language dialects must compile to equivalent semantics.
5. **Deterministic types.** Never use identifier spelling as a substitute for semantic type information.
6. **Self-hosting.** `compiler.wr` must remain capable of defining/building the compiler itself.
7. **Compiler correctness before cosmetic features.** Parsing, semantic analysis, type checking, code generation, and diagnostics take priority over superficial syntax expansion.
8. **Backend independence.** C is a current/bootstrap backend, not the conceptual limit of the language.
9. **Performance must be measurable.** Native-performance ambitions eventually require benchmarks and optimization data.
10. **Language evolution must preserve the core vision.** New features should make WeaR more capable without making it less simple.

## 14. Current engineering consequence

The current M1 work should therefore be understood as **foundation work for the original WeaR vision**.

The immediate priority is to replace heuristic compiler behavior with real semantic state, including symbol/type tracking, deterministic expression handling, reliable diagnostics, and synchronized Stage-0/Stage-1 behavior.

After that foundation is solid, the project can responsibly advance toward:

```text
stable semantic core
        -> complete self-hosting
        -> canonical IR
        -> optimization
        -> native performance work
        -> scalable multilingual frontend system
        -> mature tooling / standard library
        -> production-ready WeaR ecosystem
```

## 15. Historical evidence used for this document

The audit was performed against the repository's `main` branch and its visible release history.

Key historical evidence includes:

- main HEAD `ebdfe0f` — `Feat: Release v1.5 (Advanced Control Flow - Else If)`;
- v1.4 — `Feat: Release v1.4 (Strong Typing & Type Annotations)`;
- v1.4.1 — `Fix: Release v1.4.1 (Forward Declarations & Triple-Buffer Output)`;
- v1.1 — `Feat: Release v1.1 (User Input & String Concat Fix)`;
- v1.0 — `Release: WeaR Lang v1.0 (Clean & Self-Hosted)`;
- the earlier v1.0-era README text describing WeaR as a **Polyglot Programming Language** with **Low Floor, High Ceiling** philosophy and localized English/Indonesian syntax.

This file is a project-memory document. It records the intended direction so that future implementation decisions can be evaluated against the original purpose instead of only against the latest temporary compiler architecture.
