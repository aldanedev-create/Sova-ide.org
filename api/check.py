from http.server import BaseHTTPRequestHandler

from ._common import check_project, handle_options, handle_post


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_POST(self):
        handle_post(self, check_project)
