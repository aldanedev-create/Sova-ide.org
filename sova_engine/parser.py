from __future__ import annotations

"""Sova's single recursive-descent statement parser and Pratt-style expression parser."""

from .ast_nodes import (
    AssignmentNode,
    BinaryNode,
    BlockNode,
    BreakNode,
    CallArgument,
    CallNode,
    ClassNode,
    ConditionalExpressionNode,
    ContinueNode,
    DestructureNode,
    ExportNode,
    ExpressionStatementNode,
    ForNode,
    FunctionNode,
    IdentifierNode,
    IfNode,
    ImportNode,
    IndexNode,
    LambdaNode,
    LetNode,
    ListNode,
    LiteralNode,
    Node,
    ObjectNode,
    Parameter,
    ProgramNode,
    PropertyNode,
    RangeNode,
    ReturnNode,
    SafePropertyNode,
    ShellNode,
    SliceNode,
    ThrowNode,
    TryExpressionNode,
    TryNode,
    TupleNode,
    TypeAnnotationNode,
    UnaryNode,
    WhileNode,
)
from .diagnostics import SourceSpan, SovaSyntaxError
from .lexer import tokenize
from .tokens import Token


ASSIGNMENT_TYPES = {"EQUAL", "PLUS_EQUAL", "MINUS_EQUAL", "STAR_EQUAL", "SLASH_EQUAL"}


class Parser:
    def __init__(self, source: str, filename: str = "<source>") -> None:
        self.source = source
        self.filename = filename
        self.tokens = tokenize(source, filename)
        self.index = 0

    def parse(self) -> ProgramNode:
        statements: list[Node] = []
        self.skip_separators()
        start = self.current.span
        while not self.check("EOF"):
            statements.append(self.statement())
            self.skip_separators()
        return ProgramNode(span=self.merge(start, self.current.span), statements=statements)

    def parse_expression_only(self) -> Node:
        self.skip_separators()
        expression = self.expression()
        self.skip_separators()
        self.expect("EOF", "Expected the end of the expression.")
        return expression

    def statement(self) -> Node:
        if self.match("LET"):
            return self.let_statement(self.previous)
        if self.match("FUNCTION"):
            return self.function_declaration(self.previous)
        if self.match("RETURN"):
            return self.return_statement(self.previous)
        if self.match("IF"):
            return self.if_statement(self.previous)
        if self.match("WHILE"):
            return self.while_statement(self.previous)
        if self.match("FOR"):
            return self.for_statement(self.previous)
        if self.match("BREAK"):
            return BreakNode(span=self.previous.span)
        if self.match("CONTINUE"):
            return ContinueNode(span=self.previous.span)
        if self.match("CLASS"):
            return self.class_declaration(self.previous)
        if self.match("IMPORT"):
            return self.import_statement(self.previous)
        if self.match("FROM"):
            return self.from_import_statement(self.previous)
        if self.match("EXPORT"):
            return self.export_statement(self.previous)
        if self.check("TRY") and self.peek_type(1) == "LBRACE":
            start = self.advance()
            return self.try_statement(start)
        if self.match("THROW"):
            value = self.expression()
            return ThrowNode(span=self.merge(self.previous.span, value.span), value=value)
        if self.match("SHELL"):
            value = self.expression()
            return ShellNode(span=self.merge(self.previous.span, value.span), command=value)
        expression = self.expression()
        return ExpressionStatementNode(span=expression.span, expression=expression)

    def let_statement(self, start: Token) -> LetNode:
        annotation = None
        if self.match("LBRACKET"):
            target = self.list_pattern(self.previous)
        elif self.match("LBRACE"):
            target = self.object_pattern(self.previous)
        else:
            name = self.expect("IDENTIFIER", "Expected a variable name after 'let'.")
            target = IdentifierNode(span=name.span, name=name.value)
            if self.match("COLON"):
                annotation = self.type_annotation()
        self.expect("EQUAL", "Expected '=' after the variable declaration.")
        value = self.expression()
        return LetNode(span=self.merge(start.span, value.span), target=target, value=value, annotation=annotation)

    def list_pattern(self, start: Token) -> DestructureNode:
        items: list[tuple[str | None, str]] = []
        self.skip_separators()
        while not self.check("RBRACKET"):
            name = self.expect("IDENTIFIER", "Expected a name in the list destructuring pattern.")
            items.append((None, name.value))
            if not self.match("COMMA"):
                break
            self.skip_separators()
        end = self.expect("RBRACKET", "Expected ']' after the list destructuring pattern.")
        return DestructureNode(span=self.merge(start.span, end.span), kind="list", items=items)

    def object_pattern(self, start: Token) -> DestructureNode:
        items: list[tuple[str | None, str]] = []
        self.skip_separators()
        while not self.check("RBRACE"):
            key = self.expect_any(("IDENTIFIER", "STRING"), "Expected a field in the object destructuring pattern.")
            local_name = key.value
            if self.match("COLON"):
                local_name = self.expect("IDENTIFIER", "Expected a local name after ':'.").value
            items.append((str(key.value), str(local_name)))
            if not self.match("COMMA"):
                break
            self.skip_separators()
        end = self.expect("RBRACE", "Expected '}' after the object destructuring pattern.")
        return DestructureNode(span=self.merge(start.span, end.span), kind="object", items=items)

    def function_declaration(self, start: Token, *, exported: bool = False) -> FunctionNode:
        name = self.expect("IDENTIFIER", "Expected a function name.")
        parameters, return_type, body, end = self.function_tail()
        return FunctionNode(
            span=self.merge(start.span, end),
            name=name.value,
            parameters=parameters,
            body=body,
            return_type=return_type,
            exported=exported,
        )

    def function_tail(self) -> tuple[list[Parameter], TypeAnnotationNode | None, BlockNode, SourceSpan]:
        self.expect("LPAREN", "Expected '(' before function parameters.")
        parameters: list[Parameter] = []
        self.skip_separators()
        while not self.check("RPAREN"):
            variadic = self.match("ELLIPSIS")
            token = self.expect("IDENTIFIER", "Expected a parameter name.")
            annotation = self.type_annotation() if self.match("COLON") else None
            default = self.expression() if self.match("EQUAL") else None
            parameters.append(Parameter(token.value, token.span, annotation, default, variadic))
            if variadic and not self.check("RPAREN"):
                self.error(self.current, "A variadic parameter must be the final parameter.")
            if not self.match("COMMA"):
                break
            self.skip_separators()
        self.expect("RPAREN", "Expected ')' after function parameters.")
        return_type = self.type_annotation() if self.match("ARROW") else None
        body = self.block("Expected '{' before the function body.")
        return parameters, return_type, body, body.span

    def return_statement(self, start: Token) -> ReturnNode:
        if self.check_any("NEWLINE", "SEMICOLON", "RBRACE", "EOF"):
            return ReturnNode(span=start.span, value=None)
        value = self.coalesce()
        condition = None
        if self.match("IF"):
            condition = self.coalesce()
            if self.match("ELSE"):
                fallback = self.conditional()
                value = ConditionalExpressionNode(
                    span=self.merge(value.span, fallback.span),
                    condition=condition,
                    then_value=value,
                    else_value=fallback,
                )
                condition = None
        end = condition.span if condition else value.span
        return ReturnNode(span=self.merge(start.span, end), value=value, condition=condition)

    def if_statement(self, start: Token) -> IfNode:
        condition = self.expression()
        body = self.block("Expected '{' after the if condition.")
        branches = [(condition, body)]
        self.skip_separators()
        while self.match("ELIF"):
            condition = self.expression()
            branch = self.block("Expected '{' after the elif condition.")
            branches.append((condition, branch))
            self.skip_separators()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.block("Expected '{' after else.")
        end = else_branch.span if else_branch else branches[-1][1].span
        return IfNode(span=self.merge(start.span, end), branches=branches, else_branch=else_branch)

    def while_statement(self, start: Token) -> WhileNode:
        condition = self.expression()
        body = self.block("Expected '{' after the while condition.")
        return WhileNode(span=self.merge(start.span, body.span), condition=condition, body=body)

    def for_statement(self, start: Token) -> ForNode:
        name = self.expect("IDENTIFIER", "Expected a loop variable after 'for'.")
        target = IdentifierNode(span=name.span, name=name.value)
        self.expect("IN", "Expected 'in' after the loop variable.")
        iterable = self.expression()
        body = self.block("Expected '{' after the for iterable.")
        return ForNode(span=self.merge(start.span, body.span), target=target, iterable=iterable, body=body)

    def class_declaration(self, start: Token, *, exported: bool = False) -> ClassNode:
        name = self.expect("IDENTIFIER", "Expected a class name.")
        constructor_parameters: list[Parameter] = []
        if self.match("LPAREN"):
            self.skip_separators()
            while not self.check("RPAREN"):
                param = self.expect("IDENTIFIER", "Expected a constructor field name.")
                annotation = self.type_annotation() if self.match("COLON") else None
                default = self.expression() if self.match("EQUAL") else None
                constructor_parameters.append(Parameter(param.value, param.span, annotation, default))
                if not self.match("COMMA"):
                    break
                self.skip_separators()
            self.expect("RPAREN", "Expected ')' after constructor fields.")
        superclass = self.expect("IDENTIFIER", "Expected a superclass name after 'extends'.").value if self.match("EXTENDS") else None
        self.expect("LBRACE", "Expected '{' before the class body.")
        methods: list[FunctionNode] = []
        self.skip_separators()
        while not self.check("RBRACE") and not self.check("EOF"):
            fn = self.expect("FUNCTION", "Classes may contain function methods.")
            method = self.function_declaration(fn)
            methods.append(method)
            self.skip_separators()
        end = self.expect("RBRACE", "Expected '}' after the class body.")
        return ClassNode(
            span=self.merge(start.span, end.span),
            name=name.value,
            constructor_parameters=constructor_parameters,
            superclass=superclass,
            methods=methods,
            exported=exported,
        )

    def import_statement(self, start: Token) -> ImportNode:
        module = self.dotted_name()
        alias = self.expect("IDENTIFIER", "Expected an alias after 'as'.").value if self.match("AS") else None
        return ImportNode(span=self.merge(start.span, self.previous.span), module=module, alias=alias)

    def from_import_statement(self, start: Token) -> ImportNode:
        module = self.dotted_name()
        self.expect("IMPORT", "Expected 'import' after the module name.")
        names: list[tuple[str, str | None]] = []
        while True:
            name = self.expect("IDENTIFIER", "Expected an imported member name.")
            alias = self.expect("IDENTIFIER", "Expected an alias after 'as'.").value if self.match("AS") else None
            names.append((name.value, alias))
            if not self.match("COMMA"):
                break
        return ImportNode(span=self.merge(start.span, self.previous.span), module=module, names=names)

    def export_statement(self, start: Token) -> ExportNode:
        default = self.match("DEFAULT")
        if self.match("FUNCTION"):
            declaration: Node = self.function_declaration(self.previous, exported=True)
        elif self.match("CLASS"):
            declaration = self.class_declaration(self.previous, exported=True)
        elif self.match("LET"):
            declaration = self.let_statement(self.previous)
        else:
            declaration = self.expression()
        return ExportNode(span=self.merge(start.span, declaration.span), declaration=declaration, default=default)

    def try_statement(self, start: Token) -> TryNode:
        opening = self.expect("LBRACE", "Expected '{' after 'try'.")
        body = self.block_after_open(opening)
        self.skip_separators()
        self.expect("CATCH", "Expected 'catch' after the try block.")
        name = self.expect("IDENTIFIER", "Expected an error variable after 'catch'.")
        catch_body = self.block("Expected '{' after the catch variable.")
        return TryNode(
            span=self.merge(start.span, catch_body.span),
            body=body,
            error_name=name.value,
            catch_body=catch_body,
        )

    def block(self, message: str) -> BlockNode:
        start = self.expect("LBRACE", message)
        return self.block_after_open(start)

    def block_after_open(self, start: Token) -> BlockNode:
        statements: list[Node] = []
        self.skip_separators()
        while not self.check("RBRACE") and not self.check("EOF"):
            statements.append(self.statement())
            self.skip_separators()
        end = self.expect("RBRACE", "Expected '}' after the block.")
        return BlockNode(span=self.merge(start.span, end.span), statements=statements)

    def expression(self) -> Node:
        return self.assignment()

    def assignment(self) -> Node:
        if self.is_lambda_start():
            return self.lambda_expression()
        left = self.conditional()
        if self.current.type in ASSIGNMENT_TYPES:
            operator = self.advance()
            value = self.assignment()
            if not isinstance(left, (IdentifierNode, PropertyNode, SafePropertyNode, IndexNode)):
                self.error(operator, "The left side of an assignment must be a variable, property, or index.")
            return AssignmentNode(span=self.merge(left.span, value.span), target=left, value=value, operator=operator.value)
        return left

    def conditional(self) -> Node:
        then_value = self.coalesce()
        if self.match("IF"):
            condition = self.coalesce()
            self.expect("ELSE", "Expected 'else' in the conditional expression.")
            else_value = self.conditional()
            return ConditionalExpressionNode(
                span=self.merge(then_value.span, else_value.span),
                condition=condition,
                then_value=then_value,
                else_value=else_value,
            )
        return then_value

    def coalesce(self) -> Node:
        expression = self.logical_or()
        while self.match("COALESCE"):
            operator = self.previous
            right = self.logical_or()
            expression = BinaryNode(span=self.merge(expression.span, right.span), left=expression, operator=operator.value, right=right)
        return expression

    def logical_or(self) -> Node:
        return self.binary(self.logical_and, {"OR"})

    def logical_and(self) -> Node:
        return self.binary(self.equality, {"AND"})

    def equality(self) -> Node:
        return self.binary(self.comparison, {"EQUAL_EQUAL", "BANG_EQUAL", "IS"})

    def comparison(self) -> Node:
        return self.binary(self.range_expression, {"GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL", "IN"})

    def range_expression(self) -> Node:
        expression = self.term()
        if self.match("RANGE"):
            end = self.term()
            return RangeNode(span=self.merge(expression.span, end.span), start=expression, end=end)
        return expression

    def term(self) -> Node:
        return self.binary(self.factor, {"PLUS", "MINUS"})

    def factor(self) -> Node:
        return self.binary(self.unary, {"STAR", "SLASH", "PERCENT"})

    def binary(self, operand_parser, operators: set[str]) -> Node:
        expression = operand_parser()
        while self.current.type in operators:
            operator = self.advance()
            right = operand_parser()
            expression = BinaryNode(span=self.merge(expression.span, right.span), left=expression, operator=operator.value, right=right)
        return expression

    def unary(self) -> Node:
        if self.match("BANG", "NOT", "MINUS", "PLUS"):
            operator = self.previous
            operand = self.unary()
            return UnaryNode(span=self.merge(operator.span, operand.span), operator=operator.value, operand=operand)
        return self.power()

    def power(self) -> Node:
        expression = self.postfix()
        if self.match("POWER"):
            operator = self.previous
            right = self.unary()
            return BinaryNode(span=self.merge(expression.span, right.span), left=expression, operator=operator.value, right=right)
        return expression

    def postfix(self) -> Node:
        expression = self.primary()
        while True:
            if self.match("LPAREN"):
                arguments: list[CallArgument] = []
                self.skip_separators()
                while not self.check("RPAREN"):
                    name = None
                    if self.check("IDENTIFIER") and self.peek_type(1) == "COLON":
                        name = self.advance().value
                        self.advance()
                    arguments.append(CallArgument(self.expression(), name))
                    if not self.match("COMMA"):
                        break
                    self.skip_separators()
                self.skip_separators()
                end = self.expect("RPAREN", "Expected ')' after call arguments.")
                expression = CallNode(span=self.merge(expression.span, end.span), callee=expression, arguments=arguments)
            elif self.match("DOT", "SAFE_DOT"):
                operator = self.previous
                name = self.expect("IDENTIFIER", "Expected a property name after '.'.")
                node_type = SafePropertyNode if operator.type == "SAFE_DOT" else PropertyNode
                expression = node_type(span=self.merge(expression.span, name.span), target=expression, name=name.value)
            elif self.match("LBRACKET"):
                opening = self.previous
                self.skip_separators()
                start = None if self.check("RANGE") else self.expression()
                if self.match("RANGE"):
                    end_value = None if self.check("RBRACKET") else self.expression()
                    self.skip_separators()
                    end = self.expect("RBRACKET", "Expected ']' after the slice.")
                    expression = SliceNode(span=self.merge(expression.span, end.span), target=expression, start=start, end=end_value)
                else:
                    if start is None:
                        self.error(opening, "Expected an index expression before ']'.", "Use a valid index such as scores[0].")
                    self.skip_separators()
                    end = self.expect("RBRACKET", "Expected ']' after the index expression.")
                    expression = IndexNode(span=self.merge(expression.span, end.span), target=expression, index=start)
            else:
                break
        return expression

    def primary(self) -> Node:
        if self.match("INTEGER", "FLOAT", "STRING"):
            return LiteralNode(span=self.previous.span, value=self.previous.value)
        if self.match("TRUE"):
            return LiteralNode(span=self.previous.span, value=True)
        if self.match("FALSE"):
            return LiteralNode(span=self.previous.span, value=False)
        if self.match("NULL"):
            return LiteralNode(span=self.previous.span, value=None)
        if self.match("IDENTIFIER", "SELF"):
            return IdentifierNode(span=self.previous.span, name=self.previous.value)
        if self.match("LBRACKET"):
            start = self.previous
            items = self.comma_values("RBRACKET")
            self.skip_separators()
            end = self.expect("RBRACKET", "Expected ']' after the list literal.")
            return ListNode(span=self.merge(start.span, end.span), items=items)
        if self.match("LBRACE"):
            return self.object_literal(self.previous)
        if self.match("LPAREN"):
            start = self.previous
            self.skip_separators()
            if self.match("RPAREN"):
                return TupleNode(span=self.merge(start.span, self.previous.span), items=[])
            first = self.expression()
            if self.match("COMMA"):
                items = [first]
                self.skip_separators()
                while not self.check("RPAREN"):
                    items.append(self.expression())
                    if not self.match("COMMA"):
                        break
                    self.skip_separators()
                self.skip_separators()
                end = self.expect("RPAREN", "Expected ')' after the tuple literal.")
                return TupleNode(span=self.merge(start.span, end.span), items=items)
            self.expect("RPAREN", "Expected ')' after the grouped expression.")
            return first
        if self.match("FUNCTION"):
            start = self.previous
            name = self.advance().value if self.check("IDENTIFIER") and self.peek_type(1) == "LPAREN" else None
            parameters, return_type, body, end = self.function_tail()
            return FunctionNode(span=self.merge(start.span, end), name=name, parameters=parameters, body=body, return_type=return_type)
        if self.match("TRY"):
            start = self.previous
            expression = self.postfix()
            self.expect("ELSE", "Expected 'else' in the try fallback expression.")
            fallback = self.expression()
            return TryExpressionNode(span=self.merge(start.span, fallback.span), expression=expression, fallback=fallback)
        self.error(self.current, "Expected an expression.", "Add a literal, variable name, function call, list, or object expression.")

    def object_literal(self, start: Token) -> ObjectNode:
        entries: list[tuple[str, Node]] = []
        self.skip_separators()
        while not self.check("RBRACE"):
            key = self.expect_any(("IDENTIFIER", "STRING"), "Expected an object field name.")
            self.expect("COLON", "Expected ':' after the object field name.")
            entries.append((str(key.value), self.expression()))
            if not self.match("COMMA"):
                break
            self.skip_separators()
        self.skip_separators()
        end = self.expect("RBRACE", "Expected '}' after the object literal.")
        return ObjectNode(span=self.merge(start.span, end.span), entries=entries)

    def lambda_expression(self) -> LambdaNode:
        start = self.current.span
        parameters: list[Parameter] = []
        if self.match("IDENTIFIER"):
            parameters.append(Parameter(self.previous.value, self.previous.span))
        else:
            self.expect("LPAREN", "Expected '(' before lambda parameters.")
            self.skip_separators()
            while not self.check("RPAREN"):
                name = self.expect("IDENTIFIER", "Expected a lambda parameter name.")
                parameters.append(Parameter(name.value, name.span))
                if not self.match("COMMA"):
                    break
                self.skip_separators()
            self.expect("RPAREN", "Expected ')' after lambda parameters.")
        self.expect("FAT_ARROW", "Expected '=>' after lambda parameters.")
        body = self.block("Expected a lambda body.") if self.check("LBRACE") else self.expression()
        return LambdaNode(span=self.merge(start, body.span), parameters=parameters, body=body)

    def is_lambda_start(self) -> bool:
        if self.check("IDENTIFIER") and self.peek_type(1) == "FAT_ARROW":
            return True
        if not self.check("LPAREN"):
            return False
        depth = 0
        cursor = self.index
        while cursor < len(self.tokens):
            token_type = self.tokens[cursor].type
            if token_type == "LPAREN":
                depth += 1
            elif token_type == "RPAREN":
                depth -= 1
                if depth == 0:
                    return cursor + 1 < len(self.tokens) and self.tokens[cursor + 1].type == "FAT_ARROW"
            elif token_type not in {"IDENTIFIER", "COMMA", "COLON", "QUESTION"} and depth == 1:
                return False
            cursor += 1
        return False

    def comma_values(self, terminator: str) -> list[Node]:
        values: list[Node] = []
        self.skip_separators()
        while not self.check(terminator):
            values.append(self.expression())
            if not self.match("COMMA"):
                break
            self.skip_separators()
        return values

    def type_annotation(self) -> TypeAnnotationNode:
        start = self.expect("IDENTIFIER", "Expected a type name.")
        arguments: list[TypeAnnotationNode] = []
        if self.match("LESS"):
            self.skip_separators()
            while not self.check("GREATER"):
                arguments.append(self.type_annotation())
                if not self.match("COMMA"):
                    break
                self.skip_separators()
            end = self.expect("GREATER", "Expected '>' after generic type arguments.")
        else:
            end = start
        nullable = self.match("QUESTION")
        if nullable:
            end = self.previous
        return TypeAnnotationNode(span=self.merge(start.span, end.span), name=start.value, arguments=arguments, nullable=nullable)

    def dotted_name(self) -> str:
        parts = [self.expect("IDENTIFIER", "Expected a module name.").value]
        while self.match("DOT"):
            parts.append(self.expect("IDENTIFIER", "Expected a module name after '.'.").value)
        return ".".join(parts)

    def skip_separators(self) -> None:
        while self.match("NEWLINE", "SEMICOLON"):
            pass

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    @property
    def previous(self) -> Token:
        return self.tokens[self.index - 1]

    def peek_type(self, distance: int) -> str:
        position = min(self.index + distance, len(self.tokens) - 1)
        return self.tokens[position].type

    def check(self, token_type: str) -> bool:
        return self.current.type == token_type

    def check_any(self, *token_types: str) -> bool:
        return self.current.type in token_types

    def match(self, *token_types: str) -> bool:
        if self.current.type in token_types:
            self.index += 1
            return True
        return False

    def advance(self) -> Token:
        token = self.current
        if token.type != "EOF":
            self.index += 1
        return token

    def expect(self, token_type: str, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        self.error(self.current, message)

    def expect_any(self, token_types: tuple[str, ...], message: str) -> Token:
        if self.current.type in token_types:
            return self.advance()
        self.error(self.current, message)

    def error(self, token: Token, message: str, suggestion: str | None = None):
        raise SovaSyntaxError(message, token.span, source=self.source, suggestion=suggestion)

    @staticmethod
    def merge(start: SourceSpan, end: SourceSpan) -> SourceSpan:
        return SourceSpan(start.filename, start.line, start.column, end.end_line, end.end_column, start.start, end.end)


def parse(source: str, filename: str = "<source>") -> ProgramNode:
    return Parser(source, filename).parse()
