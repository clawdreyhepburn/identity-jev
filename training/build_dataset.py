#!/usr/bin/env python3
"""
Build a labeled fine-tuning dataset for Identity-Jev over the Laya `noul` primitive.

Each training row is: (query, card) -> label in {0.0, 1.0}
rendered as a Laya noul question:
  state      = {"query": <query>}
  question   = noul: "Is <card.label> (<card.criteria>) a strong match for the query?"
  target     = 1.0 (relevant) | 0.0 (not relevant)

Positives come from:
  - curated natural-language queries per card (data/queries.json)
  - the card's own tags/label (keyword-style queries)
Hard negatives come from:
  - sibling cards in the same family that are plausible-but-wrong for a query
  - random other cards

Output: training/dataset.jsonl  (one JSON row per line)
Also emits a held-out eval split: training/eval.jsonl

Run:  python training/build_dataset.py
"""
import json
import random
from pathlib import Path

random.seed(1337)
ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "data" / "catalog.json").read_text())
CARDS = {c["key"]: c for c in CATALOG["cards"]}
QUERIES = {k: v for k, v in json.loads((ROOT / "training" / "queries.json").read_text()).items() if not k.startswith("_")}

# Families: cards that are semantically adjacent. Used to mine HARD negatives —
# the sibling that a naive matcher would confuse with the true answer.
FAMILIES = {
    "sub_claim": ["oidc_core", "rfc9068_jwt_at", "rfc7519_jwt", "rfc7662_introspection",
                  "oidc_userinfo", "cwt", "rfc7523_jwt_bearer"],
    "pop": ["rfc9449_dpop", "rfc8705_mtls", "fapi2"],
    "delegation": ["rfc8693_token_exchange", "oauth_actor_profile", "id_jag",
                   "txn_tokens", "ft_jwt", "waffles", "ovid", "agentic_ai_identity"],
    "authz_model": ["authzen", "tbac", "intent_based_access", "rfc9396_rar", "cedar",
                    "rar_cedar", "zero_standing_privilege"],
    "continuous": ["shared_signals_ssf", "caep", "risc", "global_token_revocation",
                   "oauth_status_list", "itdr", "openid_provider_commands"],
    "workload": ["spiffe_svid", "wimse_s2s", "wimse_ai_agent", "wimse_ect",
                 "nhi_governance", "txn_tokens"],
    "vc": ["verifiable_credentials", "did_core", "sd_jwt", "sd_jwt_vc", "oid4vci",
           "oid4vp", "mdl_iso18013", "eudiw_arf", "decentralized_claims"],
    "jose": ["rfc7515_jws", "rfc7516_jwe", "rfc7517_jwk", "rfc7518_jwa",
             "jose_hpke", "cose", "cwt"],
    "oauth_core": ["rfc6749_oauth2", "oauth21", "rfc7636_pkce", "rfc9126_par",
                   "rfc9101_jar", "rfc9207_iss_response", "rfc8414_as_metadata"],
    "agent_id": ["agentic_ai_identity", "ai_identity_control_plane", "mcp_authorization",
                 "intent_based_access", "aiagent_auth", "ovid", "agentic_jwt_unforge",
                 "prompt_injection"],
    "passwordless": ["passkeys_webauthn"],
    "provisioning": ["scim2", "ipsie", "nhi_governance", "openid_provider_commands"],
}

# Reverse index: card -> families it belongs to
CARD_FAMILIES = {}
for fam, keys in FAMILIES.items():
    for k in keys:
        CARD_FAMILIES.setdefault(k, []).append(fam)


def noul_instruction(card, query):
    return (f'Query: "{query}". Is the standard "{card["label"]}" '
            f'\u2014 {card["criteria"]} \u2014 a strong, direct match for this query?')


def make_row(query, card_key, label):
    card = CARDS[card_key]
    return {
        "state": {"query": query},
        "question": {
            "type": "noul",
            "instructions": noul_instruction(card, query),
        },
        "target": float(label),
        "meta": {"query": query, "card": card_key, "label": int(label)},
    }


def hard_negatives(query, positive_keys, n=3):
    """Pick sibling cards (same family) that are NOT the positive answer."""
    sib = set()
    for pk in positive_keys:
        for fam in CARD_FAMILIES.get(pk, []):
            for k in FAMILIES[fam]:
                if k not in positive_keys:
                    sib.add(k)
    sib = list(sib)
    random.shuffle(sib)
    return sib[:n]


def keyword_queries(card):
    """Cheap positive queries from label + salient tags (string-search style)."""
    qs = set()
    # short tag tokens that a person might literally type
    for t in card.get("tags", []):
        if 1 <= len(t.split()) <= 4 and len(t) >= 2:
            qs.add(t)
    return list(qs)[:6]


def build():
    rows = []
    # 1. curated NL positives + mined negatives
    for card_key, qlist in QUERIES.items():
        if card_key not in CARDS:
            raise SystemExit(f"queries.json references unknown card: {card_key}")
        for q in qlist:
            rows.append(make_row(q, card_key, 1.0))
            for nk in hard_negatives(q, [card_key], n=3):
                rows.append(make_row(q, nk, 0.0))
            # 1 random easy negative
            others = [k for k in CARDS if k != card_key]
            rows.append(make_row(q, random.choice(others), 0.0))

    # 2. keyword positives (label/tag) so literal queries still work
    for card_key, card in CARDS.items():
        for q in keyword_queries(card):
            rows.append(make_row(q, card_key, 1.0))
            for nk in hard_negatives(q, [card_key], n=2):
                rows.append(make_row(q, nk, 0.0))

    random.shuffle(rows)
    # 90/10 split
    cut = int(len(rows) * 0.9)
    train, ev = rows[:cut], rows[cut:]

    out_train = ROOT / "training" / "dataset.jsonl"
    out_eval = ROOT / "training" / "eval.jsonl"
    with out_train.open("w") as f:
        for r in train:
            f.write(json.dumps(r) + "\n")
    with out_eval.open("w") as f:
        for r in ev:
            f.write(json.dumps(r) + "\n")

    pos = sum(1 for r in rows if r["target"] == 1.0)
    neg = len(rows) - pos
    print(f"cards: {len(CARDS)}")
    print(f"curated NL queries: {sum(len(v) for v in QUERIES.values())} "
          f"across {len(QUERIES)} cards")
    print(f"total rows: {len(rows)}  (pos {pos} / neg {neg})")
    print(f"train: {len(train)}  eval: {len(ev)}")
    print(f"wrote {out_train}")
    print(f"wrote {out_eval}")


if __name__ == "__main__":
    build()
