from __future__ import annotations

"""Conservative Sova source formatter for indentation and trailing whitespace."""


def format_source(source: str, indent: int = 4) -> str:
    depth = 0
    result: list[str] = []
    for raw in source.splitlines():
        text = raw.strip()
        if not text:
            if result and result[-1] != "":
                result.append("")
            continue
        if text.startswith("}"):
            depth = max(0, depth - 1)
        result.append(" " * (depth * indent) + text)
        opens = text.count("{")
        closes = text.count("}")
        depth = max(0, depth + opens - closes - (1 if text.startswith("}") else 0))
    return "\n".join(result).rstrip() + "\n"
