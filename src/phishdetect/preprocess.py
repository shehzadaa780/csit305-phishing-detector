"""Step 2 of the workflow: privacy preprocessing.

- Masks e-mail addresses and phone numbers before anything is modelled or logged.
- Extracts URLs from the text WITHOUT visiting them (string parsing only).
- Normalises text so that formatting differences between corpora
  (e.g. HTML, tokenised Enron text, casing) do not leak into the model.
"""
from __future__ import annotations

import html
import re

MAX_CHARS = 20_000  # long inputs are truncated (edge case: very long e-mails)

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
# 1) explicit links: scheme or www. prefix (may legitimately contain '@')
EXPLICIT_URL_RE = re.compile(r"(?i)\b(?:https?://|hxxps?://|www\.)[^\s<>\"'()]+")
# 2) bare domains such as delivery-update.example.test/pay
BARE_DOMAIN_RE = re.compile(
    r"(?i)\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}(?:/[^\s<>\"'()]*)?"
)
TAG_RE = re.compile(r"<[^>]+>")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

# Bare-domain matches that are usually not links (file names, abbreviations)
_NOT_TLDS = {"eg", "ie", "etc", "am", "pm", "xls", "xlsx", "doc", "docx", "pdf", "txt",
             "jpg", "jpeg", "png", "gif", "zip", "exe", "htm", "html", "php", "csv", "ppt", "pptx"}
_TRAILING = ".,;:!?)]}'\""


def truncate(text: str) -> str:
    return (text or "")[:MAX_CHARS]


def _split_links(text: str) -> tuple[list[str], str]:
    """Return (links, text_without_links). Explicit links are taken first,
    then e-mail addresses are removed, then bare domains are found."""
    links: list[str] = []

    def take(m: re.Match) -> str:
        u = m.group(0).rstrip(_TRAILING)
        if u.lower() not in ("http://", "https://", "www."):
            links.append(u)
        return " urltoken "

    text = EXPLICIT_URL_RE.sub(take, text)
    text = EMAIL_RE.sub(" emailaddr ", text)

    def take_bare(m: re.Match) -> str:
        u = m.group(0).rstrip(_TRAILING)
        tld = u.split("/")[0].rsplit(".", 1)[-1].lower()
        if tld in _NOT_TLDS or len(u) < 5:
            return m.group(0)
        links.append(u)
        return " urltoken "

    text = BARE_DOMAIN_RE.sub(take_bare, text)
    seen, unique = set(), []
    for u in links:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique, text


def extract_urls(text: str) -> list[str]:
    """Return URL-like strings found in the text. Links are never opened."""
    return _split_links(text or "")[0]


def mask_pii(text: str) -> str:
    """Replace e-mail addresses and phone numbers with placeholder tokens."""
    text = EMAIL_RE.sub(" emailaddr ", text or "")
    return PHONE_RE.sub(" phonenum ", text)


def normalise(text: str) -> str:
    """Lower-case, strip HTML, replace links/e-mails/phones with tokens, keep a-z0-9."""
    text = html.unescape(text or "")
    text = TAG_RE.sub(" ", text)
    _, text = _split_links(text)
    text = PHONE_RE.sub(" phonenum ", text)
    text = text.lower()
    text = NON_ALNUM_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def preprocess(text: str) -> dict:
    """Full step-2 output used by the pipeline."""
    raw = truncate(text)
    hrefs = re.findall(r"(?i)href\s*=\s*[\"']?([^\"'\s>]+)", raw)
    visible = TAG_RE.sub(" ", html.unescape(raw))
    urls = extract_urls(" ".join(hrefs) + " " + visible)
    return {"clean_text": normalise(raw), "urls": urls}
