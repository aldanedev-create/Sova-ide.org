from __future__ import annotations

"""Nested lexical environments for variables, closures, and modules."""

from dataclasses import dataclass, field
from typing import Any

from .diagnostics import SourceSpan, SovaNameError


@dataclass(slots=True)
class Environment:
    parent: "Environment | None" = None
    values: dict[str, Any] = field(default_factory=dict)

    def define(self, name: str, value: Any) -> Any:
        self.values[name] = value
        return value

    def has_local(self, name: str) -> bool:
        return name in self.values

    def get(self, name: str, span: SourceSpan) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name, span)
        raise SovaNameError(
            f"The variable '{name}' is not defined.",
            span,
            suggestion=f"Declare it first with: let {name} = ...",
        )

    def assign(self, name: str, value: Any, span: SourceSpan) -> Any:
        if name in self.values:
            self.values[name] = value
            return value
        if self.parent:
            return self.parent.assign(name, value, span)
        raise SovaNameError(
            f"The variable '{name}' is not defined.",
            span,
            suggestion=f"Declare it first with: let {name} = ...",
        )

    def snapshot(self) -> dict[str, Any]:
        result = self.parent.snapshot() if self.parent else {}
        result.update(self.values)
        return result
