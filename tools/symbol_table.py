#!/usr/bin/env python3
"""Deterministic scoped symbol table for the WeaR Lang frontend.

This is the migration seam toward native compiler symbol tracking. It keeps
variable identifiers separate from primitive type information and also models
the separate function namespace that the native compiler must preserve.
"""

from __future__ import annotations

from dataclasses import dataclass

from semantic_contract import FunctionSignature, INT, STR, UNKNOWN


@dataclass(frozen=True)
class Symbol:
    name: str
    type_name: str
    line: int
    scope: str
    internal_name: str = ""


@dataclass(frozen=True)
class FunctionSymbol:
    name: str
    signature: FunctionSignature
    line: int


class SymbolTable:
    """A deterministic global/local variable and function symbol table."""

    def __init__(self) -> None:
        self._scopes: dict[str, dict[str, Symbol]] = {"global": {}}
        self._functions: dict[str, FunctionSymbol] = {}

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

    def declare_function(
        self,
        name: str,
        signature: FunctionSignature,
        *,
        line: int | None = None,
    ) -> FunctionSymbol:
        symbol = FunctionSymbol(name, signature, line if line is not None else signature.line)
        self._functions[name] = symbol
        return symbol

    def resolve(self, name: str, *, scope: str = "global") -> Symbol | None:
        local = self._scopes.get(scope, {})
        if name in local:
            return local[name]
        return self._scopes.get("global", {}).get(name)

    def resolve_function(self, name: str) -> FunctionSymbol | None:
        return self._functions.get(name)

    def update_type(self, name: str, type_name: str, *, scope: str = "global") -> Symbol | None:
        if type_name not in {INT, STR, UNKNOWN}:
            raise ValueError(f"unsupported symbol type: {type_name}")
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

    def functions(self) -> dict[str, FunctionSymbol]:
        return dict(self._functions)


__all__ = ["FunctionSymbol", "Symbol", "SymbolTable"]
