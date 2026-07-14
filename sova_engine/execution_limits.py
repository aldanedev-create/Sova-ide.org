from __future__ import annotations

"""Step, time, call-depth, output, and collection limits."""

import time

from .diagnostics import ExecutionLimitError, SourceSpan
from .execution_policy import ExecutionPolicy


class ExecutionLimits:
    def __init__(self, policy: ExecutionPolicy) -> None:
        self.policy = policy
        self.reset()

    def reset(self) -> None:
        """Start a fresh execution budget while retaining the active policy."""
        self.steps = 0
        self.call_depth = 0
        self.output_bytes = 0
        self.started = time.monotonic()

    @property
    def duration_ms(self) -> float:
        return (time.monotonic() - self.started) * 1000

    def step(self, span: SourceSpan, amount: int = 1) -> None:
        self.steps += amount
        if self.steps > self.policy.max_steps:
            raise ExecutionLimitError(
                f"The program exceeded the execution limit of {self.policy.max_steps:,} steps.",
                span,
                suggestion="Check for an infinite loop, excessive recursion, or too much input data.",
            )
        if self.duration_ms > self.policy.max_runtime_ms:
            raise ExecutionLimitError(
                f"The program exceeded the runtime limit of {self.policy.max_runtime_ms:,} ms.",
                span,
                suggestion="Run the program locally with a larger policy or reduce the work it performs.",
            )

    def enter_call(self, span: SourceSpan) -> None:
        self.call_depth += 1
        if self.call_depth > self.policy.max_call_depth:
            raise ExecutionLimitError(
                f"The program exceeded the call-depth limit of {self.policy.max_call_depth}.",
                span,
                suggestion="Check recursive functions for a reachable base case.",
            )

    def leave_call(self) -> None:
        self.call_depth = max(0, self.call_depth - 1)

    def count_output(self, text: str, span: SourceSpan) -> None:
        self.output_bytes += len(text.encode("utf-8"))
        if self.output_bytes > self.policy.max_output_bytes:
            raise ExecutionLimitError(
                f"The program exceeded the output limit of {self.policy.max_output_bytes:,} bytes.",
                span,
                suggestion="Print less data or run the program locally with a larger output limit.",
            )

    def check_collection(self, value: object, span: SourceSpan) -> None:
        if isinstance(value, (list, tuple, dict, set)) and len(value) > self.policy.max_collection_items:
            raise ExecutionLimitError(
                f"A collection exceeded the limit of {self.policy.max_collection_items:,} items.",
                span,
            )
        if isinstance(value, str) and len(value) > self.policy.max_string_length:
            raise ExecutionLimitError(
                f"A string exceeded the limit of {self.policy.max_string_length:,} characters.",
                span,
            )
