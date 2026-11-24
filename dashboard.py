"""Local browser UI: python dashboard.py --port 8765 (no client API keys)."""
from __future__ import annotations
import argparse
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit
from core import SERVICES, run

HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MUHRIS AI LAB · Source-grounded agent workstation</title>
<style>
:root{color-scheme:dark;font-family:Inter,system-ui,Arial,sans-serif}
*{box-sizing:border-box}body{margin:0;min-height:100vh;color:#f1eafa;background:#0a0915}
body:before{content:"";position:fixed;inset:0;z-index:-1;background:radial-gradient(ellipse at 85% 12%,#9c37a844,transparent 40%),radial-gradient(ellipse at 15% 100%,#225b9b55,transparent 42%)}
main{max-width:1050px;margin:auto;padding:66px 22px}
.eyebrow{font-size:11px;color:#ffa9d7;font-weight:800;letter-spacing:.2em}h1{font-size:clamp(40px,7vw,82px);letter-spacing:-.055em;line-height:1.03;margin:18px 0}h1 em{font-style:normal;color:#fb9bcb}
.lead{color:#b9afc4;line-height:1.7;max-width:730px}
.panel{margin-top:34px;padding:25px;border:1px solid #ffffff28;border-radius:21px;background:#ffffff0b;backdrop-filter:blur(18px)}
form{display:flex;flex-wrap:wrap;gap:10px}
input,select,button{font:inherit;border-radius:10px;padding:13px 16px}
input,select{background:#17162a;color:#f3eefa;border:1px solid #ffffff35}
input{min-width:220px;flex:1}button{color:#161321;background:linear-gradient(110deg,#ffd1b4,#ee98d8);border:0;font-weight:800;cursor:pointer}button:disabled{opacity:.6;cursor:wait}
#status{margin:22px 0;color:#eac0db;font-size:13px}pre{overflow-x:auto;white-space:pre-wrap;overflow-wrap:anywhere;background:#0b0c1a;border:1px solid #ffffff22;border-radius:14px;padding:22px;line-height:1.7;color:#c8d4f6;font-size:12px}small{color:#b9aec6}
a{color:#f7b6db}
</style></head><body><main><div class="eyebrow">MUHRIS AI LAB / REAL DATA · EVIDENCE · HUMAN REVIEW</div>
<h1>Evidence-first <em>agent workflows.</em></h1>
<p class="lead">This local demo runs specialist, rule-based agents: discover public records, check their provenance, analyse relevance, and prepare a structured report. No paid LLM or secret key is required for the default workflows.</p>
<div class="panel"><form id="form"><select id="service" aria-label="Select project"></select>
<input id="query" maxlength="120" aria-label="Search query" placeholder="Enter topic, location, product or market" required>
<button id="go" type="submit">RUN WORKFLOW ↗</button></form>
<p id="status" role="status">Choose a project and enter a search.</p>
<pre id="result" aria-label="JSON source report">Results will appear here.</pre>
<small>Source APIs may be unavailable or rate-limited. Outcomes are informational and require human verification. No background monitoring or autonomous decisions.</small></div></main>
<script>
const services=__SERVICES__, selector=document.getElementById('service');
services.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;selector.append(o)});
const form=document.getElementById('form'),go=document.getElementById('go'),status=document.getElementById('status'),view=document.getElementById('result');
form.addEventListener('submit',async ev=>{ev.preventDefault();go.disabled=true;status.textContent='Retrieving public source data and preparing report…';view.textContent='';
try{const params=new URLSearchParams({service:selector.value,query:document.getElementById('query').value});const response=await fetch('/api?'+params);const data=await response.json();view.textContent=JSON.stringify(data,null,2);status.textContent=response.ok?'Report ready · inspect original sources':'Source error · check API availability';}
catch(e){status.textContent='Network error';view.textContent=String(e)}finally{go.disabled=false}});
</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path)
        if route.path == "/":
            raw = HTML.replace("__SERVICES__", json.dumps(SERVICES)).encode("utf-8")
            kind, code = "text/html; charset=utf-8", 200
        elif route.path == "/api":
            args = parse_qs(route.query)
            query = args.get("query", [""])[0]
            service = args.get("service", [SERVICES[0]])[0]
            try:
                if len(query) > 120 or len(query.strip()) < 2:
                    raise ValueError("Query length must be 2–120 characters.")
                if service not in SERVICES:
                    raise ValueError("Unknown project.")
                result = run(query, service)
                code = 200
            except ValueError as exc:
                result, code = {"error": str(exc)}, 400
            except Exception as exc:
                result, code = {"error": str(exc), "source_status": "unavailable"}, 502
            raw = json.dumps(result, ensure_ascii=False, default=str).encode("utf-8")
            kind = "application/json; charset=utf-8"
        else:
            raw, kind, code = b"Not found", "text/plain", 404
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(raw)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print("Open http://localhost:%d" % args.port)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
