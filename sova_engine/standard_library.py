from __future__ import annotations

"""Bind NovaDev's canonical library objects under the separate Sova namespace."""

from types import SimpleNamespace
from typing import Any, Iterable

from novadev.standard_library import nova_root

from .diagnostics import LibraryError, SourceSpan
from .execution_policy import ExecutionPolicy


class BlockedLibrary:
    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason

    def reject(self, member: str) -> None:
        raise LibraryError(
            f"{self.name}.{member} is disabled: {self.reason}.",
            SourceSpan.synthetic("<standard-library>"),
            suggestion="Run locally with an explicit capability policy if this operation is required.",
        )

    def __getattr__(self, member: str):
        if member.startswith("__") and member.endswith("__"):
            raise AttributeError(member)
        self.reject(member)


class LibraryFacade(BlockedLibrary):
    """Expose an approved subset of a canonical Nova library object."""

    def __init__(self, name: str, members: dict[str, Any], reason: str) -> None:
        super().__init__(name, reason)
        self.members = members

    def __getattr__(self, member: str) -> Any:
        if member in self.members:
            return self.members[member]
        return super().__getattr__(member)


class SovaRoot(SimpleNamespace):
    """Library root carrying the exact host members approved for this policy."""

    def __init__(
        self,
        values: dict[str, Any],
        bindings: list[tuple[Any, str, dict[str, Any], str]],
    ) -> None:
        super().__init__(**values)
        self._bindings: dict[int, tuple[Any, str, dict[str, Any], str]] = {}
        self._register(self, "Sova", values, "it is not part of the public Sova library API")
        for owner, name, members, reason in bindings:
            self._register(owner, name, members, reason)

    def _register(self, owner: Any, name: str, members: dict[str, Any], reason: str) -> None:
        self._bindings[id(owner)] = (owner, name, members, reason)

    def resolve_member(self, owner: Any, member: str) -> tuple[bool, Any]:
        binding = self._bindings.get(id(owner))
        if binding is None or binding[0] is not owner:
            return False, None
        _, name, members, reason = binding
        if member not in members:
            raise LibraryError(
                f"{name}.{member} is disabled: {reason}.",
                SourceSpan.synthetic("<standard-library>"),
                suggestion="Use a public Sova library member allowed by the active capability policy.",
            )
        return True, members[member]


class VirtualFiles:
    def __init__(self, files: dict[str, str]) -> None:
        self.files = files

    def read(self, path: str) -> str:
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]

    def exists(self, path: str) -> bool:
        return path in self.files

    def list(self) -> list[str]:
        return sorted(self.files)


def _member_map(target: Any, names: Iterable[str]) -> dict[str, Any]:
    return {name: getattr(target, name) for name in names}


def sova_root(policy: ExecutionPolicy, virtual_files: dict[str, str] | None = None) -> SovaRoot:
    """Return policy-filtered aliases to Nova's canonical implementation objects."""

    nova = nova_root()
    bindings: list[tuple[Any, str, dict[str, Any], str]] = []

    def expose(
        name: str,
        target: Any,
        public_names: Iterable[str],
        allowed_names: Iterable[str] | None = None,
        *,
        reason: str = "the member is not part of the public Sova library API",
    ) -> Any:
        public = tuple(public_names)
        allowed = public if allowed_names is None else tuple(allowed_names)
        members = _member_map(target, allowed)
        if not members:
            owner: Any = BlockedLibrary(name, reason)
        elif set(allowed) == set(public):
            owner = target
        else:
            owner = LibraryFacade(name, members, reason)
        bindings.append((owner, name, members, reason))
        return owner

    file_reason = "the required local file capability is unavailable"
    file_read = policy.allow_local_file_read
    file_write = policy.allow_file_write

    file_public = ("read", "write", "append", "delete", "copy", "move", "mkdir", "exists", "list")
    file_allowed: list[str] = []
    if file_read:
        file_allowed.extend(("read", "exists", "list"))
    if file_write:
        file_allowed.extend(("write", "append", "delete", "mkdir"))
    if file_read and file_write:
        file_allowed.extend(("copy", "move"))

    json_public = ("parse", "stringify", "pretty", "read", "write")
    json_allowed = ["parse", "stringify", "pretty"]
    if file_read:
        json_allowed.append("read")
    if file_write:
        json_allowed.append("write")

    csv_public = ("read", "write", "append")
    csv_allowed: list[str] = []
    if file_read:
        csv_allowed.append("read")
    if file_write:
        csv_allowed.extend(("write", "append"))

    path_public = ("join", "exists", "name")
    path_allowed = ["join", "name"]
    if file_read:
        path_allowed.append("exists")

    http_public = ("get", "post", "put", "delete", "download", "request")
    http_allowed: list[str] = []
    if policy.allow_network:
        http_allowed.extend(("get", "post", "put", "delete", "request"))
        if file_write:
            http_allowed.append("download")

    database_allowed = ("connect", "query", "execute", "insert", "table") if file_read and file_write else ()

    collections = SimpleNamespace(sum=sum, min=min, max=max, sorted=sorted)
    strings = SimpleNamespace(join=lambda separator, values: separator.join(map(str, values)))
    virtual = VirtualFiles(virtual_files or {})

    values = {
        "Math": expose("Sova.Math", nova.math, ("round", "sqrt", "floor", "ceil", "percent", "avg", "min", "max", "clamp")),
        "Files": expose("Sova.Files", nova.files, file_public, file_allowed, reason=file_reason),
        "Json": expose("Sova.Json", nova.json, json_public, json_allowed, reason=file_reason),
        "Time": expose("Sova.Time", nova.time, ("now", "today", "format", "parse", "sleep")),
        "Random": expose(
            "Sova.Random",
            nova.random,
            ("random", "randint", "randrange", "choice", "choices", "sample", "shuffle", "uniform", "seed"),
        ),
        "Regex": expose("Sova.Regex", nova.regex, ("match", "replace", "findall")),
        "Crypto": expose(
            "Sova.Crypto",
            nova.crypto,
            ("md5", "sha256", "token", "hmac_sha256", "passwordHash", "verifyPassword"),
        ),
        "Csv": expose("Sova.Csv", nova.csv, csv_public, csv_allowed, reason=file_reason),
        "Path": expose("Sova.Path", nova.path, path_public, path_allowed, reason=file_reason),
        "Http": expose(
            "Sova.Http",
            nova.http,
            http_public,
            http_allowed,
            reason="the required network or file-write capability is unavailable",
        ),
        "Statistics": expose("Sova.Statistics", nova.statistics, ("mean", "median", "mode", "variance", "stdev")),
        "Email": expose(
            "Sova.Email",
            nova.email,
            ("message", "send"),
            ("message", "send") if policy.allow_network else (),
            reason="network access is unavailable",
        ),
        "Database": expose(
            "Sova.Database",
            nova.sqlite,
            ("connect", "query", "execute", "insert", "table"),
            database_allowed,
            reason=file_reason,
        ),
        "VirtualFiles": expose("Sova.VirtualFiles", virtual, ("read", "exists", "list")),
        "Collections": expose("Sova.Collections", collections, ("sum", "min", "max", "sorted")),
        "Strings": expose("Sova.Strings", strings, ("join",)),
    }
    return SovaRoot(values, bindings)


LIBRARY_NAMES = [
    "Sova.Math",
    "Sova.Files",
    "Sova.Json",
    "Sova.Time",
    "Sova.Random",
    "Sova.Regex",
    "Sova.Crypto",
    "Sova.Csv",
    "Sova.Path",
    "Sova.Http",
    "Sova.Statistics",
    "Sova.VirtualFiles",
    "Sova.Collections",
    "Sova.Strings",
]
