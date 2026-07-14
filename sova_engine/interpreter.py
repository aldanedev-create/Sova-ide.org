from __future__ import annotations

"""Tree-walking interpreter for Sova's one analyzed AST."""

import json
import re
import shlex
import subprocess
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Callable

from . import ast_nodes as ast
from .diagnostics import (
    ExecutionLimitError,
    SourceSpan,
    SovaError,
    SovaFileError,
    SovaImportError,
    SovaIndexError,
    SovaNameError,
    SovaRuntimeError,
    SovaSyntaxError,
    SovaTypeError,
    SovaValueError,
)
from .environment import Environment
from .execution_limits import ExecutionLimits
from .execution_policy import ExecutionPolicy
from .parser import Parser
from .runtime import SovaClass, SovaFunction, SovaInstance, SovaModule, SovaNativeFunction, SovaRange
from .standard_library import sova_root


class ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ThrownSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


def count_ast_nodes(root: ast.Node) -> int:
    """Count nodes iteratively so deeply nested input cannot recurse in the guard."""

    count = 0
    pending: list[Any] = [root]
    while pending:
        value = pending.pop()
        if isinstance(value, ast.Node):
            count += 1
            if is_dataclass(value):
                pending.extend(getattr(value, item.name) for item in fields(value) if item.name != "span")
        elif isinstance(value, (list, tuple)):
            pending.extend(value)
    return count


class Interpreter:
    def __init__(
        self,
        *,
        policy: ExecutionPolicy | None = None,
        writer: Callable[[str], None] | None = None,
        input_reader: Callable[[str], str] | None = None,
        virtual_files: dict[str, str] | None = None,
        module_loader: Any = None,
        limits: ExecutionLimits | None = None,
        sova_library: Any = None,
    ) -> None:
        self.policy = policy or ExecutionPolicy.local()
        self.limits = limits or ExecutionLimits(self.policy)
        self.writer = writer or (lambda text: print(text, end=""))
        self.input_reader = input_reader or input
        self.virtual_files = virtual_files or {}
        self.module_loader = module_loader
        self.globals = Environment()
        self.environment = self.globals
        self.exports: dict[str, Any] = {}
        self.last_value: Any = None
        self.current_source = ""
        self.current_filename = "<source>"
        self.sova_library = sova_library
        self.install_builtins()

    def install_builtins(self) -> None:
        if self.sova_library is None:
            self.sova_library = sova_root(self.policy, self.virtual_files)
        self.globals.define("Sova", self.sova_library)
        self.globals.define("print", SovaNativeFunction("print", self.native_print))
        self.globals.define("input", SovaNativeFunction("input", self.input_reader))
        self.globals.define("len", SovaNativeFunction("len", len))
        self.globals.define("type", SovaNativeFunction("type", lambda value: type_name(value)))
        self.globals.define("Error", SovaNativeFunction("Error", lambda message="Error": SovaRuntimeError(str(message))))
        self.globals.define("SyntaxError", SovaNativeFunction("SyntaxError", lambda message="Syntax error": SovaRuntimeError(str(message))))
        self.globals.define("TypeError", SovaNativeFunction("TypeError", lambda message="Type error": SovaTypeError(str(message))))
        self.globals.define("NameError", SovaNativeFunction("NameError", lambda message="Name error": SovaNameError(str(message))))
        self.globals.define("IndexError", SovaNativeFunction("IndexError", lambda message="Index error": SovaIndexError(str(message))))
        self.globals.define("FileError", SovaNativeFunction("FileError", lambda message="File error": SovaFileError(str(message))))
        self.globals.define("ImportError", SovaNativeFunction("ImportError", lambda message="Import error": SovaImportError(str(message))))
        self.globals.define("ValueError", SovaNativeFunction("ValueError", lambda message="Value error": SovaValueError(str(message))))
        self.globals.define("RuntimeError", SovaNativeFunction("RuntimeError", lambda message="Runtime error": SovaRuntimeError(str(message))))

    def run(self, source: str, filename: str = "<source>", *, analyze: bool = True) -> "Interpreter":
        if len(source.encode("utf-8")) > self.policy.max_source_bytes:
            raise ExecutionLimitError(
                f"Source exceeds the {self.policy.max_source_bytes:,}-byte limit.",
                SourceSpan.synthetic(filename),
            )
        self.current_source = source
        self.current_filename = filename
        program = Parser(source, filename).parse()
        ast_nodes = count_ast_nodes(program)
        if ast_nodes > self.policy.max_ast_nodes:
            raise ExecutionLimitError(
                f"The program exceeds the AST limit of {self.policy.max_ast_nodes:,} nodes.",
                program.span,
                source=source,
                suggestion="Split the program into smaller modules or run it locally with a higher limit.",
            )
        if analyze:
            from .semantic_analyzer import SemanticAnalyzer

            report = SemanticAnalyzer().analyze(program)
            if report.errors:
                error = report.errors[0]
                raise SovaRuntimeError(error.message, error.span, source=source, suggestion=error.suggestion)
        self.interpret(program)
        return self

    def interpret(self, program: ast.ProgramNode) -> Any:
        try:
            for statement in program.statements:
                self.last_value = self.execute(statement)
        except ThrownSignal as thrown:
            if isinstance(thrown.value, Exception):
                raise thrown.value
            raise SovaRuntimeError(str(thrown.value), program.span, source=self.current_source) from None
        return self.last_value

    def execute(self, node: ast.Node | None) -> Any:
        if node is None:
            return None
        self.limits.step(node.span)
        method = getattr(self, f"execute_{node.__class__.__name__}", None)
        if not method:
            return self.evaluate(node)
        return method(node)

    def evaluate(self, node: ast.Node | None) -> Any:
        if node is None:
            return None
        self.limits.step(node.span)
        method = getattr(self, f"evaluate_{node.__class__.__name__}", None)
        if not method:
            raise SovaRuntimeError(f"Unsupported AST node {node.__class__.__name__}.", node.span)
        try:
            value = method(node)
            self.limits.check_collection(value, node.span)
            return value
        except (SovaError, ReturnSignal, BreakSignal, ContinueSignal, ThrownSignal):
            raise
        except (IndexError, KeyError) as error:
            raise SovaIndexError(str(error), node.span, source=self.current_source) from None
        except TypeError as error:
            raise SovaTypeError(str(error), node.span, source=self.current_source) from None
        except Exception as error:  # noqa: BLE001 - convert host errors into Sova diagnostics.
            raise SovaRuntimeError(str(error), node.span, source=self.current_source) from None

    def execute_BlockNode(self, node: ast.BlockNode) -> Any:
        return self.execute_block(node, Environment(self.environment))

    def execute_block(self, block: ast.BlockNode, environment: Environment) -> Any:
        previous = self.environment
        self.environment = environment
        result = None
        try:
            for statement in block.statements:
                result = self.execute(statement)
        finally:
            self.environment = previous
        return result

    def execute_LetNode(self, node: ast.LetNode) -> Any:
        value = self.evaluate(node.value)
        self.check_type(value, node.annotation, node.span)
        self.bind_pattern(node.target, value, define=True)
        return value

    def execute_ExpressionStatementNode(self, node: ast.ExpressionStatementNode) -> Any:
        return self.evaluate(node.expression)

    def execute_FunctionNode(self, node: ast.FunctionNode) -> SovaFunction:
        function = SovaFunction(node, self.environment)
        if node.name:
            self.environment.define(node.name, function)
        return function

    def execute_ReturnNode(self, node: ast.ReturnNode) -> None:
        if node.condition is not None and not truthy(self.evaluate(node.condition)):
            return None
        raise ReturnSignal(self.evaluate(node.value))

    def execute_IfNode(self, node: ast.IfNode) -> Any:
        for condition, branch in node.branches:
            if truthy(self.evaluate(condition)):
                return self.execute(branch)
        return self.execute(node.else_branch) if node.else_branch else None

    def execute_WhileNode(self, node: ast.WhileNode) -> Any:
        result = None
        while truthy(self.evaluate(node.condition)):
            self.limits.step(node.span)
            try:
                result = self.execute(node.body)
            except ContinueSignal:
                continue
            except BreakSignal:
                break
        return result

    def execute_ForNode(self, node: ast.ForNode) -> Any:
        iterable = self.evaluate(node.iterable)
        if isinstance(iterable, SovaRange):
            iterable = iterable.values()
        result = None
        for value in iterable:
            self.limits.step(node.span)
            loop_environment = Environment(self.environment)
            previous = self.environment
            self.environment = loop_environment
            try:
                self.bind_pattern(node.target, value, define=True)
                result = self.execute(node.body)
            except ContinueSignal:
                continue
            except BreakSignal:
                break
            finally:
                self.environment = previous
        return result

    def execute_BreakNode(self, _node: ast.BreakNode) -> None:
        raise BreakSignal()

    def execute_ContinueNode(self, _node: ast.ContinueNode) -> None:
        raise ContinueSignal()

    def execute_ClassNode(self, node: ast.ClassNode) -> SovaClass:
        superclass = None
        if node.superclass:
            superclass = self.environment.get(node.superclass, node.span)
            if not isinstance(superclass, SovaClass):
                raise SovaTypeError(f"'{node.superclass}' is not a class.", node.span)
        self.environment.define(node.name, None)
        methods = {method.name or "": SovaFunction(method, self.environment) for method in node.methods}
        klass = SovaClass(node.name, node.constructor_parameters, methods, superclass)
        self.environment.assign(node.name, klass, node.span)
        return klass

    def execute_ImportNode(self, node: ast.ImportNode) -> Any:
        if node.module == "Sova" or node.module.startswith("Sova."):
            return self.globals.get("Sova", node.span)
        if not self.module_loader:
            raise SovaRuntimeError(f"No module loader is configured for '{node.module}'.", node.span)
        module = self.module_loader.load(node.module, self)
        if node.names:
            for name, alias in node.names:
                if name not in module.exports:
                    raise SovaRuntimeError(f"Module '{node.module}' does not export '{name}'.", node.span)
                self.environment.define(alias or name, module.exports[name])
        else:
            self.environment.define(node.alias or node.module.split(".")[-1], module)
        return module

    def execute_ExportNode(self, node: ast.ExportNode) -> Any:
        value = self.execute(node.declaration) if isinstance(node.declaration, ast.Node) else None
        name = getattr(node.declaration, "name", None)
        if isinstance(node.declaration, ast.LetNode) and isinstance(node.declaration.target, ast.IdentifierNode):
            name = node.declaration.target.name
        if node.default:
            self.exports["default"] = value
        elif name:
            self.exports[name] = self.environment.get(name, node.span)
        return value

    def execute_TryNode(self, node: ast.TryNode) -> Any:
        try:
            return self.execute(node.body)
        except (ExecutionLimitError, ReturnSignal, BreakSignal, ContinueSignal):
            raise
        except Exception as error:  # noqa: BLE001 - language-level catch.
            environment = Environment(self.environment)
            environment.define(node.error_name or "error", str(error))
            return self.execute_block(node.catch_body, environment) if node.catch_body else None

    def execute_ThrowNode(self, node: ast.ThrowNode) -> None:
        raise ThrownSignal(self.evaluate(node.value))

    def execute_ShellNode(self, node: ast.ShellNode) -> int:
        command = str(self.evaluate(node.command))
        if not self.policy.allow_shell:
            raise SovaRuntimeError(
                "Shell execution is disabled by the current Sova policy.",
                node.span,
                suggestion="Run locally with: sova run file.sova --allow-shell",
            )
        parts = shlex.split(command, posix=False)
        if not parts:
            return 0
        if parts[0].lower() == "echo":
            self.native_print(" ".join(parts[1:]))
            return 0
        completed = subprocess.run(parts, shell=False, check=False, capture_output=True, text=True, timeout=10)
        if completed.stdout:
            self.native_print(completed.stdout.rstrip("\n"))
        if completed.stderr:
            self.native_print(completed.stderr.rstrip("\n"))
        return completed.returncode

    def evaluate_LiteralNode(self, node: ast.LiteralNode) -> Any:
        if isinstance(node.value, str) and "{" in node.value:
            return self.interpolate(node.value, node.span)
        return node.value

    def evaluate_IdentifierNode(self, node: ast.IdentifierNode) -> Any:
        return self.environment.get(node.name, node.span)

    def evaluate_ListNode(self, node: ast.ListNode) -> list[Any]:
        return [self.evaluate(item) for item in node.items]

    def evaluate_TupleNode(self, node: ast.TupleNode) -> tuple[Any, ...]:
        return tuple(self.evaluate(item) for item in node.items)

    def evaluate_ObjectNode(self, node: ast.ObjectNode) -> dict[str, Any]:
        return {key: self.evaluate(value) for key, value in node.entries}

    def evaluate_UnaryNode(self, node: ast.UnaryNode) -> Any:
        value = self.evaluate(node.operand)
        if node.operator in {"!", "not"}:
            return not truthy(value)
        if node.operator == "-":
            return -value
        if node.operator == "+":
            return +value
        raise SovaRuntimeError(f"Unknown unary operator '{node.operator}'.", node.span)

    def evaluate_BinaryNode(self, node: ast.BinaryNode) -> Any:
        left = self.evaluate(node.left)
        if node.operator in {"and", "&&"}:
            return self.evaluate(node.right) if truthy(left) else left
        if node.operator in {"or", "||"}:
            return left if truthy(left) else self.evaluate(node.right)
        if node.operator == "??":
            return left if left is not None else self.evaluate(node.right)
        right = self.evaluate(node.right)
        return apply_binary(node.operator, left, right, node.span)

    def evaluate_RangeNode(self, node: ast.RangeNode) -> SovaRange:
        return SovaRange(int(self.evaluate(node.start)), int(self.evaluate(node.end)))

    def evaluate_ConditionalExpressionNode(self, node: ast.ConditionalExpressionNode) -> Any:
        return self.evaluate(node.then_value if truthy(self.evaluate(node.condition)) else node.else_value)

    def evaluate_AssignmentNode(self, node: ast.AssignmentNode) -> Any:
        value = self.evaluate(node.value)
        if node.operator != "=":
            current = self.read_target(node.target)
            value = apply_binary(node.operator[0], current, value, node.span)
        self.write_target(node.target, value)
        return value

    def evaluate_PropertyNode(self, node: ast.PropertyNode) -> Any:
        return self.get_property(self.evaluate(node.target), node.name, node.span)

    def evaluate_SafePropertyNode(self, node: ast.SafePropertyNode) -> Any:
        target = self.evaluate(node.target)
        if target is None:
            return None
        try:
            return self.get_property(target, node.name, node.span)
        except SovaRuntimeError:
            return None

    def evaluate_IndexNode(self, node: ast.IndexNode) -> Any:
        target = self.evaluate(node.target)
        index = self.evaluate(node.index)
        return target[index]

    def evaluate_SliceNode(self, node: ast.SliceNode) -> Any:
        target = self.evaluate(node.target)
        start = self.evaluate(node.start) if node.start else None
        end = self.evaluate(node.end) if node.end else None
        return target[start:end]

    def evaluate_CallNode(self, node: ast.CallNode) -> Any:
        callee = self.evaluate(node.callee)
        positional = []
        named = {}
        for argument in node.arguments:
            value = self.evaluate(argument.value)
            if argument.name:
                named[argument.name] = value
            else:
                positional.append(value)
        return self.call_value(callee, positional, named, node.span)

    def evaluate_LambdaNode(self, node: ast.LambdaNode) -> SovaFunction:
        body = node.body if isinstance(node.body, ast.BlockNode) else ast.BlockNode(
            span=node.body.span,
            statements=[ast.ReturnNode(span=node.body.span, value=node.body)],
        )
        declaration = ast.FunctionNode(span=node.span, name=None, parameters=node.parameters, body=body)
        return SovaFunction(declaration, self.environment)

    def evaluate_FunctionNode(self, node: ast.FunctionNode) -> SovaFunction:
        return SovaFunction(node, self.environment)

    def evaluate_TryExpressionNode(self, node: ast.TryExpressionNode) -> Any:
        try:
            return self.evaluate(node.expression)
        except ExecutionLimitError:
            raise
        except Exception:  # noqa: BLE001 - language fallback expression.
            return self.evaluate(node.fallback)

    def call_value(self, callee: Any, positional: list[Any], named: dict[str, Any], span: SourceSpan) -> Any:
        self.limits.enter_call(span)
        try:
            if isinstance(callee, SovaFunction):
                return self.call_function(callee, positional, named, span)
            if isinstance(callee, SovaClass):
                return self.call_class(callee, positional, named, span)
            if isinstance(callee, SovaNativeFunction):
                return callee.function(*positional, **named)
            raise SovaTypeError(f"{format_value(callee)} is not callable.", span)
        finally:
            self.limits.leave_call()

    def call_function(self, function: SovaFunction, positional: list[Any], named: dict[str, Any], span: SourceSpan) -> Any:
        environment = Environment(function.closure)
        if function.bound_self:
            environment.define("self", function.bound_self)
        position = 0
        for parameter in function.declaration.parameters:
            if parameter.variadic:
                value = positional[position:]
                position = len(positional)
            elif parameter.name in named:
                value = named.pop(parameter.name)
            elif position < len(positional):
                value = positional[position]
                position += 1
            elif parameter.default is not None:
                previous = self.environment
                self.environment = function.closure
                try:
                    value = self.evaluate(parameter.default)
                finally:
                    self.environment = previous
            else:
                raise SovaTypeError(f"Missing argument '{parameter.name}' for {function.name}().", span)
            self.check_type(value, parameter.annotation, span)
            environment.define(parameter.name, value)
        if position < len(positional) or named:
            raise SovaTypeError(f"Too many arguments for {function.name}().", span)
        try:
            self.execute_block(function.declaration.body, environment)
        except ReturnSignal as returned:
            self.check_type(returned.value, function.declaration.return_type, span)
            return returned.value
        self.check_type(None, function.declaration.return_type, span)
        return None

    def call_class(self, klass: SovaClass, positional: list[Any], named: dict[str, Any], span: SourceSpan) -> SovaInstance:
        instance = SovaInstance(klass)
        parameters = klass.constructor_parameters
        if parameters:
            values = self.bind_call_arguments(parameters, positional, named, span)
            for parameter, value in zip(parameters, values):
                self.check_type(value, parameter.annotation, span)
                instance.set(parameter.name, value)
        initializer = klass.find_method("init")
        if initializer:
            self.call_value(initializer.bind(instance), positional, dict(named), span)
        elif not parameters and (positional or named):
            raise SovaTypeError(f"{klass.name}() does not accept constructor arguments.", span)
        return instance

    def bind_call_arguments(self, parameters: list[ast.Parameter], positional: list[Any], named: dict[str, Any], span: SourceSpan) -> list[Any]:
        values = []
        named = dict(named)
        for index, parameter in enumerate(parameters):
            if parameter.name in named:
                values.append(named.pop(parameter.name))
            elif index < len(positional):
                values.append(positional[index])
            elif parameter.default is not None:
                values.append(self.evaluate(parameter.default))
            else:
                raise SovaTypeError(f"Missing constructor argument '{parameter.name}'.", span)
        if len(positional) > len(parameters) or named:
            raise SovaTypeError("Constructor argument count does not match its declaration.", span)
        return values

    def bind_pattern(self, target: ast.Node | None, value: Any, *, define: bool) -> None:
        if isinstance(target, ast.IdentifierNode):
            (self.environment.define if define else self.environment.assign)(target.name, value, target.span) if not define else self.environment.define(target.name, value)
            return
        if isinstance(target, ast.DestructureNode):
            if target.kind == "list":
                if not isinstance(value, (list, tuple)):
                    raise SovaTypeError("List destructuring requires a list or tuple.", target.span)
                for index, (_, name) in enumerate(target.items):
                    item = value[index] if index < len(value) else None
                    if name != "_":
                        self.environment.define(name, item)
            else:
                if not isinstance(value, dict):
                    raise SovaTypeError("Object destructuring requires an object.", target.span)
                for key, name in target.items:
                    if name != "_":
                        self.environment.define(name, value.get(key))
            return
        raise SovaTypeError("Invalid binding target.", target.span if target else SourceSpan.synthetic())

    def read_target(self, target: ast.Node | None) -> Any:
        if isinstance(target, ast.IdentifierNode):
            return self.environment.get(target.name, target.span)
        if isinstance(target, (ast.PropertyNode, ast.SafePropertyNode)):
            return self.get_property(self.evaluate(target.target), target.name, target.span)
        if isinstance(target, ast.IndexNode):
            return self.evaluate(target.target)[self.evaluate(target.index)]
        raise SovaTypeError("Invalid assignment target.", target.span if target else SourceSpan.synthetic())

    def write_target(self, target: ast.Node | None, value: Any) -> Any:
        if isinstance(target, ast.IdentifierNode):
            return self.environment.assign(target.name, value, target.span)
        if isinstance(target, (ast.PropertyNode, ast.SafePropertyNode)):
            owner = self.evaluate(target.target)
            if isinstance(owner, SovaInstance):
                return owner.set(target.name, value)
            if isinstance(owner, dict):
                owner[target.name] = value
                return value
            raise SovaTypeError(f"Cannot set properties on host value {type_name(owner)}.", target.span)
        if isinstance(target, ast.IndexNode):
            owner = self.evaluate(target.target)
            owner[self.evaluate(target.index)] = value
            return value
        raise SovaTypeError("Invalid assignment target.", target.span if target else SourceSpan.synthetic())

    def get_property(self, value: Any, name: str, span: SourceSpan) -> Any:
        self.limits.step(span)
        if isinstance(value, SovaInstance):
            try:
                return value.get(name)
            except AttributeError:
                raise SovaRuntimeError(f"{value.klass.name} has no property '{name}'.", span) from None
        if isinstance(value, SovaModule):
            if name in value.exports:
                return value.exports[name]
            raise SovaRuntimeError(f"Module '{value.name}' has no export '{name}'.", span)
        if isinstance(value, dict):
            if name in value:
                return value[name]
            method = self.object_method(value, name)
            if method:
                return method
            raise SovaRuntimeError(f"Object has no field '{name}'.", span)
        if isinstance(value, list):
            method = self.list_method(value, name)
            if method:
                return method
        if isinstance(value, tuple):
            method = self.list_method(list(value), name, mutable=False)
            if method:
                return method
        if isinstance(value, str):
            method = self.string_method(value, name)
            if method:
                return method
        approved, member = self.sova_library.resolve_member(value, name)
        if approved:
            if callable(member):
                return SovaNativeFunction(f"library.{name}", member)
            return member
        if name.startswith("__") and name.endswith("__"):
            raise SovaRuntimeError("Python dunder attributes are not accessible from Sova.", span)
        raise SovaRuntimeError(f"{type_name(value)} has no property '{name}'.", span)

    def list_method(self, values: list[Any], name: str, *, mutable: bool = True) -> SovaNativeFunction | None:
        def mutate(method):
            def wrapped(*args):
                if not mutable:
                    raise SovaTypeError("Tuples cannot be changed.")
                result = method(*args)
                return values if result is None else result
            return wrapped

        methods: dict[str, Callable[..., Any]] = {
            "add": mutate(values.append),
            "append": mutate(values.append),
            "insert": mutate(values.insert),
            "remove": mutate(values.remove),
            "pop": mutate(values.pop),
            "clear": mutate(values.clear),
            "contains": lambda item: item in values,
            "length": lambda: len(values),
            "isEmpty": lambda: not values,
            "first": lambda: values[0] if values else None,
            "last": lambda: values[-1] if values else None,
            "sort": mutate(values.sort),
            "reverse": mutate(values.reverse),
            "map": lambda function: [self.call_value(function, [item], {}, SourceSpan.synthetic()) for item in values],
            "filter": lambda function: [item for item in values if truthy(self.call_value(function, [item], {}, SourceSpan.synthetic()))],
            "reduce": lambda function, initial=None: self.reduce_values(values, function, initial),
            "find": lambda function: next((item for item in values if truthy(self.call_value(function, [item], {}, SourceSpan.synthetic()))), None),
            "any": lambda function=None: any(truthy(self.call_value(function, [item], {}, SourceSpan.synthetic())) for item in values) if function else any(map(truthy, values)),
            "all": lambda function=None: all(truthy(self.call_value(function, [item], {}, SourceSpan.synthetic())) for item in values) if function else all(map(truthy, values)),
            "unique": lambda: list(dict.fromkeys(values)),
            "join": lambda separator="": separator.join(format_value(item) for item in values),
            "average": lambda: sum(values) / len(values) if values else 0,
        }
        return SovaNativeFunction(f"list.{name}", methods[name]) if name in methods else None

    def reduce_values(self, values: list[Any], function: Any, initial: Any = None) -> Any:
        if not values and initial is None:
            return None
        iterator = iter(values)
        accumulator = next(iterator) if initial is None else initial
        for item in iterator:
            accumulator = self.call_value(function, [accumulator, item], {}, SourceSpan.synthetic())
        return accumulator

    def object_method(self, value: dict[str, Any], name: str) -> SovaNativeFunction | None:
        methods: dict[str, Callable[..., Any]] = {
            "keys": lambda: list(value.keys()),
            "values": lambda: list(value.values()),
            "entries": lambda: [[key, item] for key, item in value.items()],
            "contains": lambda key: key in value,
            "get": lambda key, default=None: value.get(key, default),
            "set": lambda key, item: value.__setitem__(key, item) or value,
            "remove": lambda key: value.pop(key, None),
            "merge": lambda other: {**value, **other},
            "length": lambda: len(value),
            "isEmpty": lambda: not value,
        }
        return SovaNativeFunction(f"object.{name}", methods[name]) if name in methods else None

    def string_method(self, value: str, name: str) -> SovaNativeFunction | None:
        methods: dict[str, Callable[..., Any]] = {
            "length": lambda: len(value),
            "upper": value.upper,
            "lower": value.lower,
            "trim": value.strip,
            "split": value.split,
            "replace": value.replace,
            "contains": lambda part: part in value,
            "startsWith": value.startswith,
            "endsWith": value.endswith,
            "slice": lambda start=None, end=None: value[start:end],
            "isEmpty": lambda: not value,
        }
        return SovaNativeFunction(f"string.{name}", methods[name]) if name in methods else None

    def interpolate(self, template: str, span: SourceSpan) -> str:
        def replace(match: re.Match[str]) -> str:
            expression = match.group(1).strip()
            try:
                node = Parser(expression, span.filename).parse_expression_only()
                return format_value(self.evaluate(node))
            except Exception:
                return match.group(0)
        return re.sub(r"\{([^{}]+)\}", replace, template)

    def native_print(self, *values: Any) -> None:
        text = " ".join(format_value(value) for value in values) + "\n"
        self.limits.count_output(text, SourceSpan.synthetic(self.current_filename))
        self.writer(text)

    def check_type(self, value: Any, annotation: ast.TypeAnnotationNode | None, span: SourceSpan) -> None:
        if not annotation or annotation.name == "Any":
            return
        if value is None and annotation.nullable:
            return
        expected = {
            "Int": int,
            "Float": (int, float),
            "String": str,
            "Bool": bool,
            "Null": type(None),
            "List": list,
            "Tuple": tuple,
            "Object": dict,
            "Function": (SovaFunction, SovaNativeFunction),
        }.get(annotation.name)
        if expected and (isinstance(value, bool) and annotation.name == "Int" or not isinstance(value, expected)):
            raise SovaTypeError(
                f"Expected {annotation.name}, but received {type_name(value)}.",
                span,
                suggestion="Change the value or remove the optional type annotation.",
            )


def apply_binary(operator: str, left: Any, right: Any, span: SourceSpan) -> Any:
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise SovaValueError("Division by zero is not allowed.", span)
        return left / right
    if operator == "%":
        if right == 0:
            raise SovaValueError("Modulo by zero is not allowed.", span)
        return left % right
    if operator == "**":
        return left**right
    if operator == "==":
        return left == right
    if operator == "!=":
        return left != right
    if operator == ">":
        return left > right
    if operator == ">=":
        return left >= right
    if operator == "<":
        return left < right
    if operator == "<=":
        return left <= right
    if operator == "in":
        return left in right
    if operator == "is":
        return left is right if right is None else left == right
    raise SovaRuntimeError(f"Unknown binary operator '{operator}'.", span)


def truthy(value: Any) -> bool:
    return bool(value)


def type_name(value: Any) -> str:
    if value is None:
        return "Null"
    if isinstance(value, bool):
        return "Bool"
    if isinstance(value, int):
        return "Int"
    if isinstance(value, float):
        return "Float"
    if isinstance(value, str):
        return "String"
    if isinstance(value, list):
        return "List"
    if isinstance(value, tuple):
        return "Tuple"
    if isinstance(value, dict):
        return "Object"
    return value.__class__.__name__


def format_value(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, default=str)
    if isinstance(value, (list, tuple)):
        opening, closing = ("[", "]") if isinstance(value, list) else ("(", ")")
        return opening + ", ".join(format_value(item) for item in value) + closing
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def run_source(
    source: str,
    filename: str = "<source>",
    *,
    policy: ExecutionPolicy | None = None,
    writer: Callable[[str], None] | None = None,
) -> Interpreter:
    return Interpreter(policy=policy, writer=writer).run(source, filename)
