from __future__ import annotations

"""One source-located AST model for Sova parsing, analysis, and execution."""

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from typing import Any

from .diagnostics import SourceSpan


@dataclass(slots=True, kw_only=True)
class Node:
    span: SourceSpan


@dataclass(slots=True)
class ProgramNode(Node):
    statements: list[Node] = field(default_factory=list)


@dataclass(slots=True)
class BlockNode(Node):
    statements: list[Node] = field(default_factory=list)


@dataclass(slots=True)
class TypeAnnotationNode(Node):
    name: str = "Any"
    arguments: list["TypeAnnotationNode"] = field(default_factory=list)
    nullable: bool = False


@dataclass(slots=True)
class Parameter:
    name: str
    span: SourceSpan
    annotation: TypeAnnotationNode | None = None
    default: Node | None = None
    variadic: bool = False


@dataclass(slots=True)
class LetNode(Node):
    target: Node | None = None
    value: Node | None = None
    annotation: TypeAnnotationNode | None = None


@dataclass(slots=True)
class AssignmentNode(Node):
    target: Node | None = None
    value: Node | None = None
    operator: str = "="


@dataclass(slots=True)
class FunctionNode(Node):
    name: str | None = None
    parameters: list[Parameter] = field(default_factory=list)
    body: BlockNode | None = None
    return_type: TypeAnnotationNode | None = None
    exported: bool = False


@dataclass(slots=True)
class MethodNode(FunctionNode):
    pass


@dataclass(slots=True)
class ReturnNode(Node):
    value: Node | None = None
    condition: Node | None = None


@dataclass(slots=True)
class IfNode(Node):
    branches: list[tuple[Node, BlockNode]] = field(default_factory=list)
    else_branch: BlockNode | None = None


@dataclass(slots=True)
class WhileNode(Node):
    condition: Node | None = None
    body: BlockNode | None = None


@dataclass(slots=True)
class ForNode(Node):
    target: Node | None = None
    iterable: Node | None = None
    body: BlockNode | None = None


@dataclass(slots=True)
class BreakNode(Node):
    pass


@dataclass(slots=True)
class ContinueNode(Node):
    pass


@dataclass(slots=True)
class ClassNode(Node):
    name: str = ""
    constructor_parameters: list[Parameter] = field(default_factory=list)
    superclass: str | None = None
    methods: list[FunctionNode] = field(default_factory=list)
    exported: bool = False


@dataclass(slots=True)
class ImportNode(Node):
    module: str = ""
    alias: str | None = None
    names: list[tuple[str, str | None]] = field(default_factory=list)


@dataclass(slots=True)
class ExportNode(Node):
    declaration: Node | None = None
    default: bool = False


@dataclass(slots=True)
class TryNode(Node):
    body: BlockNode | None = None
    error_name: str | None = None
    catch_body: BlockNode | None = None


@dataclass(slots=True)
class CatchNode(Node):
    name: str = "error"
    body: BlockNode | None = None


@dataclass(slots=True)
class ThrowNode(Node):
    value: Node | None = None


@dataclass(slots=True)
class ShellNode(Node):
    command: Node | None = None


@dataclass(slots=True)
class ExpressionStatementNode(Node):
    expression: Node | None = None


@dataclass(slots=True)
class BinaryNode(Node):
    left: Node | None = None
    operator: str = ""
    right: Node | None = None


@dataclass(slots=True)
class UnaryNode(Node):
    operator: str = ""
    operand: Node | None = None


@dataclass(slots=True)
class LiteralNode(Node):
    value: Any = None


@dataclass(slots=True)
class IdentifierNode(Node):
    name: str = ""


@dataclass(slots=True)
class ListNode(Node):
    items: list[Node] = field(default_factory=list)


@dataclass(slots=True)
class TupleNode(Node):
    items: list[Node] = field(default_factory=list)


@dataclass(slots=True)
class ObjectNode(Node):
    entries: list[tuple[str, Node]] = field(default_factory=list)


@dataclass(slots=True)
class IndexNode(Node):
    target: Node | None = None
    index: Node | None = None


@dataclass(slots=True)
class SliceNode(Node):
    target: Node | None = None
    start: Node | None = None
    end: Node | None = None


@dataclass(slots=True)
class PropertyNode(Node):
    target: Node | None = None
    name: str = ""


@dataclass(slots=True)
class SafePropertyNode(PropertyNode):
    pass


@dataclass(slots=True)
class CallArgument:
    value: Node
    name: str | None = None


@dataclass(slots=True)
class CallNode(Node):
    callee: Node | None = None
    arguments: list[CallArgument] = field(default_factory=list)


@dataclass(slots=True)
class LambdaNode(Node):
    parameters: list[Parameter] = field(default_factory=list)
    body: Node | None = None


@dataclass(slots=True)
class RangeNode(Node):
    start: Node | None = None
    end: Node | None = None


@dataclass(slots=True)
class ConditionalExpressionNode(Node):
    condition: Node | None = None
    then_value: Node | None = None
    else_value: Node | None = None


@dataclass(slots=True)
class DestructureNode(Node):
    kind: str = "list"
    items: list[tuple[str | None, str]] = field(default_factory=list)


@dataclass(slots=True)
class TryExpressionNode(Node):
    expression: Node | None = None
    fallback: Node | None = None


def node_to_data(value: Any) -> Any:
    if isinstance(value, SourceSpan):
        return asdict(value)
    if isinstance(value, Node):
        data = {item.name: node_to_data(getattr(value, item.name)) for item in fields(value)}
        data["node"] = value.__class__.__name__
        return data
    if is_dataclass(value):
        return {item.name: node_to_data(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, list):
        return [node_to_data(item) for item in value]
    if isinstance(value, tuple):
        return [node_to_data(item) for item in value]
    if isinstance(value, dict):
        return {str(key): node_to_data(item) for key, item in value.items()}
    return value
