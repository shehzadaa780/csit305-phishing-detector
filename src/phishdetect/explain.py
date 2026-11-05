"""Step 6: explanation engine.

Explanations are built only from evidence the model actually used:
- Text models (logistic regression): each word/phrase's contribution is its
  TF-IDF value x model coefficient, i.e. the exact amount it adds to the
  model's score. Only words present in the input with a positive contribution
  are shown.
- URL model (v0.2.0, logistic regression on character fragments + lexical
  features): the same exact linear contributions. A lexical cue is shown only
  when the link's value is ABOVE the training average AND a higher value
  raises risk, so the wording ("unusually long", "contains '@'") is true.
  Fragment cues quote the actual characters found in the link.
- Very common words (the, your, to ...) still count in the score but are not
  shown as warning signs, because they mean nothing to a user (v0.2.0).
No external LLM is used, so explanations cannot invent facts.
"""
from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from .url_features import FEATURES, FEATURE_NAMES
from .url_model import url_matrix, url_text

MIN_WEIGHT = 0.05  # ignore negligible contributions
KEEP_WORDS = {"urltoken", "phonenum", "emailaddr", "now", "call", "free", "last"}
TOKEN_DISPLAY = {"urltoken": "a link", "phonenum": "a phone number", "emailaddr": "an e-mail address"}
CATEGORIES = {
    "urgency or pressure": {"urgent", "immediately", "now", "today", "expire", "expires", "expired",
                            "suspended", "suspend", "limited", "final", "last", "asap", "deadline",
                            "within", "hours", "warning", "alert", "attention", "important"},
    "request for account details or log-in": {"password", "login", "log", "verify", "verification",
                                              "account", "confirm", "update", "security", "unlock",
                                              "credentials", "sign", "signin", "username", "validate",
                                              "identity", "access", "restore"},
    "money, payment or bank details": {"pay", "payment", "fee", "invoice", "bank", "card", "transfer",
                                       "refund", "cash", "billing", "credit", "paypal", "charge",
                                       "dollars", "fund", "funds", "wire"},
    "prize, reward or free offer": {"win", "won", "winner", "prize", "free", "reward", "claim", "award",
                                    "gift", "bonus", "selected", "congratulations", "guaranteed", "offer"},
    "call to action (click / call / reply)": {"click", "urltoken", "link", "visit", "call", "phonenum",
                                              "txt", "text", "reply", "stop", "here", "mobile"},
    "parcel or delivery": {"parcel", "package", "delivery", "courier", "shipment", "shipping", "held"},
}


def _names(art: dict):
    """Vocabulary lookup, computed once per model (it is slow for 200k features)."""
    if "_names" not in art:
        art["_names"] = art["vectoriser"].get_feature_names_out()
    return art["_names"]


def _category(term: str) -> str | None:
    for word in term.split():
        for cat, words in CATEGORIES.items():
            if word in words:
                return cat
    return None


def _display(term: str) -> str:
    return " ".join(TOKEN_DISPLAY.get(w, w) for w in term.split())


def explain_text(art: dict, clean_text: str, top_k: int = 6) -> list[dict]:
    """Top input terms pushing the text model towards 'phishing'."""
    vec, base = art["vectoriser"], art["base"]
    x = vec.transform([clean_text])
    if x.nnz == 0:
        return []
    coef = base.coef_.ravel()
    contrib = x.multiply(coef).tocsr()
    idx, vals = contrib.indices, contrib.data
    order = np.argsort(-vals)
    names = _names(art)
    cues, seen = [], set()
    for i in order:
        if vals[i] <= 0 or len(cues) >= top_k:
            break
        term = names[idx[i]]
        if all(w in ENGLISH_STOP_WORDS and w not in KEEP_WORDS for w in term.split()):
            continue  # counts in the score, but is not a meaningful warning sign
        # skip a unigram already covered by a chosen bigram (and vice versa)
        if any(w in seen for w in term.split()):
            continue
        seen.update(term.split())
        cues.append({"source": "text", "evidence": _display(term), "category": _category(term),
                     "weight": round(float(vals[i]), 3)})
    return cues


def explain_url(art: dict, url: str, top_k: int = 4) -> list[dict]:
    """Exact linear contributions for the hybrid URL model."""
    vec, scaler, base = art["vectoriser"], art["scaler"], art["base"]
    x = url_matrix(vec, scaler, [url])
    coef = base.coef_.ravel()
    n_char = len(vec.vocabulary_)
    contrib = x.multiply(coef).tocsr()
    cues: list[dict] = []

    # (a) readable link properties
    dense = x[:, n_char:].toarray().ravel()
    lex = [(j, dense[j] * coef[n_char + j]) for j in range(len(FEATURE_NAMES))
           if dense[j] > 0 and coef[n_char + j] > 0]
    for j, w in sorted(lex, key=lambda t: -t[1])[:top_k]:
        if w < MIN_WEIGHT:
            break
        name = FEATURE_NAMES[j]
        cues.append({"source": "url", "evidence": FEATURES[name], "category": "link structure",
                     "feature": name, "z": round(float(dense[j]), 3), "weight": round(float(w), 3)})

    # (b) text fragments inside the link
    names = _names(art)
    frag = [(names[i], v) for i, v in zip(contrib.indices, contrib.data) if i < n_char and v > 0]
    chosen: list[str] = []
    for f, w in sorted(frag, key=lambda t: -t[1]):
        f = f.strip()
        if len(chosen) >= 3 or w < MIN_WEIGHT:
            break
        if len(f) < 4 or any(f in c or c in f for c in chosen):
            continue
        chosen.append(f)
        cues.append({"source": "url", "evidence": f"the link contains the fragment '{f}', common in phishing links",
                     "category": "link structure", "fragment": f, "weight": round(float(w), 3)})
    return cues


def summarise(cues: list[dict], band: str) -> str:
    """Plain-language sentence built only from the extracted cues."""
    if band == "low":
        return "No strong warning signs were found. Stay careful with unexpected requests."
    if not cues:
        return "The score is raised by the overall wording, but no single clear warning sign stands out."
    cats = []
    for c in sorted(cues, key=lambda c: c["category"] is None):
        label = c["category"] or "wording often seen in scams"
        if c["source"] == "url":
            label = c["evidence"]
        if label not in cats:
            cats.append(label)
    head = "This looks risky because" if band == "high" else "Be careful: this may be risky because"
    return f"{head}: " + "; ".join(cats[:4]) + "."
