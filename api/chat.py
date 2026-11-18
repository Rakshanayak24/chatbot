import json
from http.server import BaseHTTPRequestHandler
from app import ask_openrouter, retrieve

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            question = str(body.get("message", "")).strip()[:2000]
        except (ValueError, TypeError):
            question = ""
        if not question:
            self._json({"error": "Please enter a question."}, 400)
            return
        records = retrieve(question)
        answer, ai = ask_openrouter(question, records)
        self._json({"answer": answer, "ai": ai, "sources": [
            {"source": r["source"], "title": r["title"], "url": r["url"]} for r in records
        ]})

    def _json(self, payload, status=200):
        raw = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)
