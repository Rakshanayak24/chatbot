import json
from http.server import BaseHTTPRequestHandler
from app import DATA

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        raw = json.dumps({
            "snapshot_date": DATA["snapshot_date"],
            "sources": [{"source": r["source"], "title": r["title"], "url": r["url"]} for r in DATA["records"]]
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
