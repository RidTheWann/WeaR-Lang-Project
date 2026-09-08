# WeaR Lang — Multilingual Frontend

WeaR Lang treats human-language syntax as a frontend concern. The compiler backend should operate on one canonical semantic language instead of maintaining a separate compiler implementation for every locale.

## Current implementation

`tools/localization.py` normalizes supported localized keywords before semantic analysis and legacy Stage-0 transpilation.

Current dialects:

- `id` — canonical Indonesian keyword spelling.
- `en` — English aliases normalized to the canonical spelling.
- `auto` — accepts the union of currently supported English and canonical Indonesian keywords.

Examples:

```text
function greet(name) { return "Hello " + name }
```

becomes:

```text
fungsi greet(name) { kembalikan "Hello " + name }
```

Likewise:

```text
if (ready) {
    print "OK"
} else {
    print "WAIT"
}
```

becomes:

```text
jika (ready) {
    cetak "OK"
} lainnya {
    cetak "WAIT"
}
```

## Preservation rule

Normalization is token-aware. It rewrites identifier-like tokens only outside quoted strings and `//` comments. This prevents localized keyword text inside user strings or comments from being altered.

## Compiler pipeline

```text
localized WeaR source
        |
        v
 tools/localization.py
        |
        v
canonical WeaR dialect
        |
        +--> semantic_contract.py
        |
        +--> semantic_frontend.py
        |
        v
 legacy Stage-0 backend
        |
        v
 generated C
        |
        v
 native toolchain
```

## Long-term direction

The current normalizer is a compatibility frontend while the self-hosted compiler is being migrated toward an explicit token/parser/AST architecture. Future locales should extend the frontend mapping rather than duplicate compiler semantics.

Adding a new human language should therefore primarily involve a locale definition and, where necessary, locale-specific lexical rules. The semantic core, type system, IR, optimization passes, and native backends must remain language-neutral.
