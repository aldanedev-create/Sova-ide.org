from __future__ import annotations

"""Command-line interface for the clean Sova 0.1v language package."""

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from .ast_nodes import node_to_data
from .diagnostics import SovaError
from .execution_policy import ExecutionPolicy
from .formatter import format_source
from .interpreter import Interpreter
from .lexer import tokenize
from .module_loader import ModuleLoader
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from .standard_library import LIBRARY_NAMES
from .version import DISPLAY_VERSION, __version__


ROOT = Path(__file__).resolve().parents[1]


def _resource_roots() -> tuple[Path, ...]:
    roots: list[Path] = []
    if getattr(sys, "frozen", False):
        executable_directory = Path(sys.executable).resolve().parent
        roots.append(executable_directory)
        if executable_directory.name.casefold() == "bin":
            roots.append(executable_directory.parent)

    roots.append(ROOT)
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        roots.append(Path(bundle_root))

    unique_roots: list[Path] = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in unique_roots:
            unique_roots.append(resolved)
    return tuple(unique_roots)


def _transient_bundle_root() -> Path | None:
    if not getattr(sys, "frozen", False):
        return None
    bundle_root_value = getattr(sys, "_MEIPASS", None)
    if not bundle_root_value:
        return None

    bundle_root = Path(bundle_root_value).resolve()
    executable_directory = Path(sys.executable).resolve().parent
    if bundle_root.name.casefold().startswith("_mei"):
        return bundle_root
    if bundle_root == executable_directory or bundle_root.is_relative_to(executable_directory):
        return None
    return bundle_root


def resource_path(*relative_parts: str | Path, persistent: bool = False) -> Path:
    """Resolve a resource in source, installed, portable, or frozen layouts."""
    if not relative_parts:
        raise ValueError("a relative resource path is required")
    relative_path = Path(*relative_parts)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(f"resource path must stay relative: {relative_path}")

    transient_root = _transient_bundle_root() if persistent else None
    candidates: list[Path] = []
    for root in _resource_roots():
        candidate = (root / relative_path).resolve()
        if transient_root and (candidate == transient_root or candidate.is_relative_to(transient_root)):
            continue
        candidates.append(candidate)
        if candidate.exists():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Sova resource not found: {relative_path} (searched: {searched})")


def read_source(path_value: str) -> tuple[Path, str]:
    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return path, path.read_text(encoding="utf-8")


def command_run(args) -> int:
    path, source = read_source(args.file)
    loader = ModuleLoader(path.parent)
    interpreter = Interpreter(policy=ExecutionPolicy.local(allow_shell=args.allow_shell), module_loader=loader)
    interpreter.run(source, str(path))
    return 0


def command_tokens(args) -> int:
    path, source = read_source(args.file)
    print(json.dumps([token.to_dict() for token in tokenize(source, str(path))], indent=2, ensure_ascii=False))
    return 0


def command_ast(args) -> int:
    path, source = read_source(args.file)
    print(json.dumps(node_to_data(Parser(source, str(path)).parse()), indent=2, ensure_ascii=False))
    return 0


def command_check(args) -> int:
    path, source = read_source(args.file)
    program = Parser(source, str(path)).parse()
    report = SemanticAnalyzer().analyze(program)
    for item in report.diagnostics:
        print(f"{item.severity}: {item.message} ({item.span.filename}:{item.span.line}:{item.span.column})")
    if report.ok:
        print(f"check passed: {path.name}")
        return 0
    return 1


def command_lint(args) -> int:
    return command_check(args)


def command_format(args) -> int:
    path, source = read_source(args.file)
    formatted = format_source(source)
    if args.check:
        if source != formatted:
            print(f"format needed: {path}")
            return 1
        print(f"format passed: {path}")
        return 0
    path.write_text(formatted, encoding="utf-8")
    print(f"formatted: {path}")
    return 0


def command_explain(args) -> int:
    path, source = read_source(args.file)
    program = Parser(source, str(path)).parse()
    counts = Counter(statement.__class__.__name__ for statement in program.statements)
    report = SemanticAnalyzer().analyze(program)
    print(f"Sova source: {path}")
    print(f"Tokens: {len(tokenize(source, str(path)))}")
    print(f"Top-level statements: {len(program.statements)}")
    print("Statement kinds: " + ", ".join(f"{name}={count}" for name, count in sorted(counts.items())))
    print(f"Semantic errors: {len(report.errors)}")
    print(f"Semantic warnings: {len(report.warnings)}")
    return 0 if report.ok else 1


def command_docs(_args) -> int:
    print(resource_path("docs", "language-overview.md", persistent=True))
    return 0


def command_libraries(_args) -> int:
    print("Sova 0.1v standard-library namespaces:")
    for name in LIBRARY_NAMES:
        print(f"  {name}")
    print("\nThese bind NovaDev's canonical implementation objects; they are not duplicate libraries.")
    return 0


def command_version(_args) -> int:
    print(f"Sova {DISPLAY_VERSION} ({__version__})")
    return 0


def command_new(args) -> int:
    root = Path(args.name).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    manifest = root / "Sova.toml"
    entry = root / "src" / "main.sova"
    if not manifest.exists():
        manifest.write_text(
            f'name = "{root.name}"\nversion = "0.1.0"\nentry = "src/main.sova"\nsova_version = ">=0.1"\n\nallow_shell = false\nallow_network = false\nallow_unsafe = false\n',
            encoding="utf-8",
        )
    if not entry.exists():
        entry.write_text(f'let project = "{root.name}"\nprint("Hello from {{project}}")\n', encoding="utf-8")
    print(f"created Sova project: {root}")
    return 0


def command_test(_args) -> int:
    tests = ROOT / "tests"
    completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(tests), "-p", "test_*.py", "-v"], check=False)
    return completed.returncode


def command_dev(args) -> int:
    path = Path(args.file).resolve()
    print(f"Sova dev mode: {path} (Ctrl+C to stop)")
    last_modified = 0.0
    try:
        while True:
            modified = path.stat().st_mtime
            if modified != last_modified:
                last_modified = modified
                print(f"\n--- running {path.name} ---")
                try:
                    command_run(argparse.Namespace(file=str(path), allow_shell=args.allow_shell))
                except Exception as error:  # noqa: BLE001 - dev mode keeps watching.
                    print(error)
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sova", description="Sova 0.1v programming language")
    subparsers = parser.add_subparsers(dest="command")

    run = subparsers.add_parser("run", help="Run a .sova program")
    run.add_argument("file")
    run.add_argument("--allow-shell", action="store_true")
    run.set_defaults(func=command_run)

    subparsers.add_parser("shell", help="Open the interactive shell")
    for name, handler in (("tokens", command_tokens), ("ast", command_ast), ("check", command_check), ("lint", command_lint), ("explain", command_explain)):
        command = subparsers.add_parser(name)
        command.add_argument("file")
        command.set_defaults(func=handler)

    formatting = subparsers.add_parser("format")
    formatting.add_argument("file")
    formatting.add_argument("--check", action="store_true")
    formatting.set_defaults(func=command_format)

    subparsers.add_parser("docs").set_defaults(func=command_docs)
    subparsers.add_parser("libraries").set_defaults(func=command_libraries)
    subparsers.add_parser("version").set_defaults(func=command_version)
    project = subparsers.add_parser("new")
    project.add_argument("name")
    project.set_defaults(func=command_new)
    subparsers.add_parser("test").set_defaults(func=command_test)
    development = subparsers.add_parser("dev")
    development.add_argument("file")
    development.add_argument("--allow-shell", action="store_true")
    development.set_defaults(func=command_dev)
    subparsers.add_parser("help")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "shell":
        from .shell import main as shell_main

        return shell_main()
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except SovaError as error:
        print(error.pretty(), file=sys.stderr)
        return 1
    except (FileNotFoundError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
