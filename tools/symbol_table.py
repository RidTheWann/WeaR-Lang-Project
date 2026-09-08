#!/usr/bin/env python3
"""Deterministic scoped symbol table for the WeaR Lang frontend.

This is the migration seam toward native compiler symbol tracking.  It keeps
identifier spelling completely separate from primitive type information and
provides the same lookup order the future self-hosted compiler must implement:
local function scope, then global scope.
"""

from __future__ import annotations

from dataclasses import dataclass

from semantic_contract import INT, STR, UNKNOWN


@dataclass(frozen=True)
class Symbol:
    name: str
    type_name: str
    line: int
    scope: str
    internal_name: str = ""


class SymbolTable:
    """A small deterministic global/local symbol table."""

    def __init__(self) -> None:
        self._scopes: dict[str, dict[str, Symbol]] = {"global": {}}

    def ensure_scope(self, scope: str) -> None:
        self._scopes.setdefault(scope, {})

    def declare(
        self,
        name: str,
        type_name: str,
        *,
        line: int,
        scope: str = "global",
        internal_name: str = "",
    ) -> Symbol:
        if type_name not in {INT, STR, UNKNOWN}:
            raise ValueError(f"unsupported symbol type: {type_name}")
        self.ensure_scope(scope)
        symbol = Symbol(name, type_name, line, scope, internal_name)
        self._scopes[scope][name] = symbol
        return symbol

    def resolve(self, name: str, *, scope: str = "global") -> Symbol | None:
        local = self._scopes.get(scope, {})
        if name in local:
            return local[name]
        return self._scopes.get("global", {}).get(name)

    def update_type(self, name: str, type_name: str, *, scope: str = "global") -> Symbol | None:
        symbol = self.resolve(name, scope=scope)
        if symbol is None:
            return None
        self._scopes[symbol.scope][name] = Symbol(
            symbol.name,
            type_name,
            symbol.line,
            symbol.scope,
            symbol.internal_name,
        )
        return self._scopes[symbol.scope][name]

    def symbols(self, scope: str = "global") -> dict[str, Symbol]:
        return dict(self._scopes.get(scope, {}))

    def visible(self, scope: str = "global") -> dict[str, Symbol]:
        result = dict(self._scopes.get("global", {}))
        if scope != "global":
            result.update(self._scopes.get(scope, {}))
        return result


__all__ = ["Symbol", "SymbolTable"]
