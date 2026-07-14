from __future__ import annotations

"""Structural semantic analysis before Sova runtime execution."""

from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from . import ast_nodes as ast
from .diagnostics import Diagnostic


BUILTINS = {
    "Sova",
    "print",
    "input",
    "len",
    "type",
    "Error",
    "SyntaxError",
    "TypeError",
    "NameError",
    "IndexError",
    "FileError",
    "ImportError",
    "ValueError",
    "RuntimeError",
}

VALID_TYPES = {"Int", "Float", "String", "Bool", "Null", "List", "Tuple", "Object", "Any", "Function"}


@dataclass(slots=True)
class SemanticReport:
    diagnostics: list[Diagnostic]

    @property
    def errors(self) -> list[Diagnostic]:
        return [item for item in self.diagnostics if item.severity == "error"]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [item for item in self.diagnostics if item.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.scopes: list[dict[str, int]] = [{name: 1 for name in BUILTINS}]
        self.diagnostics: list[Diagnostic] = []
        self.function_depth = 0
        self.loop_depth = 0
        self.method_depth = 0

    def analyze(self, program: ast.ProgramNode) -> SemanticReport:
        self.visit(program)
        self.add_unused_warnings(self.scopes[0])
        return SemanticReport(self.diagnostics)

    def visit(self, node: Any) -> None:
        if node is None:
            return
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return
        if isinstance(node, tuple):
            for item in node:
                self.visit(item)
            return
        method = getattr(self, f"visit_{node.__class__.__name__}", None)
        if method:
            method(node)
            return
        if is_dataclass(node):
            for item in fields(node):
                if item.name != "span":
                    self.visit(getattr(node, item.name))

    def visit_ProgramNode(self, node: ast.ProgramNode) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_BlockNode(self, node: ast.BlockNode) -> None:
        self.begin_scope()
        terminated = False
        for statement in node.statements:
            if terminated:
                self.warn("SOVA_FLOW_002", "This statement is unreachable.", statement.span)
            self.visit(statement)
            terminated = (
                isinstance(statement, ast.ReturnNode)
                and statement.condition is None
            ) or isinstance(statement, (ast.ThrowNode, ast.BreakNode, ast.ContinueNode))
        self.end_scope()

    def visit_LetNode(self, node: ast.LetNode) -> None:
        self.visit(node.value)
        self.validate_type(node.annotation)
        self.declare_pattern(node.target)

    def visit_IdentifierNode(self, node: ast.IdentifierNode) -> None:
        if not self.resolve(node.name):
            self.error(
                "SOVA_NAME_001",
                f"The variable '{node.name}' is not defined.",
                node.span,
                f"Declare it first with: let {node.name} = ...",
            )

    def visit_AssignmentNode(self, node: ast.AssignmentNode) -> None:
        if isinstance(node.target, ast.IdentifierNode) and not self.resolve(node.target.name):
            self.error("SOVA_ASSIGN_001", f"Cannot assign to undefined variable '{node.target.name}'.", node.span)
        elif not isinstance(node.target, (ast.IdentifierNode, ast.PropertyNode, ast.SafePropertyNode, ast.IndexNode)):
            self.error("SOVA_ASSIGN_002", "Invalid assignment target.", node.span)
        else:
            if not isinstance(node.target, ast.IdentifierNode):
                self.visit(node.target)
        self.visit(node.value)

    def visit_FunctionNode(self, node: ast.FunctionNode) -> None:
        if node.name:
            self.declare(node.name, node.span)
        self.begin_scope()
        self.function_depth += 1
        for parameter in node.parameters:
            self.validate_type(parameter.annotation)
            self.declare(parameter.name, parameter.span)
            self.visit(parameter.default)
        self.validate_type(node.return_type)
        self.visit(node.body)
        self.function_depth -= 1
        self.end_scope()

    def visit_LambdaNode(self, node: ast.LambdaNode) -> None:
        self.begin_scope()
        self.function_depth += 1
        for parameter in node.parameters:
            self.declare(parameter.name, parameter.span)
        self.visit(node.body)
        self.function_depth -= 1
        self.end_scope()

    def visit_ReturnNode(self, node: ast.ReturnNode) -> None:
        if self.function_depth == 0:
            self.error("SOVA_FLOW_001", "'return' can only be used inside a function.", node.span)
        self.visit(node.value)
        self.visit(node.condition)

    def visit_WhileNode(self, node: ast.WhileNode) -> None:
        self.visit(node.condition)
        self.loop_depth += 1
        self.visit(node.body)
        self.loop_depth -= 1

    def visit_ForNode(self, node: ast.ForNode) -> None:
        self.visit(node.iterable)
        self.begin_scope()
        self.declare_pattern(node.target)
        self.loop_depth += 1
        self.visit(node.body)
        self.loop_depth -= 1
        self.end_scope()

    def visit_BreakNode(self, node: ast.BreakNode) -> None:
        if self.loop_depth == 0:
            self.error("SOVA_FLOW_003", "'break' can only be used inside a loop.", node.span)

    def visit_ContinueNode(self, node: ast.ContinueNode) -> None:
        if self.loop_depth == 0:
            self.error("SOVA_FLOW_004", "'continue' can only be used inside a loop.", node.span)

    def visit_ClassNode(self, node: ast.ClassNode) -> None:
        self.declare(node.name, node.span)
        if node.superclass and not self.resolve(node.superclass):
            self.error("SOVA_CLASS_001", f"Superclass '{node.superclass}' is not defined.", node.span)
        names: set[str] = set()
        for method in node.methods:
            if method.name in names:
                self.error("SOVA_CLASS_002", f"Duplicate method '{method.name}' in class '{node.name}'.", method.span)
            names.add(method.name or "")
            self.begin_scope()
            self.scopes[-1]["self"] = 1
            self.function_depth += 1
            self.method_depth += 1
            for parameter in method.parameters:
                self.declare(parameter.name, parameter.span)
                self.visit(parameter.default)
            self.visit(method.body)
            self.method_depth -= 1
            self.function_depth -= 1
            self.end_scope()

    def visit_ImportNode(self, node: ast.ImportNode) -> None:
        if node.names:
            for name, alias in node.names:
                self.declare(alias or name, node.span)
        elif not node.module.startswith("Sova."):
            self.declare(node.alias or node.module.split(".")[-1], node.span)

    def visit_ExportNode(self, node: ast.ExportNode) -> None:
        self.visit(node.declaration)

    def visit_TypeAnnotationNode(self, node: ast.TypeAnnotationNode) -> None:
        self.validate_type(node)

    def declare_pattern(self, target: ast.Node | None) -> None:
        if isinstance(target, ast.IdentifierNode):
            self.declare(target.name, target.span)
        elif isinstance(target, ast.DestructureNode):
            for _, name in target.items:
                if name != "_":
                    self.declare(name, target.span)

    def declare(self, name: str, span) -> None:
        scope = self.scopes[-1]
        if name in scope:
            self.error("SOVA_NAME_002", f"'{name}' is already declared in this scope.", span)
        else:
            scope[name] = 0

    def resolve(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] += 1
                return True
        return False

    def validate_type(self, annotation: ast.TypeAnnotationNode | None) -> None:
        if not annotation:
            return
        if annotation.name not in VALID_TYPES:
            self.error("SOVA_TYPE_002", f"Unknown type annotation '{annotation.name}'.", annotation.span)
        for argument in annotation.arguments:
            self.validate_type(argument)

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.add_unused_warnings(self.scopes.pop())

    def add_unused_warnings(self, scope: dict[str, int]) -> None:
        for name, uses in scope.items():
            if uses == 0 and name not in BUILTINS and not name.startswith("_"):
                # Source span is unavailable after scope teardown; unused warnings
                # are intentionally omitted until the resolver tracks declarations.
                pass

    def error(self, code: str, message: str, span, suggestion: str | None = None) -> None:
        self.diagnostics.append(Diagnostic(code, "error", message, span, suggestion))

    def warn(self, code: str, message: str, span, suggestion: str | None = None) -> None:
        self.diagnostics.append(Diagnostic(code, "warning", message, span, suggestion))
