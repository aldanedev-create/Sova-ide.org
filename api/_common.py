from __future__ import annotations

"""Shared validation and AST-only execution for Sova Vercel functions."""

import io
import json
import os
import re
import sys
import time
from http.server import BaseHTTPRequestHandler
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sova_engine.ast_nodes import node_to_data
from sova_engine.diagnostics import Diagnostic, SovaError, SovaRuntimeError, SourceSpan
from sova_engine.execution_policy import ExecutionPolicy
from sova_engine.formatter import format_source
from sova_engine.interpreter import Interpreter
from sova_engine.lexer import tokenize
from sova_engine.module_loader import ModuleLoader
from sova_engine.parser import Parser
from sova_engine.semantic_analyzer import SemanticAnalyzer


MAX_REQUEST_BYTES = 1_100_000
DEFAULT_ORIGINS = {
    "https://sova-lang.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}
FILENAME_RE = re.compile(r"^[A-Za-z0-9_./-]+\.sova$")


class RequestError(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status


def allowed_origins() -> set[str]:
    configured = {item.strip() for item in os.getenv("SOVA_CORS_ORIGINS", "").split(",") if item.strip()}
    return configured or DEFAULT_ORIGINS


def normalize_filename(value: str) -> str:
    if not isinstance(value, str) or not FILENAME_RE.fullmatch(value):
        raise RequestError(f"Invalid Sova filename: {value!r}")
    normalized = PurePosixPath(value).as_posix()
    if normalized.startswith("/") or ".." in PurePosixPath(normalized).parts or ":" in normalized or "\\" in normalized:
        raise RequestError(f"Project path traversal is not allowed: {value!r}")
    return normalized


def read_request(handler: BaseHTTPRequestHandler) -> tuple[str, dict[str, str], dict[str, Any]]:
    try:
        length = int(handler.headers.get("content-length", "0") or "0")
    except ValueError as error:
        raise RequestError("Invalid Content-Length header") from error
    if length <= 0 or length > MAX_REQUEST_BYTES:
        raise RequestError("Request body is empty or too large", 413)
    try:
        payload = json.loads(handler.rfile.read(length).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RequestError("Request body must be valid UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise RequestError("Request JSON must be an object")
    files_value = payload.get("files")
    if not isinstance(files_value, dict) or not files_value:
        raise RequestError("files must be a non-empty object")
    policy = ExecutionPolicy.online()
    if len(files_value) > policy.max_files:
        raise RequestError(f"A project may contain at most {policy.max_files} files", 413)
    files: dict[str, str] = {}
    total = 0
    for raw_name, source in files_value.items():
        name = normalize_filename(raw_name)
        if not isinstance(source, str):
            raise RequestError(f"Source for {name} must be a string")
        size = len(source.encode("utf-8"))
        if size > policy.max_file_bytes:
            raise RequestError(f"{name} exceeds the per-file size limit", 413)
        total += size
        files[name] = source
    if total > policy.max_source_bytes:
        raise RequestError("Project source exceeds the online size limit", 413)
    entry = normalize_filename(payload.get("entry", "main.sova"))
    if entry not in files:
        raise RequestError(f"Entry file '{entry}' is not present")
    options = payload.get("options") or {}
    if not isinstance(options, dict):
        raise RequestError("options must be an object")
    return entry, files, options


def restricted_policy(options: dict[str, Any]) -> ExecutionPolicy:
    policy = ExecutionPolicy.online()
    requested_steps = options.get("max_steps")
    requested_runtime = options.get("timeout_ms")
    if isinstance(requested_steps, int) and requested_steps > 0:
        policy.max_steps = min(policy.max_steps, requested_steps)
    if isinstance(requested_runtime, int) and requested_runtime > 0:
        policy.max_runtime_ms = min(policy.max_runtime_ms, requested_runtime)
    return policy


def run_project(entry: str, files: dict[str, str], options: dict[str, Any]) -> dict[str, Any]:
    output: list[str] = []
    policy = restricted_policy(options)
    loader = ModuleLoader(virtual_files=files)
    interpreter = Interpreter(policy=policy, writer=output.append, virtual_files=files, module_loader=loader)
    started = time.perf_counter()
    try:
        interpreter.run(files[entry], entry)
        return {
            "success": True,
            "stdout": "".join(output),
            "stderr": "",
            "diagnostics": [],
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "steps": interpreter.limits.steps,
        }
    except SovaError as error:
        return {
            "success": False,
            "stdout": "".join(output),
            "stderr": error.message,
            "diagnostics": [error.diagnostic().to_dict()],
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "steps": interpreter.limits.steps,
        }


def check_project(entry: str, files: dict[str, str]) -> dict[str, Any]:
    try:
        program = Parser(files[entry], entry).parse()
        report = SemanticAnalyzer().analyze(program)
        return {"success": report.ok, "diagnostics": [item.to_dict() for item in report.diagnostics]}
    except SovaError as error:
        return {"success": False, "diagnostics": [error.diagnostic().to_dict()]}


def token_payload(entry: str, files: dict[str, str]) -> dict[str, Any]:
    return {"success": True, "tokens": [token.to_dict() for token in tokenize(files[entry], entry)]}


def ast_payload(entry: str, files: dict[str, str]) -> dict[str, Any]:
    return {"success": True, "ast": node_to_data(Parser(files[entry], entry).parse())}


def format_payload(entry: str, files: dict[str, str]) -> dict[str, Any]:
    Parser(files[entry], entry).parse()
    return {"success": True, "source": format_source(files[entry])}


def explain_payload(entry: str, files: dict[str, str]) -> dict[str, Any]:
    program = Parser(files[entry], entry).parse()
    report = SemanticAnalyzer().analyze(program)
    return {
        "success": report.ok,
        "summary": f"{entry} contains {len(program.statements)} top-level statements and produces one Sova AST.",
        "pipeline": ["lexer", "tokens", "parser", "AST", "semantic analysis", "restricted interpreter"],
        "diagnostics": [item.to_dict() for item in report.diagnostics],
    }


def send_json(handler: BaseHTTPRequestHandler, payload: dict[str, Any], status: int = 200) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    origin = handler.headers.get("origin", "")
    handler.send_response(status)
    handler.send_header("content-type", "application/json; charset=utf-8")
    handler.send_header("cache-control", "no-store")
    if origin in allowed_origins():
        handler.send_header("access-control-allow-origin", origin)
        handler.send_header("vary", "Origin")
    handler.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
    handler.send_header("access-control-allow-headers", "content-type")
    handler.send_header("x-content-type-options", "nosniff")
    handler.send_header("content-length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def handle_post(handler: BaseHTTPRequestHandler, operation) -> None:
    try:
        entry, files, options = read_request(handler)
        payload = operation(entry, files, options) if operation is run_project else operation(entry, files)
        send_json(handler, payload)
    except RequestError as error:
        send_json(handler, {"success": False, "error": str(error)}, error.status)
    except SovaError as error:
        send_json(handler, {"success": False, "diagnostics": [error.diagnostic().to_dict()]})
    except Exception:
        send_json(handler, {"success": False, "error": "The Sova service could not process this request."}, 500)


def handle_options(handler: BaseHTTPRequestHandler) -> None:
    send_json(handler, {"success": True})
