from __future__ import annotations

"""The single source-to-token implementation used by Sova 0.1v."""

from .diagnostics import SourceSpan, SovaSyntaxError
from .tokens import KEYWORDS, Token


MULTI_OPERATORS = {
    "...": "ELLIPSIS",
    "?.": "SAFE_DOT",
    "??": "COALESCE",
    "**": "POWER",
    "+=": "PLUS_EQUAL",
    "-=": "MINUS_EQUAL",
    "*=": "STAR_EQUAL",
    "/=": "SLASH_EQUAL",
    "==": "EQUAL_EQUAL",
    "!=": "BANG_EQUAL",
    ">=": "GREATER_EQUAL",
    "<=": "LESS_EQUAL",
    "&&": "AND",
    "||": "OR",
    "=>": "FAT_ARROW",
    "->": "ARROW",
    "..": "RANGE",
}

SINGLE_TOKENS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "%": "PERCENT",
    "=": "EQUAL",
    "!": "BANG",
    ">": "GREATER",
    "<": "LESS",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ":": "COLON",
    ".": "DOT",
    ";": "SEMICOLON",
    "?": "QUESTION",
}


class Lexer:
    def __init__(self, source: str, filename: str = "<source>") -> None:
        self.source = source
        self.filename = filename
        self.index = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        while not self.at_end:
            start = self.index
            line = self.line
            column = self.column
            char = self.advance()

            if char in " \t\r":
                continue
            if char == "\n":
                self.add("NEWLINE", "\n", start, line, column)
                continue
            if char == "/" and self.peek() == "/":
                self.advance()
                while not self.at_end and self.peek() != "\n":
                    self.advance()
                continue
            if char == "/" and self.peek() == "*":
                self.advance()
                self.block_comment(start, line, column)
                continue
            if char in {'"', "'"}:
                self.string(char, start, line, column)
                continue
            if char.isdigit():
                self.number(start, line, column)
                continue
            if char.isalpha() or char == "_":
                self.identifier(start, line, column)
                continue

            matched = False
            for width in (3, 2):
                candidate = self.source[start : start + width]
                if candidate in MULTI_OPERATORS:
                    while self.index < start + width:
                        self.advance()
                    self.add(MULTI_OPERATORS[candidate], candidate, start, line, column)
                    matched = True
                    break
            if matched:
                continue
            token_type = SINGLE_TOKENS.get(char)
            if token_type:
                self.add(token_type, char, start, line, column)
                continue
            raise SovaSyntaxError(
                f"Unexpected character {char!r}.",
                self.span(start, line, column),
                source=self.source,
                suggestion="Remove the character or replace it with a supported Sova token.",
            )

        eof = SourceSpan(self.filename, self.line, self.column, self.line, self.column, self.index, self.index)
        self.tokens.append(Token("EOF", None, eof))
        return self.tokens

    @property
    def at_end(self) -> bool:
        return self.index >= len(self.source)

    def peek(self, distance: int = 0) -> str:
        position = self.index + distance
        return "\0" if position >= len(self.source) else self.source[position]

    def advance(self) -> str:
        char = self.source[self.index]
        self.index += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def span(self, start: int, line: int, column: int) -> SourceSpan:
        return SourceSpan(self.filename, line, column, self.line, self.column, start, self.index)

    def add(self, token_type: str, value: object, start: int, line: int, column: int) -> None:
        self.tokens.append(Token(token_type, value, self.span(start, line, column)))

    def block_comment(self, start: int, line: int, column: int) -> None:
        while not self.at_end:
            if self.peek() == "*" and self.peek(1) == "/":
                self.advance()
                self.advance()
                return
            self.advance()
        raise SovaSyntaxError(
            "Unterminated multi-line comment.",
            self.span(start, line, column),
            source=self.source,
            suggestion="Close the comment with */.",
        )

    def string(self, quote: str, start: int, line: int, column: int) -> None:
        value: list[str] = []
        escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", '"': '"', "'": "'"}
        while not self.at_end and self.peek() != quote:
            char = self.advance()
            if char == "\\":
                if self.at_end:
                    break
                escaped = self.advance()
                value.append(escapes.get(escaped, escaped))
            else:
                value.append(char)
        if self.at_end:
            raise SovaSyntaxError(
                "Unterminated string literal.",
                self.span(start, line, column),
                source=self.source,
                suggestion=f"Add a closing {quote} quote.",
            )
        self.advance()
        self.add("STRING", "".join(value), start, line, column)

    def number(self, start: int, line: int, column: int) -> None:
        while self.peek().isdigit() or self.peek() == "_":
            self.advance()
        is_float = False
        if self.peek() == "." and self.peek(1).isdigit():
            is_float = True
            self.advance()
            while self.peek().isdigit() or self.peek() == "_":
                self.advance()
        text = self.source[start : self.index].replace("_", "")
        self.add("FLOAT" if is_float else "INTEGER", float(text) if is_float else int(text), start, line, column)

    def identifier(self, start: int, line: int, column: int) -> None:
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        text = self.source[start : self.index]
        self.add(KEYWORDS.get(text, "IDENTIFIER"), text, start, line, column)


def tokenize(source: str, filename: str = "<source>") -> list[Token]:
    return Lexer(source, filename).tokenize()
