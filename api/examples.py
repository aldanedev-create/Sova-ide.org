from http.server import BaseHTTPRequestHandler
from pathlib import Path

from ._common import ROOT, handle_options, send_json


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        examples = []
        for path in sorted((ROOT / "examples").glob("*.sova")):
            examples.append({"id": path.stem, "name": path.stem.replace("_", " ").title(), "source": path.read_text(encoding="utf-8")})
        send_json(self, {"success": True, "examples": examples})
