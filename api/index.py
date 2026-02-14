"""Vercel serverless handler for Scholarship Application Tracker."""

import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from sheet_loader import load_scholarships
from web import build_html


FAVICON_FILE = "favicon.png"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/favicon.png", "/favicon.ico"):
            favicon = _root / FAVICON_FILE
            if favicon.exists():
                body = favicon.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        scholarships = load_scholarships(use_local_fallback=False)
        html = build_html(scholarships=scholarships)
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
