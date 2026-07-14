from __future__ import annotations

"""Persistent interactive Sova 0.1v shell."""

import json
from pathlib import Path

from .ast_nodes import node_to_data
from .diagnostics import SovaError
from .execution_policy import ExecutionPolicy
from .interpreter import Interpreter, format_value
from .lexer import tokenize
from .parser import Parser
from .version import DISPLAY_VERSION


HELP = """Shell commands:
  .load file.sova
  .tokens [code]
  .ast [code]
  .env
  .clear
  .help
  .exit"""


def _execute_source(interpreter: Interpreter, source: str, filename: str = "<shell>") -> None:
    interpreter.limits.reset()
    interpreter.run(source, filename, analyze=False)


def main() -> int:
    print(f"Sova {DISPLAY_VERSION} Interactive Shell")
    print("Type .help for commands and .exit to quit")
    interpreter = Interpreter(policy=ExecutionPolicy.local())
    buffer: list[str] = []
    balance = 0
    while True:
        try:
            prompt = "...> " if buffer else "sova> "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not buffer and line.strip().startswith("."):
            if handle_command(line.strip(), interpreter):
                return 0
            continue
        buffer.append(line)
        balance += line.count("{") + line.count("(") + line.count("[")
        balance -= line.count("}") + line.count(")") + line.count("]")
        if balance > 0:
            continue
        source = "\n".join(buffer)
        buffer.clear()
        balance = 0
        try:
            previous = interpreter.last_value
            _execute_source(interpreter, source)
            if interpreter.last_value is not None and interpreter.last_value is not previous:
                if not source.lstrip().startswith(("let ", "print(", "function ", "class ", "import ")):
                    print(format_value(interpreter.last_value))
        except SovaError as error:
            print(error.pretty())


def handle_command(command: str, interpreter: Interpreter) -> bool:
    name, _, argument = command.partition(" ")
    if name == ".exit":
        return True
    if name == ".help":
        print(HELP)
    elif name == ".clear":
        print("\033[2J\033[H", end="")
    elif name == ".env":
        hidden = {"Sova", "print", "input", "len", "type", "Error", "SyntaxError", "TypeError", "ValueError"}
        values = {key: format_value(value) for key, value in interpreter.globals.values.items() if key not in hidden}
        print(json.dumps(values, indent=2))
    elif name == ".load":
        path = Path(argument).expanduser().resolve()
        _execute_source(interpreter, path.read_text(encoding="utf-8"), str(path))
    elif name == ".tokens":
        source = argument or input("code> ")
        print(json.dumps([token.to_dict() for token in tokenize(source, "<shell>")], indent=2))
    elif name == ".ast":
        source = argument or input("code> ")
        print(json.dumps(node_to_data(Parser(source, "<shell>").parse()), indent=2))
    else:
        print("Unknown shell command. Type .help.")
    return False
