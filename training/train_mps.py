#!/usr/bin/env python3
"""
Fine-tune Laya on the Identity-Jev noul dataset — single-device (MPS or CPU).

Ported from Convai's Kaggle 2xT4 DDP notebook to run on a Mac (no CUDA/NCCL/DDP,
no fp16 GradScaler). Same RLCD idea:
  - sample G noisy logit distributions (zero-mean projected)
  - reward = strictly-proper scoring rule (proper_reward from laya)
  - GRPO-style group-mean-baseline advantage
  - policy-gradient loss + soft cross-entropy guidance toward the target dist
Then fit one calibration temperature for the noul question type.

Our data are noul rows (query, card) -> 0/1. Each row becomes a 2-way
distribution [P(false), P(true)] and is rendered with the model's own
build_sequence so marker positions line up with the decision head.

Run (overnight):
  cd projects/identity-jev && source .venv/bin/activate
  USE_TF=0 python training/train_mps.py \
      --epochs 6 --micro-batch 8 --grad-accum 4 \
      --out training/laya-identity-ft 2>&1 | tee training/train.log

Resume-safe: writes a rolling checkpoint after every epoch.
"""
import os
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# MPS: allow fallback for any op not implemented on Metal
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import sys, json, time, math, random, argparse
from pathlib import Path

import torch
from safetensors.torch import load_file, save_file
from transformers import AutoTokenizer
from huggingface_hub import snapshot_download

from laya.agent import _fix_tokenizer_config
from laya.common import build_model, build_sequence, render_options, proper_reward, QTYPES

ROOT = Path(__file__).resolve().parent.parent
MODEL_ID = "convaiinnovations/laya"
NOUL = QTYPES["noul"]


def pick_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_item(tok, cfg, row):
    """Render one (query, card, label) noul row into ids/markers/target."""
    q = row["question"]
    state = row["state"]
    target_true = float(row["target"])
    # noul target distribution: [false, true]
    target = [1.0 - target_true, target_true]
    crit = q.get("criteria", {})
    seq, markers = build_sequence(
        tok, state,
        {"t": "noul", "ins": q["instructions"], "crit": crit},
        cfg["max_len"], cfg["head_max_len"],
    )
    k = len(render_options({"t": "noul", "crit": crit}))
    if len(markers) != k:
        return None
    return {
        "ids": seq,
        "markers": markers,
        "qtype": NOUL,
        "target": target,
        "label": int(target_true >= 0.5),
    }


def collate(items, pad_id):
    n = len(items)
    L = max(len(it["ids"]) for it in items)
    kmax = max(len(it["markers"]) for it in items)
    ids = torch.full((n, L), pad_id, dtype=torch.long)
    att = torch.zeros((n, L), dtype=torch.long)
    mpos = torch.zeros((n, kmax), dtype=torch.long)
    mmask = torch.zeros((n, kmax), dtype=torch.bool)
    target = torch.zeros((n, kmax), dtype=torch.float32)
    for i, it in enumerate(items):
        ids[i, : len(it["ids"])] = torch.tensor(it["ids"])
        att[i, : len(it["ids"])] = 1
        k = len(it["markers"])
        mpos[i, :k] = torch.tensor(it["markers"])
        mmask[i, :k] = True
        target[i, : len(it["target"])] = torch.tensor(it["target"], dtype=torch.float32)
    return {
        "input_ids": ids, "attention_mask": att,
        "marker_pos": mpos, "marker_mask": mmask,
        "target": target,
        "qtype": torch.tensor([it["qtype"] for it in items]),
        "label": torch.tensor([it["label"] for it in items]),
    }


def fit_one_temp(sel):
    if len(sel) < 10:
        return 1.0
    kmax = max(len(z) for z, _ in sel)
    Z = torch.full((len(sel), kmax), -1e4)
    T = torch.zeros((len(sel), kmax))
    for i, (z, t) in enumerate(sel):
        Z[i, : len(z)] = torch.tensor(z)
        T[i, : len(t)] = torch.tensor(t, dtype=torch.float32)
    log_t = torch.zeros(1, requires_grad=True)
    opt = torch.optim.LBFGS([log_t], lr=0.1, max_iter=100)

    def closure():
        opt.zero_grad()
        loss = -(T * torch.log_softmax(Z / log_t.exp(), -1)).sum(-1).mean()
        loss.backward()
        return loss

    opt.step(closure)
    return float(torch.clamp(log_t.exp(), 0.1, 10.0).item())


@torch.no_grad()
def evaluate(model, device, items, pad_id, batch=16):
    model.eval()
    correct = 0
    total = 0
    for i in range(0, len(items), batch):
        chunk = items[i:i + batch]
        cb = collate(chunk, pad_id)
        logits, _ = model(
            cb["input_ids"].to(device), cb["attention_mask"].to(device),
            cb["marker_pos"].to(device), cb["marker_mask"].to(device),
            cb["qtype"].to(device),
        )
        logits = logits.float()
        mask = cb["marker_mask"].to(device)
        probs = torch.softmax(logits.masked_fill(~mask, -1e4), -1)
        pred = probs.argmax(-1).cpu()
        for r, it in enumerate(chunk):
            total += 1
            if int(pred[r]) == it["label"]:
                correct += 1
    model.train()
    return correct / max(1, total)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--group-size", type=int, default=4)
    ap.add_argument("--lr-encoder", type=float, default=2.5e-5)
    ap.add_argument("--lr-head", type=float, default=1.0e-4)
    ap.add_argument("--sigma-start", type=float, default=0.4)
    ap.add_argument("--sigma-end", type=float, default=0.1)
    ap.add_argument("--max-len", type=int, default=512)
    ap.add_argument("--head-max-len", type=int, default=192)
    ap.add_argument("--out", type=str, default=str(ROOT / "training" / "laya-identity-ft"))
    ap.add_argument("--device", type=str, default="")
    args = ap.parse_args()

    device = torch.device(args.device) if args.device else pick_device()
    print(f"[ft] device={device} torch={torch.__version__}", flush=True)

    model_dir = snapshot_download(MODEL_ID)
    _fix_tokenizer_config(model_dir)
    tok = AutoTokenizer.from_pretrained(os.path.join(model_dir, "tokenizer"))
    with open(os.path.join(model_dir, "rl_agent_config.json")) as f:
        cfg = json.load(f)
    cfg["max_len"] = args.max_len
    cfg["head_max_len"] = args.head_max_len

    print("[ft] building model + loading weights…", flush=True)
    model = build_model(cfg, encoder_dir=os.path.join(model_dir, "encoder"))
    weights = load_file(os.path.join(model_dir, "model.safetensors"))
    model.load_state_dict(weights, strict=True)
    model.to(device)
    model.train()

    # Data
    train_rows = load_rows(ROOT / "training" / "dataset.jsonl")
    eval_rows = load_rows(ROOT / "training" / "eval.jsonl")
    items, skipped = [], 0
    for r in train_rows:
        it = build_item(tok, cfg, r)
        (items.append(it) if it else None)
        if it is None:
            skipped += 1
    eval_items = [build_item(tok, cfg, r) for r in eval_rows]
    eval_items = [x for x in eval_items if x]
    print(f"[ft] train items={len(items)} (skipped {skipped}) eval={len(eval_items)}", flush=True)

    enc_params = [p for n, p in model.named_parameters() if "encoder." in n]
    head_params = [p for n, p in model.named_parameters() if "encoder." not in n]
    optimizer = torch.optim.AdamW(
        [{"params": enc_params, "lr": args.lr_encoder},
         {"params": head_params, "lr": args.lr_head}],
        weight_decay=0.01,
    )
    micro, accum, G = args.micro_batch, args.grad_accum, args.group_size
    total_updates = max(1, (len(items) // (micro * accum)) * args.epochs)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=total_updates, eta_min=1e-6)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base_acc = evaluate(model, device, eval_items, tok.pad_token_id)
    print(f"[ft] zero-shot eval acc = {base_acc:.3f}", flush=True)

    t0 = time.time()
    for epoch in range(args.epochs):
        random.seed(42 + epoch)
        random.shuffle(items)
        progress = epoch / max(1, args.epochs - 1)
        sigma = args.sigma_start + (args.sigma_end - args.sigma_start) * progress
        optimizer.zero_grad(set_to_none=True)
        epoch_loss, n_batches, accum_step = 0.0, 0, 0

        for b_idx in range(0, len(items), micro):
            chunk = items[b_idx:b_idx + micro]
            if not chunk:
                continue
            batch = collate(chunk, tok.pad_token_id)
            logits, act = model(
                batch["input_ids"].to(device), batch["attention_mask"].to(device),
                batch["marker_pos"].to(device), batch["marker_mask"].to(device),
                batch["qtype"].to(device),
            )
            logits = logits.float()
            mask = batch["marker_mask"].to(device)
            k = mask.sum(-1, keepdim=True).float()
            target = batch["target"].to(device)

            eps = torch.randn((G,) + logits.shape, device=device) * sigma * mask
            eps = (eps - eps.sum(-1, keepdim=True) / k) * mask
            z = logits.detach().unsqueeze(0) + eps
            q = torch.softmax(z.masked_fill(~mask, -1e4), -1)

            with torch.no_grad():
                r = proper_reward(q, target.unsqueeze(0), batch["qtype"].to(device),
                                  mask, w_sph=0.75, w_rps=1.0)
                adv = r - r.mean(0, keepdim=True)
                adv = adv / (adv.std() + 1e-6)

            logp = -(((z - logits.unsqueeze(0)) ** 2) * mask).sum(-1) / (2 * sigma ** 2)
            loss_rl = -(adv * logp).mean()
            loss_ce = -(target * torch.log_softmax(logits.masked_fill(~mask, -1e4), -1)).sum(-1).mean()
            loss = (loss_rl + 1.0 * loss_ce) / accum + 0.0 * act.sum()

            loss.backward()
            accum_step += 1
            if accum_step % accum == 0 or (b_idx + micro) >= len(items):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)

            epoch_loss += loss.item() * accum
            n_batches += 1
            if n_batches % 25 == 0:
                print(f"  ep{epoch+1}/{args.epochs} step{n_batches} "
                      f"loss={loss.item()*accum:.4f} reward={r.mean().item():.3f} "
                      f"lr={scheduler.get_last_lr()[0]:.2e} "
                      f"elapsed={time.time()-t0:.0f}s", flush=True)

        acc = evaluate(model, device, eval_items, tok.pad_token_id)
        print(f"=== epoch {epoch+1}/{args.epochs} done "
              f"avg_loss={epoch_loss/max(1,n_batches):.4f} eval_acc={acc:.3f} "
              f"({time.time()-t0:.0f}s) ===", flush=True)

        # rolling checkpoint
        ckpt = out / "checkpoint_latest"
        ckpt.mkdir(parents=True, exist_ok=True)
        sd = {k2: v.half().contiguous().cpu() for k2, v in model.state_dict().items()}
        save_file(sd, os.path.join(ckpt, "model.safetensors"))
        model.encoder.config.save_pretrained(os.path.join(ckpt, "encoder"))
        tok.save_pretrained(os.path.join(ckpt, "tokenizer"))
        json.dump({"epoch": epoch + 1, "total_epochs": args.epochs,
                   "avg_loss": epoch_loss / max(1, n_batches), "eval_acc": acc},
                  open(os.path.join(ckpt, "checkpoint_meta.json"), "w"), indent=2)
        print(f"  saved checkpoint epoch {epoch+1}", flush=True)

    # temperature calibration on noul
    print("[ft] fitting noul calibration temperature…", flush=True)
    model.eval()
    calib = items[::5][:400]
    preds = []
    with torch.no_grad():
        for i in range(0, len(calib), 16):
            cb = collate(calib[i:i + 16], tok.pad_token_id)
            l, _ = model(
                cb["input_ids"].to(device), cb["attention_mask"].to(device),
                cb["marker_pos"].to(device), cb["marker_mask"].to(device),
                cb["qtype"].to(device),
            )
            l = l.float().cpu().numpy()
            for r2, it in enumerate(calib[i:i + 16]):
                kk = len(it["markers"])
                preds.append((l[r2, :kk], it["target"]))
    temp = fit_one_temp(preds)
    print(f"[ft] noul temperature = {temp:.3f}", flush=True)

    # final export
    final = out / "final"
    final.mkdir(parents=True, exist_ok=True)
    sd = {k2: v.half().contiguous().cpu() for k2, v in model.state_dict().items()}
    save_file(sd, os.path.join(final, "model.safetensors"))
    model.encoder.config.save_pretrained(os.path.join(final, "encoder"))
    tok.save_pretrained(os.path.join(final, "tokenizer"))
    # copy config, set fitted temperature for noul (index 2)
    tbo = cfg.get("temperature_by_options") or {}
    cfg["_identity_ft"] = {"noul_temperature": temp}
    cfg["temperature"] = cfg.get("temperature", [1.2, 1.2, 1.2])
    json.dump(cfg, open(os.path.join(final, "rl_agent_config.json"), "w"), indent=2)
    final_acc = evaluate(model, device, eval_items, tok.pad_token_id)
    print(f"[ft] DONE. final eval acc={final_acc:.3f} (zero-shot was {base_acc:.3f})", flush=True)
    print(f"[ft] model at {final}", flush=True)


if __name__ == "__main__":
    main()
