import json
from http.server import BaseHTTPRequestHandler

from ._common import ROOT, handle_options, send_json


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        manifest = ROOT / "website" / "public" / "releases" / "latest.json"
        payload = (
            json.loads(manifest.read_text(encoding="utf-8"))
            if manifest.exists()
            else {"version": "0.1.0", "status": "manifest-unavailable"}
        )
        send_json(self, {"success": True, "release": payload})
