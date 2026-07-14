from __future__ import annotations

"""Source locations and beginner-friendly Sova diagnostics."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceSpan:
    filename: str
    line: int
    column: int
    end_line: int
    end_column: int
    start: int = 0
    end: int = 0

    @classmethod
    def synthetic(cls, filename: str = "<runtime>") -> "SourceSpan":
        return cls(filename, 1, 1, 1, 1)


@dataclass(slots=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    span: SourceSpan
    suggestion: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "file": self.span.filename,
            "line": self.span.line,
            "column": self.span.column,
            "endLine": self.span.end_line,
            "endColumn": self.span.end_column,
            "suggestion": self.suggestion,
        }


class SovaError(Exception):
    category = "Error"
    code = "SOVA_000"

    def __init__(
        self,
        message: str,
        span: SourceSpan | None = None,
        *,
        source: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.span = span or SourceSpan.synthetic()
        self.source = source
        self.suggestion = suggestion

    def diagnostic(self) -> Diagnostic:
        return Diagnostic(self.code, "error", self.message, self.span, self.suggestion)

    def pretty(self) -> str:
        location = f"{self.span.filename}:{self.span.line}:{self.span.column}"
        result = [f"{self.category} in {location}", ""]
        if self.source:
            lines = self.source.splitlines()
            if 1 <= self.span.line <= len(lines):
                excerpt = lines[self.span.line - 1]
                width = max(1, self.span.end_column - self.span.column)
                result.extend([excerpt, " " * (self.span.column - 1) + "^" * width, ""])
        result.append(self.message)
        if self.suggestion:
            result.extend(["", "Suggestion:", self.suggestion])
        return "\n".join(result)

    def __str__(self) -> str:
        return self.pretty()


class SovaSyntaxError(SovaError):
    category = "SyntaxError"
    code = "SOVA_SYNTAX_001"


class SovaNameError(SovaError):
    category = "NameError"
    code = "SOVA_NAME_001"


class SovaTypeError(SovaError):
    category = "TypeError"
    code = "SOVA_TYPE_001"


class SovaIndexError(SovaError):
    category = "IndexError"
    code = "SOVA_INDEX_001"


class SovaValueError(SovaError):
    category = "ValueError"
    code = "SOVA_VALUE_001"


class SovaImportError(SovaError):
    category = "ImportError"
    code = "SOVA_IMPORT_001"


class SovaFileError(SovaError):
    category = "FileError"
    code = "SOVA_FILE_001"


class SovaRuntimeError(SovaError):
    category = "RuntimeError"
    code = "SOVA_RUNTIME_001"


class ExecutionLimitError(SovaRuntimeError):
    category = "ExecutionLimitError"
    code = "SOVA_LIMIT_001"


class LibraryError(SovaRuntimeError):
    category = "LibraryError"
    code = "SOVA_LIBRARY_001"
