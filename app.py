import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))

def retrieve(question, limit=5):
    terms = set(re.findall(r"[a-z0-9]+", question.lower()))
    ranked = []
    for item in DATA["records"]:
        words = set(re.findall(r"[a-z0-9]+", (item["title"] + " " + item["text"] + " " + item["source"]).lower()))
        score = len(terms & words)
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in ranked[:limit]]

def ask_openrouter(question, records):
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key:
        return "The AI assistant is not configured yet. Set OPENROUTER_API_KEY on the server to enable AI answers. You can still browse the public source links below.", False
    model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    context = "\n\n".join(f"[{r['source']} — {r['title']}]({r['url']})\n{r['text']}" for r in records)
    payload = {"model": model, "temperature": 0.2, "messages": [
        {"role":"system","content":"You are Estate Scout, a helpful property research assistant. Answer only from the supplied source notes. Treat listing prices and counts as a dated snapshot; clearly say they may have changed. If data is missing, say so instead of guessing. Use SAR for Saudi listing prices. Mention which source supports your answer and keep source URLs in markdown links. You do not provide investment, legal, or financial advice."},
        {"role":"user","content":f"Question: {question}\n\nPublic source notes (snapshot {DATA['snapshot_date']}):\n{context}"}
    ]}
    request = Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization":f"Bearer {key}","Content-Type":"application/json","HTTP-Referer":os.getenv("APP_URL","http://localhost:8080"),"X-Title":"Estate Scout"}, method="POST")
    try:
        with urlopen(request, timeout=50) as response:
            result = json.loads(response.read())
        return result["choices"][0]["message"]["content"], True
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError) as exc:
        detail = "OpenRouter is temporarily unavailable. Please try again shortly."
        if isinstance(exc, HTTPError):
            detail = "OpenRouter could not complete the request. Check the API key, model availability, or free-tier rate limit."
        return detail, False

class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        raw = json.dumps(payload).encode()
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path == "/api/health":
            self.send_json({"ok":True,"ai_configured":bool(os.getenv("OPENROUTER_API_KEY")),"snapshot_date":DATA["snapshot_date"]}); return
        if self.path == "/api/sources":
            self.send_json({"snapshot_date":DATA["snapshot_date"],"sources":[{"source":r["source"],"title":r["title"],"url":r["url"]} for r in DATA["records"]]}); return
        if self.path not in ("/", "/index.html"):
            self.send_error(404); return
        body=(ROOT/"index.html").read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        if self.path != "/api/chat": self.send_error(404); return
        try:
            body=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
            question=str(body.get("message", "")).strip()[:2000]
        except (ValueError, TypeError): question=""
        if not question: self.send_json({"error":"Please enter a question."},400); return
        records=retrieve(question)
        answer, ai=ask_openrouter(question, records)
        self.send_json({"answer":answer,"ai":ai,"sources":[{"source":r["source"],"title":r["title"],"url":r["url"]} for r in records]})
    def log_message(self, fmt, *args): print("%s - %s"%(self.address_string(),fmt%args))

if __name__ == "__main__":
    port=int(os.getenv("PORT","8080")); print(f"Estate Scout listening on :{port}"); ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()
