from __future__ import annotations

"""Local and virtual .sova module loading with caching and cycle detection."""

from pathlib import Path, PurePosixPath

from .diagnostics import ExecutionLimitError, SourceSpan, SovaImportError
from .execution_policy import ExecutionPolicy
from .runtime import SovaModule


class ModuleLoader:
    def __init__(self, root: Path | None = None, virtual_files: dict[str, str] | None = None) -> None:
        self.root = (root or Path.cwd()).resolve()
        self.virtual_files = virtual_files
        self.cache: dict[str, SovaModule] = {}
        self.loading: list[str] = []
        self.file_bytes: dict[str, int] = {}

    def normalize_module(self, module: str) -> str:
        if "://" in module or module.startswith(("/", "\\")) or ".." in module.split("."):
            raise SovaImportError(f"Invalid module path '{module}'.", SourceSpan.synthetic(module))
        path = PurePosixPath(*module.split(".")).with_suffix(".sova").as_posix()
        if path.startswith("../") or "/../" in path:
            raise SovaImportError(f"Module traversal is not allowed: '{module}'.", SourceSpan.synthetic(module))
        return path

    def ensure_import_allowed(self, module: str, policy: ExecutionPolicy) -> None:
        if self.virtual_files is None and not policy.allow_external_imports:
            raise SovaImportError(
                f"External module import '{module}' is disabled by the current Sova policy.",
                SourceSpan.synthetic(module),
                suggestion="Use submitted virtual modules or enable external imports for trusted local code.",
            )

    def ensure_file_size(self, source: str, filename: str, policy: ExecutionPolicy) -> int:
        size = len(source.encode("utf-8"))
        if size > policy.max_file_bytes:
            raise ExecutionLimitError(
                f"Module '{filename}' exceeds the {policy.max_file_bytes:,}-byte file limit.",
                SourceSpan.synthetic(filename),
            )
        return size

    def read(self, module: str, policy: ExecutionPolicy | None = None) -> tuple[str, str]:
        relative = self.normalize_module(module)
        if policy is not None:
            self.ensure_import_allowed(module, policy)
        if self.virtual_files is not None:
            if relative not in self.virtual_files:
                raise SovaImportError(f"Module '{module}' was not found in the submitted project.", SourceSpan.synthetic(relative))
            source = self.virtual_files[relative]
            if policy is not None:
                self.ensure_file_size(source, relative, policy)
            return source, relative
        path = (self.root / relative).resolve()
        if self.root not in path.parents:
            raise SovaImportError(f"Module '{module}' resolves outside the project.", SourceSpan.synthetic(relative))
        if not path.exists():
            raise SovaImportError(f"Module '{module}' was not found at {path}.", SourceSpan.synthetic(relative))
        if policy is not None and path.stat().st_size > policy.max_file_bytes:
            raise ExecutionLimitError(
                f"Module '{path}' exceeds the {policy.max_file_bytes:,}-byte file limit.",
                SourceSpan.synthetic(str(path)),
            )
        source = path.read_text(encoding="utf-8")
        if policy is not None:
            self.ensure_file_size(source, str(path), policy)
        return source, str(path)

    def load(self, module: str, parent_interpreter) -> SovaModule:
        policy = parent_interpreter.policy
        self.ensure_import_allowed(module, policy)
        if module in self.cache:
            if self.file_bytes.get(module, 0) > policy.max_file_bytes:
                raise ExecutionLimitError(
                    f"Module '{module}' exceeds the {policy.max_file_bytes:,}-byte file limit.",
                    SourceSpan.synthetic(module),
                )
            return self.cache[module]
        if module in self.loading:
            chain = " -> ".join([*self.loading, module])
            raise SovaImportError(f"Circular import detected: {chain}.", SourceSpan.synthetic(module))
        if len(self.cache) + len(self.loading) >= policy.max_files:
            raise ExecutionLimitError(
                f"The project exceeds the module limit of {policy.max_files:,} files.",
                SourceSpan.synthetic(module),
            )
        self.loading.append(module)
        try:
            source, filename = self.read(module, policy)
            self.file_bytes[module] = len(source.encode("utf-8"))
            from .interpreter import Interpreter

            child = Interpreter(
                policy=parent_interpreter.policy,
                writer=parent_interpreter.writer,
                input_reader=parent_interpreter.input_reader,
                virtual_files=parent_interpreter.virtual_files,
                module_loader=self,
                limits=parent_interpreter.limits,
                sova_library=parent_interpreter.sova_library,
            )
            child.run(source, filename)
            exported = child.exports or {
                name: value
                for name, value in child.globals.values.items()
                if name not in parent_interpreter.globals.values and not name.startswith("_")
            }
            result = SovaModule(module, exported)
            self.cache[module] = result
            return result
        finally:
            self.loading.pop()
