from __future__ import annotations

"""Capability and resource policies for local and online Sova execution."""

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionPolicy:
    allow_shell: bool = False
    allow_python_bridge: bool = False
    allow_network: bool = False
    allow_file_write: bool = False
    allow_local_file_read: bool = False
    allow_external_imports: bool = False
    max_source_bytes: int = 100_000
    max_files: int = 20
    max_file_bytes: int = 50_000
    max_ast_nodes: int = 50_000
    max_steps: int = 100_000
    max_call_depth: int = 100
    max_collection_items: int = 10_000
    max_string_length: int = 100_000
    max_output_bytes: int = 64_000
    max_runtime_ms: int = 2_000

    @classmethod
    def local(cls, *, allow_shell: bool = False) -> "ExecutionPolicy":
        return cls(
            allow_shell=allow_shell,
            allow_network=True,
            allow_file_write=True,
            allow_local_file_read=True,
            allow_external_imports=True,
            max_source_bytes=2_000_000,
            max_files=500,
            max_file_bytes=2_000_000,
            max_ast_nodes=500_000,
            max_steps=2_000_000,
            max_call_depth=500,
            max_collection_items=1_000_000,
            max_string_length=5_000_000,
            max_output_bytes=2_000_000,
            max_runtime_ms=30_000,
        )

    @classmethod
    def online(cls) -> "ExecutionPolicy":
        return cls()
