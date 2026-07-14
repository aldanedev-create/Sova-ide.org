from http.server import BaseHTTPRequestHandler

from ._common import handle_options, handle_post, run_project


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_POST(self):
        handle_post(self, run_project)
