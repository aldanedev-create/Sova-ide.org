from http.server import BaseHTTPRequestHandler

from ._common import handle_options, send_json


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        send_json(self, {"success": True, "service": "sova-online", "version": "0.1.0", "pipeline": "single-ast"})
