#!/usr/bin/env python3
"""
Local Laya decision server for the Identity-Jev demo.

Loads the Laya model once (preloaded in memory) and exposes:
  GET  /health            -> {status, model, cards}
  GET  /catalog           -> the card catalog (labels/criteria/href for the UI)
  POST /filter  {query}   -> [{key, p}] scored by Laya over all cards

Scoring shape: ONE Choice question over all cards (each card = one option).
Choice returns a probability distribution across every option in a single
forward pass, which is exactly what the pile animation wants.

Run:
  cd projects/identity-jev
  source .venv/bin/activate
  USE_TF=0 python server/laya_server.py           # http://127.0.0.1:8799

Env:
  LAYA_MODEL   default convaiinnovations/laya
  PORT         default 8799
  HEAD_MAX_LEN default 512   (raise so 50+ options stay distinct)
  MAX_LEN      default 1024
"""

import os
os.environ.setdefault("USE_TF", "0")

import json
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data" / "catalog.json"
PORT = int(os.environ.get("PORT", "8799"))
MODEL_ID = os.environ.get("LAYA_MODEL", "convaiinnovations/laya")
HEAD_MAX_LEN = int(os.environ.get("HEAD_MAX_LEN", "512"))
MAX_LEN = int(os.environ.get("MAX_LEN", "1024"))

catalog = json.loads(CATALOG_PATH.read_text())
CARDS = catalog["cards"]
BY_KEY = {c["key"]: c for c in CARDS}

_agent = None
_lock = threading.Lock()


def load_agent():
    global _agent
    if _agent is not None:
        return _agent
    with _lock:
        if _agent is not None:
            return _agent
        import laya  # noqa
        t0 = time.time()
        agent = laya.load(MODEL_ID)
        # Give options room so 50+ cards stay distinguishable.
        try:
            agent.cfg["head_max_len"] = HEAD_MAX_LEN
            agent.cfg["max_len"] = MAX_LEN
        except Exception:
            pass
        print(f"[laya] loaded {MODEL_ID} in {time.time()-t0:.1f}s "
              f"(head_max_len={HEAD_MAX_LEN}, max_len={MAX_LEN})", flush=True)
        _agent = agent
        return _agent


def build_choice(query):
    """One Choice question; each card is an option keyed by card.key."""
    criteria = {}
    for c in CARDS:
        # Keep option text tight so the shared option budget isn't blown.
        criteria[c["key"]] = f"{c['label']}: {c['criteria']}"
    return {
        "match": {
            "type": "choice",
            "instructions": (
                f"A person is searching a catalog of identity, authentication, "
                f"and authorization standards. Their query is: \"{query}\". "
                f"Which standard best matches what they are looking for?"
            ),
            "criteria": criteria,
        }
    }


def score_query(query):
    agent = load_agent()
    state = {
        "query": query,
        "context": (
            "Searching identity/authentication/authorization standards, specs, "
            "IETF drafts, and protocols by claim, mechanism, or concept."
        ),
    }
    questions = build_choice(query)
    t0 = time.time()
    with _lock:  # single model instance; serialize forward passes
        res = agent.predict(state, questions)
    dt = round((time.time() - t0) * 1000)
    ans = res.get("answers", {}).get("match", {})
    probs = ans.get("probabilities") or {}
    results = [{"key": c["key"], "p": float(probs.get(c["key"], 0.0))} for c in CARDS]
    return {"via": "laya", "model": res.get("model", MODEL_ID), "ms": dt, "results": results}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("access-control-allow-origin", "*")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-headers", "content-type")
        self.send_header("access-control-allow-methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, json.dumps({
                "status": "ok",
                "model": MODEL_ID,
                "loaded": _agent is not None,
                "cards": len(CARDS),
            }))
        if self.path == "/catalog":
            return self._send(200, json.dumps({
                "cards": [
                    {k: c.get(k) for k in ("key", "label", "org", "criteria", "tags", "href")}
                    for c in CARDS
                ]
            }))
        return self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path != "/filter":
            return self._send(404, json.dumps({"error": "not found"}))
        n = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(n) if n else b"{}"
        try:
            query = (json.loads(raw or b"{}").get("query") or "").strip()
        except Exception:
            return self._send(400, json.dumps({"error": "bad json"}))
        if not query:
            return self._send(200, json.dumps({"via": "laya", "results": []}))
        try:
            return self._send(200, json.dumps(score_query(query)))
        except Exception as e:
            return self._send(500, json.dumps({"error": str(e)}))

    def log_message(self, *a):
        pass


def main():
    print(f"[laya] preloading model… (first run downloads weights)", flush=True)
    load_agent()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[laya] serving http://127.0.0.1:{PORT}  cards={len(CARDS)}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
