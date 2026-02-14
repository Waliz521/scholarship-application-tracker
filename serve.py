"""Run the Scholarship Application Tracker locally. Open http://localhost:8000"""

import http.server
import os
import socketserver
import webbrowser

from web import build_html

PORT = int(os.environ.get("PORT", 8000))


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        html = build_html()
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    with socketserver.TCPServer((host, PORT), _Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Open in browser: {url}")
        if host == "127.0.0.1":
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
