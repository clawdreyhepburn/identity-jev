#!/usr/bin/env python3
"""
Inference server for the FINE-TUNED Identity-Jev Laya checkpoint.

Loads the fine-tuned model from training/laya-identity-ft/final and scores a
query against every card with the noul primitive (one batched forward pass over
all 85 cards). Serves the demo:

  GET  /health           -> {status, cards, tuned}
  GET  /catalog          -> cards for the UI
  POST /filter {query}   -> {via, ms, results:[{key,p}]}

Run:
  cd projects/identity-jev && source .venv/bin/activate
  USE_TF=0 python server/laya_ft_server.py     # http://127.0.0.1:8799

Falls back to the stock checkpoint if the fine-tune isn't present yet.
"""
import os
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import json
import time
import threading
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import torch
from transformers import AutoTokenizer
from huggingface_hub import snapshot_download
from safetensors.torch import load_file

from laya.agent import _fix_tokenizer_config
from laya.common import build_model, build_sequence, render_options, QTYPES

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
FT_DIR = ROOT / "training" / "laya-identity-ft" / "final"
PORT = int(os.environ.get("PORT", "8799"))
NOUL = QTYPES["noul"]

catalog = json.loads((ROOT / "data" / "catalog.json").read_text())
CARDS = catalog["cards"]

_model = None
_tok = None
_cfg = None
_device = None
_temp = 1.0
_tuned = False
_lock = threading.Lock()


def pick_device():
    return torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")


def load_model():
    global _model, _tok, _cfg, _device, _temp, _tuned
    if _model is not None:
        return
    with _lock:
        if _model is not None:
            return
        _device = pick_device()
        if FT_DIR.exists() and (FT_DIR / "model.safetensors").exists():
            src = str(FT_DIR)
            _tuned = True
        else:
            src = snapshot_download("convaiinnovations/laya")
            _tuned = False
        _fix_tokenizer_config(src)
        _tok = AutoTokenizer.from_pretrained(os.path.join(src, "tokenizer"))
        with open(os.path.join(src, "rl_agent_config.json")) as f:
            _cfg = json.load(f)
        _cfg.setdefault("max_len", 512)
        _cfg.setdefault("head_max_len", 192)
        enc = os.path.join(src, "encoder")
        m = build_model(_cfg, encoder_dir=enc)
        m.load_state_dict(load_file(os.path.join(src, "model.safetensors")), strict=True)
        m.to(_device)
        m.eval()
        _model = m
        ft = _cfg.get("_identity_ft") or {}
        _temp = float(ft.get("noul_temperature", 1.0))
        print(f"[serve] device={_device} tuned={_tuned} temp={_temp:.3f} cards={len(CARDS)}", flush=True)


def noul_instruction(card, query):
    return (f'Query: "{query}". Is the standard "{card["label"]}" '
            f'\u2014 {card["criteria"]} \u2014 a strong, direct match for this query?')


def collate(items, pad_id):
    n = len(items)
    L = max(len(it["ids"]) for it in items)
    kmax = max(len(it["markers"]) for it in items)
    ids = torch.full((n, L), pad_id, dtype=torch.long)
    att = torch.zeros((n, L), dtype=torch.long)
    mpos = torch.zeros((n, kmax), dtype=torch.long)
    mmask = torch.zeros((n, kmax), dtype=torch.bool)
    for i, it in enumerate(items):
        ids[i, : len(it["ids"])] = torch.tensor(it["ids"])
        att[i, : len(it["ids"])] = 1
        k = len(it["markers"])
        mpos[i, :k] = torch.tensor(it["markers"])
        mmask[i, :k] = True
    return ids, att, mpos, mmask


@torch.no_grad()
def score_query(query, batch=8, on_progress=None):
    load_model()
    items = []
    for c in CARDS:
        seq, markers = build_sequence(
            _tok, {"query": query},
            {"t": "noul", "ins": noul_instruction(c, query), "crit": {}},
            _cfg["max_len"], _cfg["head_max_len"],
        )
        if len(markers) != len(render_options({"t": "noul", "crit": {}})):
            continue
        items.append({"ids": seq, "markers": markers, "key": c["key"]})

    results = {}
    total = len(items)
    done = 0
    if on_progress:
        on_progress(0, total)
    t0 = time.time()
    with _lock:
        for i in range(0, total, batch):
            chunk = items[i:i + batch]
            ids, att, mpos, mmask = collate(chunk, _tok.pad_token_id)
            logits, _ = _model(ids.to(_device), att.to(_device),
                               mpos.to(_device), mmask.to(_device),
                               torch.tensor([NOUL] * len(chunk)).to(_device))
            logits = logits.float() / _temp
            mask = mmask.to(_device)
            probs = torch.softmax(logits.masked_fill(~mask, -1e4), -1)
            ptrue = probs[:, 1].cpu().tolist()
            for j, it in enumerate(chunk):
                results[it["key"]] = float(ptrue[j])
            done += len(chunk)
            if on_progress:
                on_progress(done, total)
    dt = round((time.time() - t0) * 1000)
    out = [{"key": c["key"], "p": results.get(c["key"], 0.0)} for c in CARDS]
    return {"via": "laya-ft" if _tuned else "laya-base", "ms": dt, "tuned": _tuned, "results": out}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("access-control-allow-origin", "*")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-headers", "content-type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, json.dumps({"status": "ok", "cards": len(CARDS),
                                               "tuned": _tuned, "loaded": _model is not None}))
        if self.path == "/catalog":
            return self._send(200, json.dumps({"cards": [
                {k: c.get(k) for k in ("key", "label", "org", "criteria", "tags", "href")}
                for c in CARDS]}))
        return self._serve_static(self.path)

    def _serve_static(self, path):
        rel = path.split("?", 1)[0].lstrip("/") or "index.html"
        target = (PUBLIC / rel).resolve()
        try:
            target.relative_to(PUBLIC.resolve())
        except ValueError:
            return self._send(403, json.dumps({"error": "forbidden"}))
        if not target.is_file():
            return self._send(404, json.dumps({"error": "not found"}))
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("content-type", ctype)
        self.send_header("access-control-allow-origin", "*")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _stream(self, obj):
        self.wfile.write((json.dumps(obj) + "\n").encode())
        self.wfile.flush()

    def do_POST(self):
        if self.path != "/filter":
            return self._send(404, json.dumps({"error": "not found"}))
        n = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(n) if n else b"{}"
        try:
            query = (json.loads(raw or b"{}").get("query") or "").strip()
        except Exception:
            return self._send(400, json.dumps({"error": "bad json"}))
        self.send_response(200)
        self.send_header("content-type", "application/x-ndjson")
        self.send_header("cache-control", "no-cache")
        self.send_header("access-control-allow-origin", "*")
        self.send_header("connection", "close")
        self.end_headers()
        if not query:
            return self._stream({"type": "done", "via": "laya", "results": []})
        try:
            payload = score_query(query, on_progress=lambda done, total: self._stream(
                {"type": "progress", "done": done, "total": total}
            ))
            payload["type"] = "done"
            self._stream(payload)
        except Exception as e:
            self._stream({"type": "error", "error": str(e)})

    def log_message(self, *a):
        pass


def main():
    print("[serve] loading model…", flush=True)
    load_model()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[serve] http://127.0.0.1:{PORT}  tuned={_tuned}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
