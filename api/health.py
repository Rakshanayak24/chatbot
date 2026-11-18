import json
import os
from http.server import BaseHTTPRequestHandler
from app import DATA

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        raw = json.dumps({
            "ok": True,
            "ai_configured": bool(os.getenv("OPENROUTER_API_KEY")),
            "snapshot_date": DATA["snapshot_date"]
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
