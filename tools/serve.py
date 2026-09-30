#!/usr/bin/env python3
"""Local preview server mimicking the production host: clean URLs → .html, real 404 page with HTTP 404."""
import http.server, os, sys, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0].split("#")[0]
        if path == "/home":
            self.send_response(301); self.send_header("Location", "/"); self.end_headers(); return
        fs = os.path.join(ROOT, path.lstrip("/"))
        if path != "/" and not os.path.isfile(fs) and os.path.isfile(fs + ".html"):
            self.path = path + ".html"
        elif path != "/" and not os.path.exists(fs):
            body = open(os.path.join(ROOT, "404.html"), "rb").read()
            self.send_response(404); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        return super().do_GET()
    def log_message(self, *a): pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=ROOT)).serve_forever()
