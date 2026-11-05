"""Step 3 (URL path): lexical URL features computed from the string only.

Links are parsed with urllib, never requested. Following Sahingoz et al. [2],
features describe length, host structure, special characters and misleading
words. The scheme (http/https) and a leading 'www.' are removed before feature
extraction: in the training data these differ systematically between the
phishing and legitimate lists, so keeping them would let the model learn how the
dataset was collected instead of what phishing looks like (leakage control).
"""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

import numpy as np

SUSPICIOUS_WORDS = [
    "login", "log-in", "signin", "sign-in", "verify", "verification", "secure", "account",
    "update", "confirm", "banking", "bank", "password", "webscr", "cmd", "billing",
    "unlock", "suspend", "wallet", "payment", "invoice", "support", "recover", "auth",
]
SHORTENERS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
              "cutt.ly", "rebrand.ly", "shorturl.at", "tiny.cc", "rb.gy", "t.ly"}
COMMON_TLDS = {"com", "org", "net", "edu", "gov", "uk", "de", "au", "ca", "ae", "in", "io", "co"}

# brand list from the Sahingoz et al. repository (allbrands.txt), shipped with the package so
# live predictions use exactly the same features as training
_BRANDS_FILE = Path(__file__).resolve().parent / "brands.txt"
_DEFAULT_BRANDS = ["paypal", "apple", "icloud", "amazon", "netflix", "microsoft", "office365",
                   "outlook", "google", "facebook", "instagram", "whatsapp", "dhl", "fedex",
                   "ups", "aramex", "emirates", "etisalat", "chase", "wellsfargo", "hsbc", "ebay"]


def _load_brands() -> list[str]:
    brands = set(_DEFAULT_BRANDS)
    if _BRANDS_FILE.exists():
        brands |= {b.strip().lower() for b in _BRANDS_FILE.read_text().splitlines() if len(b.strip()) >= 4}
    return sorted(brands)


BRANDS = _load_brands()

# name -> plain-language description used by the explanation engine
FEATURES: dict[str, str] = {
    "url_length": "the link is unusually long",
    "host_length": "the website name is unusually long",
    "path_length": "the part after the website name is long",
    "num_dots_host": "the website name has many dots (many sub-domains)",
    "num_hyphens_host": "the website name contains several hyphens",
    "num_digits": "the link contains many digits",
    "digit_ratio": "a large share of the link is digits",
    "num_special": "the link contains many special characters (= ? & % _ ~)",
    "num_path_segments": "the link has many folder levels",
    "query_length": "the link carries a long query string",
    "has_ip_host": "the link uses a raw IP address instead of a website name",
    "has_at_symbol": "the link contains '@', which can hide the real destination",
    "has_double_slash_path": "the link contains '//' inside the path (a redirect trick)",
    "is_shortener": "the link uses a URL shortener that hides the real destination",
    "has_punycode": "the website name uses punycode (xn--), often used for look-alike letters",
    "uncommon_tld": "the website ends in an uncommon domain extension",
    "suspicious_words": "the link contains words like login / verify / secure / account",
    "brand_outside_domain": "a well-known brand name appears in the link but is not the real website",
    "host_entropy": "the website name looks random",
    "longest_token": "the link contains a very long unbroken word or code",
    "has_port": "the link specifies an unusual port number",
}
FEATURE_NAMES = list(FEATURES)


def normalise_url(url: str) -> str:
    u = (url or "").strip().strip("<>\"'")
    u = re.sub(r"(?i)^hxxp", "http", u)
    u = re.sub(r"(?i)^[a-z][a-z0-9+.-]*://", "", u)
    u = re.sub(r"(?i)^www\d?\.", "", u)
    return u


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def split_url(url: str) -> tuple[str, str, str, int | None]:
    """Return (host, path, query, port) for a normalised URL string."""
    u = normalise_url(url)
    try:
        parts = urlsplit("http://" + u)
        host = (parts.hostname or "").lower()
        port = parts.port
    except ValueError:  # malformed (e.g. bad port) -> treat whole string as host
        parts = None
        host, port = u.split("/")[0].lower(), None
    path = parts.path if parts else "/".join(u.split("/")[1:])
    query = parts.query if parts else ""
    return host, path, query, port


def registered_domain(host: str) -> str:
    """Approximate registered domain (last two labels; three for e.g. co.uk)."""
    labels = [x for x in host.split(".") if x]
    if len(labels) >= 3 and labels[-2] in {"co", "com", "ac", "gov", "org", "net", "edu"} and len(labels[-1]) == 2:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def extract(url: str) -> dict[str, float]:
    u = normalise_url(url)
    host, path, query, port = split_url(url)
    low = u.lower()
    reg = registered_domain(host)
    reg_name = reg.split(".")[0] if reg else ""
    tokens = re.split(r"[^a-z0-9]+", low)
    token_set = set(tokens)
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    return {
        "url_length": len(u),
        "host_length": len(host),
        "path_length": len(path),
        "num_dots_host": host.count("."),
        "num_hyphens_host": host.count("-"),
        "num_digits": sum(c.isdigit() for c in u),
        "digit_ratio": sum(c.isdigit() for c in u) / max(len(u), 1),
        "num_special": sum(u.count(c) for c in "=?&%_~"),
        "num_path_segments": len([p for p in path.split("/") if p]),
        "query_length": len(query),
        "has_ip_host": float(bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host))),
        "has_at_symbol": float("@" in u),
        "has_double_slash_path": float("//" in u),
        "is_shortener": float(host in SHORTENERS),
        "has_punycode": float("xn--" in host),
        "uncommon_tld": float(tld.isalpha() and tld not in COMMON_TLDS),
        "suspicious_words": float(sum(w in low for w in SUSPICIOUS_WORDS)),
        "brand_outside_domain": float(any(b in token_set and b != reg_name for b in BRANDS)),
        "host_entropy": _entropy(host),
        "longest_token": float(max((len(t) for t in tokens), default=0)),
        "has_port": float(port is not None),
    }


def extract_matrix(urls: list[str]) -> np.ndarray:
    return np.array([[f[n] for n in FEATURE_NAMES] for f in map(extract, urls)], dtype=float)
