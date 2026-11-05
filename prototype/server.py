"""Demo server (Python standard library only).

Serves a single-page UI in a Next.js-style layout (question input, generated
query panel, checked result panel, cited sources panel) backed by the agent.
HONEST: this is NOT a Next.js app — it is stdlib http.server serving HTML,
so the demo runs with zero dependencies. A real Next.js frontend calling the
same agent API is a documented next step, not a claim.

Run: python3 prototype/server.py  ->  http://127.0.0.1:8000
Endpoints: GET /  (UI), GET /api/ask?q=...&variant=improved|base  (JSON)
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(__file__))
from agent import run_agent  # noqa: E402
from db import open_db  # noqa: E402

CONN = open_db()

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>DataAgent — Lexsi Track 3 No. 6 demo</title>
<style>body{font-family:system-ui,sans-serif;max-width:800px;margin:2em auto;padding:0 1em}
pre{background:#f4f4f4;padding:1em;overflow:auto}label{font-weight:bold}</style></head>
<body><h1>DataAgent — business questions over a sample database</h1>
<p>Lexsi Track 3 No. 6 prototype. Sample data only — no real business data.</p>
<label>Question</label><br>
<input id="q" size="80" value="Who is the top customer by delivered spend?">
<select id="v"><option value="improved">improved</option><option value="base">base</option></select>
<button onclick="ask()">Ask</button>
<h2>Answer</h2><p id="ans"></p>
<h2>Generated query</h2><pre id="sql"></pre>
<h2>Checked result (cited source)</h2><pre id="rows"></pre>
<h2>Checks</h2><pre id="checks"></pre>
<script>async function ask(){
 const q=document.getElementById('q').value, v=document.getElementById('v').value;
 const r=await fetch('/api/ask?q='+encodeURIComponent(q)+'&variant='+v).then(r=>r.json());
 document.getElementById('ans').textContent=r.answer;
 document.getElementById('sql').textContent=r.sql;
 document.getElementById('rows').textContent=JSON.stringify(r.rows,null,2);
 document.getElementById('checks').textContent=JSON.stringify(r.checks,null,2);
}</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def _send(self, body, ctype="text/html"):
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            return self._send(HTML)
        if u.path == "/api/ask":
            qs = parse_qs(u.query)
            q = qs.get("q", [""])[0]
            variant = qs.get("variant", ["improved"])[0]
            try:
                r = run_agent(CONN, q, variant)
                return self._send(json.dumps({
                    "answer": r.answer, "sql": r.sql, "rows": r.rows,
                    "checks": r.checks,
                    "tool_calls": [t for t, _ in r.tool_calls]}), "application/json")
            except Exception as e:
                return self._send(json.dumps({"error": str(e)}), "application/json")
        if u.path == "/health":
            return self._send(json.dumps({"ok": True}), "application/json")
        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    print("Serving on http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), H).serve_forever()
