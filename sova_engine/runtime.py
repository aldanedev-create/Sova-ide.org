from __future__ import annotations

"""Runtime values for Sova functions, classes, instances, modules, and ranges."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from .ast_nodes import FunctionNode, Parameter
from .environment import Environment

if TYPE_CHECKING:
    from .interpreter import Interpreter


@dataclass(slots=True)
class SovaRange:
    start: int
    end: int

    def values(self) -> range:
        step = 1 if self.end >= self.start else -1
        return range(self.start, self.end + step, step)

    def __iter__(self):
        return iter(self.values())


@dataclass(slots=True)
class SovaFunction:
    declaration: FunctionNode
    closure: Environment
    bound_self: "SovaInstance | None" = None

    @property
    def name(self) -> str:
        return self.declaration.name or "<function>"

    def bind(self, instance: "SovaInstance") -> "SovaFunction":
        return SovaFunction(self.declaration, self.closure, instance)

    def __repr__(self) -> str:
        return f"<function {self.name}>"


@dataclass(slots=True)
class SovaNativeFunction:
    name: str
    function: Callable[..., Any]

    def __repr__(self) -> str:
        return f"<native {self.name}>"


@dataclass(slots=True)
class SovaClass:
    name: str
    constructor_parameters: list[Parameter]
    methods: dict[str, SovaFunction]
    superclass: "SovaClass | None" = None

    def find_method(self, name: str) -> SovaFunction | None:
        if name in self.methods:
            return self.methods[name]
        return self.superclass.find_method(name) if self.superclass else None

    def __repr__(self) -> str:
        return f"<class {self.name}>"


@dataclass(slots=True)
class SovaInstance:
    klass: SovaClass
    fields: dict[str, Any] = field(default_factory=dict)

    def get(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        method = self.klass.find_method(name)
        if method:
            return method.bind(self)
        raise AttributeError(name)

    def set(self, name: str, value: Any) -> Any:
        self.fields[name] = value
        return value

    def __repr__(self) -> str:
        return f"<{self.klass.name} instance>"


@dataclass(slots=True)
class SovaModule:
    name: str
    exports: dict[str, Any]

    def __getattr__(self, name: str) -> Any:
        if name in self.exports:
            return self.exports[name]
        raise AttributeError(name)

    def __repr__(self) -> str:
        return f"<module {self.name}>"


# Public runtime value names for the 0.1v specification. Host primitives are
# intentionally reused instead of wrapping every integer/string allocation.
SovaInt = int
SovaFloat = float
SovaString = str
SovaBool = bool
SovaNull = type(None)
SovaList = list
SovaTuple = tuple
SovaObject = dict
SovaNativeFunctionType = SovaNativeFunction
