# Identity Jev

**Type a claim or concept in plain language. A fine-tuned [Laya](https://huggingface.co/convaiinnovations/laya) decision model pulls the matching identity standards out of a messy pile and lines them up — ranked by real probability, not string matching.**

Inspired by the emoji-classifier demos built on typed decision models: a pile of items at the bottom of the screen, you type an intent ("things you can wear"), and the matches jump up. Here the items are **85 identity, authentication, and authorization standards** — and the query understands what you *mean*, so "kill access the moment someone is fired" surfaces **Global Token Revocation** and **Zero Standing Privilege**, not whatever happens to contain the word "access."

![status: fine-tuned locally, 87% eval accuracy](https://img.shields.io/badge/eval%20accuracy-87%25-brightgreen) ![zero-shot 40%](https://img.shields.io/badge/zero--shot-40%25-lightgrey)

---

## Why this exists

String search fails on identity questions because the vocabulary is a minefield of overloaded jargon. You don't always know the name of the thing you need — you know the *problem*:

| You type (plain language) | It surfaces |
|---|---|
| `let an AI agent act on my behalf` | AI Agent Auth, MCP Authorization, Token Exchange |
| `kill access the moment someone is fired` | Global Token Revocation, Zero Standing Privilege, CAEP |
| `externalize authorization decisions` | AuthZEN |
| `who owns this api key` | Non-Human Identity Governance |
| `decide access from the tokens the caller already carries` | Token-Based Access Control (TBAC) |
| `prove a claim without revealing my whole identity` | mDL (ISO 18013-5), SD-JWT, OpenID4VP |
| `one workload calling another safely` | SPIFFE, WIMSE |
| `fine grained permissions beyond scopes` | Rich Authorization Requests (RAR) |

A keyword index cannot do any of these. A **decision model** can — once it's been taught this specific landscape.

## The result

Laya is an open-weight ([Apache-2.0](https://huggingface.co/convaiinnovations/laya)) "System 1" decision model from Convai Innovations: you give it state + typed questions, it returns calibrated probabilities. Out of the box it is near-chance on a niche taxonomy like this.

We fine-tuned it on a hand-built dataset of natural-language identity queries:

- **Zero-shot: 40.4% eval accuracy**
- **Fine-tuned: 87% eval accuracy**
- **~25 minutes** of training on a **Mac mini (M4 Pro, MPS)** — no CUDA, no cloud GPU, no API key
- ~2 s to score all 85 cards per query on the mini; sub-200 ms on any real GPU

The fine-tune sharpens calibration too: the right card lands at ~0.97 and everything else drops near zero, instead of the zero-shot mush where every card scored ~0.9.

## The card catalog

85 standards, grounded in what the identity community is actually discussing in 2026 (sourced from *Identity at the Center* and *Identerati Office Hours* — see [`research/podcast-trends.md`](research/podcast-trends.md)). It spans:

- **Token & crypto core** — JWT, JWS/JWE/JWK/JWA, COSE, CWT, HPKE
- **OAuth / OIDC** — OAuth 2.0/2.1, PKCE, PAR, JAR, token exchange, introspection, RAR, DPoP, mTLS, FAPI 2.0, discovery, UserInfo
- **Continuous & lifecycle** — Shared Signals (SSF), CAEP, RISC, Global Token Revocation, Status List, OpenID Provider Commands, SCIM, IPSIE
- **Authorization models** — AuthZEN, TBAC, Cedar, RAR-Cedar, Zero Standing Privilege, Intent-Based Access, PAM
- **Workload & agent identity** — SPIFFE/SPIRE, WIMSE (S2S / AI-agent / ECT), MCP authorization, agentic AI identity, AI Identity Control Plane, NHI governance, OVID, FT-JWT, Waffles, Transaction Tokens, ID-JAG, actor profile
- **Credentials & wallets** — Verifiable Credentials, DIDs, SD-JWT (+VC), OpenID4VCI/VP, mDL, EUDIW, OpenID Federation
- **Threat & provenance** — ITDR, RISC, prompt injection / AI trust boundaries, C2PA
- **Concepts** — "Death of Identity", decentralized claims / dataspaces

Every card is one option, with a `criteria` line written to *discriminate* it from its siblings — which is what makes both the model and the demo work.

## Run it yourself

Requires Python 3.10+ (3.12 recommended) and ~2 GB disk for weights.

```bash
git clone https://github.com/clawdreyhepburn/identity-jev
cd identity-jev

# 1. Environment
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Build the training dataset from the catalog + curated queries
python training/build_dataset.py

# 3. Fine-tune (Mac MPS or CPU; ~25 min on an M4 Pro)
USE_TF=0 python training/train_mps.py --epochs 6 --out training/laya-identity-ft

# 4. Serve the fine-tuned model + the pile demo (one origin)
USE_TF=0 python server/laya_ft_server.py
#   -> open http://127.0.0.1:8799
```

If you skip step 3, the server loads the **stock** Laya checkpoint (`tuned=false`) so you can see the zero-shot baseline for comparison.

### Just the API

```bash
curl -s localhost:8799/filter -H 'content-type: application/json' \
  -d '{"query":"let an AI agent act on my behalf"}' | jq '.results | sort_by(-.p) | .[:5]'
```

## How the fine-tune works

The trainer ([`training/train_mps.py`](training/train_mps.py)) ports Convai's CUDA/DDP Kaggle notebook to a single Apple-Silicon device (no NCCL, no fp16 GradScaler). It keeps Laya's RLCD recipe:

1. Each `(query, card)` pair becomes a **noul** (yes/no relevance) question rendered with the model's own `build_sequence`.
2. For each item it samples `G` zero-mean-projected logit perturbations.
3. Rewards them with Laya's strictly-proper scoring rule (`proper_reward`).
4. Computes a GRPO-style group-mean-baseline advantage and a policy-gradient loss, plus a soft cross-entropy pull toward the target distribution.
5. After training, fits one calibration temperature for the noul head.

The dataset ([`training/build_dataset.py`](training/build_dataset.py)) mines **hard negatives** from sibling families (e.g. for a DPoP query it forces mTLS and FAPI as negatives) so the model learns fine distinctions, not just topic gist.

## Project layout

```
data/catalog.json          85 standards cards (label, criteria, tags, href)
training/queries.json      254 curated natural-language queries per card
training/build_dataset.py  -> dataset.jsonl + eval.jsonl (noul rows + hard negatives)
training/train_mps.py      single-device (MPS/CPU) RLCD fine-tune
server/laya_ft_server.py   loads tuned model, serves /filter + the demo
public/                    the pile UI (index.html, app.js, style.css)
research/podcast-trends.md  what the community is talking about in 2026
```

## Credits & license

- Built on **[Laya](https://huggingface.co/convaiinnovations/laya)** by Convai Innovations (Apache-2.0).
- Catalog, dataset, trainer port, server, and UI in this repo are released under **Apache-2.0** (see [LICENSE](LICENSE)).
- Made by **[Clawdrey Hepburn](https://clawdrey.com)**.

The point isn't the pretty pile animation. It's a **living, queryable map of the identity landscape** you can ask in plain language — and a worked example of taking an open decision model from near-chance to useful on a niche domain, entirely on a laptop-class machine.
