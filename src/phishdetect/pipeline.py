"""Runtime detection pipeline (workflow steps 1-7).

    Detector().analyze("sms", "Your parcel is held. Pay at ...")
"""
from __future__ import annotations

import time

import joblib
import numpy as np

from .data import ROOT
from .explain import explain_text, explain_url, summarise
from .preprocess import preprocess
from .url_features import normalise_url
from .url_model import url_matrix

FORMATS = ("email", "sms", "url")
MAX_URLS = 10
ADVICE = {
    "high": "Do not click links, reply or share details. Contact the organisation through its "
            "official website or phone number that you look up yourself.",
    "uncertain": "Suspicious - check before acting. Verify the sender through an official channel "
                 "before clicking links or paying.",
    "low": "No strong warning signs found. This is decision support, not a guarantee of safety.",
}


class InputError(ValueError):
    """Raised for inputs the detector cannot analyse (empty, wrong type)."""


def band_for(risk: int, thresholds: dict) -> str:
    if risk >= thresholds["high"]:
        return "high"
    if risk >= thresholds["uncertain"]:
        return "uncertain"
    return "low"


class Detector:
    def __init__(self, model_dir=None):
        model_dir = model_dir or ROOT / "models"
        self.art = {}
        for fmt in FORMATS:
            path = model_dir / f"{fmt}.joblib"
            if not path.exists():
                raise FileNotFoundError(f"{path} missing - run `python -m phishdetect.train` first")
            self.art[fmt] = joblib.load(path)
        self.thresholds = self.art["sms"]["thresholds"]

    # ---- step 4: classifiers -------------------------------------------------
    def text_probability(self, fmt: str, clean_text: str) -> float:
        a = self.art[fmt]
        return float(a["model"].predict_proba(a["vectoriser"].transform([clean_text]))[0, 1])

    def url_probabilities(self, urls: list[str]) -> np.ndarray:
        a = self.art["url"]
        return a["model"].predict_proba(url_matrix(a["vectoriser"], a["scaler"], urls))[:, 1]

    # ---- steps 1-7 -----------------------------------------------------------
    def analyze(self, input_type: str, text: str, explain: bool = True) -> dict:
        t0 = time.perf_counter()
        input_type = (input_type or "").lower().strip()
        if input_type not in FORMATS:
            raise InputError(f"type must be one of {FORMATS}")
        if not text or not text.strip():
            raise InputError("input is empty")

        notes: list[str] = []
        if input_type == "url":
            found = preprocess(text)["urls"]
            if not found and " " in text.strip():
                raise InputError("this does not look like a URL")
            urls = (found or [text.strip()])[:1]
            if not normalise_url(urls[0]) or len(normalise_url(urls[0])) < 4:
                raise InputError("this does not look like a URL")
            clean, p_text = "", None
            versions = [self.art["url"]["version"]]
        else:
            pre = preprocess(text)
            clean, urls = pre["clean_text"], pre["urls"]
            if len(urls) > MAX_URLS:
                notes.append(f"Only the first {MAX_URLS} links were checked.")
                urls = urls[:MAX_URLS]
            if len(clean.split()) < 3:
                notes.append("Very short message: little evidence, so the score is less reliable.")
            letters = [c for c in text if c.isalpha()]
            if letters and sum(not c.isascii() for c in letters) / len(letters) > 0.3:
                notes.append("Most of the text is not in English. The text model was trained on "
                             "English only, so only the links were assessed reliably.")
            elif not letters:
                notes.append("No readable words were found (symbol-only text).")
            p_text = self.text_probability(input_type, clean) if clean else 0.0
            versions = [self.art[input_type]["version"]] + ([self.art["url"]["version"]] if urls else [])

        p_urls = self.url_probabilities(urls) if urls else np.array([])
        worst = int(np.argmax(p_urls)) if len(p_urls) else None
        p_url = float(p_urls[worst]) if worst is not None else None
        t_classify = time.perf_counter() - t0

        # step 5: risk mapping - the higher of the text and link scores is used
        p = max(x for x in (p_text, p_url) if x is not None)
        risk = int(round(100 * p))
        band = band_for(risk, self.thresholds)
        label = "phishing" if band == "high" else ("suspicious" if band == "uncertain" else "likely safe")

        # step 6: explanation
        cues: list[dict] = []
        if explain:
            if input_type != "url":
                cues += explain_text(self.art[input_type], clean)
            if worst is not None:
                cues += explain_url(self.art["url"], urls[worst])
        if band != "low" and not cues:
            notes.append("No single strong cue - the score comes from the message as a whole.")

        # step 7: response
        return {
            "label": label,
            "risk": risk,
            "band": band,
            "text_probability": None if p_text is None else round(p_text, 4),
            "url_probability": None if p_url is None else round(p_url, 4),
            "checked_urls": urls,
            "riskiest_url": urls[worst] if worst is not None else None,
            "cues": cues,
            "explanation": summarise(cues, band),
            "advice": ADVICE[band],
            "notes": notes,
            "model_version": "+".join(versions),
            "timing_ms": {"classify": round(t_classify * 1000, 2),
                          "total": round((time.perf_counter() - t0) * 1000, 2)},
        }
