from __future__ import annotations

"""Token definitions for Sova's only lexer/parser pipeline."""

from dataclasses import dataclass
from typing import Any

from .diagnostics import SourceSpan


KEYWORDS = {
    "let": "LET",
    "function": "FUNCTION",
    "return": "RETURN",
    "if": "IF",
    "elif": "ELIF",
    "else": "ELSE",
    "for": "FOR",
    "while": "WHILE",
    "break": "BREAK",
    "continue": "CONTINUE",
    "class": "CLASS",
    "extends": "EXTENDS",
    "import": "IMPORT",
    "from": "FROM",
    "as": "AS",
    "export": "EXPORT",
    "default": "DEFAULT",
    "try": "TRY",
    "catch": "CATCH",
    "throw": "THROW",
    "in": "IN",
    "not": "NOT",
    "and": "AND",
    "or": "OR",
    "true": "TRUE",
    "false": "FALSE",
    "null": "NULL",
    "self": "SELF",
    "shell": "SHELL",
    "is": "IS",
}


@dataclass(frozen=True, slots=True)
class Token:
    type: str
    value: Any
    span: SourceSpan

    @property
    def line(self) -> int:
        return self.span.line

    @property
    def column(self) -> int:
        return self.span.column

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "file": self.span.filename,
            "line": self.span.line,
            "column": self.span.column,
            "endLine": self.span.end_line,
            "endColumn": self.span.end_column,
            "start": self.span.start,
            "end": self.span.end,
        }
