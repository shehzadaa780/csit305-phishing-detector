"""Offline training pipeline (Stages 5-6): fit format-specific baselines on the
training split, choose regularisation on the validation split, calibrate the
probabilities on the validation split and export versioned models to the
model registry (models/).

Run:  python -m phishdetect.train
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.svm import LinearSVC

from . import __version__
from .data import LOADERS, ROOT, SEED, describe, split
from .url_features import FEATURE_NAMES, extract_matrix
from .url_model import fit_transformers, url_matrix

MODELS = ROOT / "models"
THRESHOLDS = {"uncertain": 40, "high": 70}  # starting values from the proposal (Section 4.1)


def _vectoriser() -> TfidfVectorizer:
    return TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9, sublinear_tf=True,
                           max_features=50_000, token_pattern=r"(?u)\b[a-z0-9]{2,}\b")


def _pick_C(make, Xtr, ytr, Xva, yva, grid=(0.3, 1.0, 3.0, 10.0, 30.0)):
    """Choose regularisation strength by validation F1 (never touches the test set)."""
    scores = {}
    for C in grid:
        m = make(C).fit(Xtr, ytr)
        scores[C] = f1_score(yva, m.predict(Xva))
    best = max(scores, key=scores.get)
    return best, {str(k): round(v, 4) for k, v in scores.items()}


def _calibrate(model, Xva, yva):
    return CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid").fit(Xva, yva)


def train_text(fmt: str) -> dict:
    df, clean_stats = LOADERS[fmt]()
    parts = split(df)
    vec = _vectoriser().fit(parts["train"]["text"])
    Xtr, Xva = vec.transform(parts["train"]["text"]), vec.transform(parts["val"]["text"])
    ytr, yva = parts["train"]["label"].values, parts["val"]["label"].values

    C, c_scores = _pick_C(lambda C: LogisticRegression(C=C, class_weight="balanced", max_iter=3000,
                                                       random_state=SEED), Xtr, ytr, Xva, yva)
    base = LogisticRegression(C=C, class_weight="balanced", max_iter=3000, random_state=SEED).fit(Xtr, ytr)
    model = _calibrate(base, Xva, yva)

    Cs, cs_scores = _pick_C(lambda C: LinearSVC(C=C, class_weight="balanced", max_iter=10000, random_state=SEED),
                            Xtr, ytr, Xva, yva)
    svm = _calibrate(LinearSVC(C=Cs, class_weight="balanced", max_iter=10000, random_state=SEED).fit(Xtr, ytr), Xva, yva)

    return {
        "format": fmt, "kind": "text", "vectoriser": vec, "base": base, "model": model,
        "comparator": svm, "comparator_name": f"tfidf-linearsvc(C={Cs})",
        "model_name": f"tfidf-logreg(C={C})",
        "tuning": {"logreg_val_f1_by_C": c_scores, "svm_val_f1_by_C": cs_scores},
        "data": {"cleaning": clean_stats, **{k: describe(v) for k, v in parts.items()}},
    }


def train_url() -> dict:
    """v0.2.0: hybrid logistic regression (char n-grams + lexical features).
    The v0.1.0 random forest on lexical features is kept as the comparator."""
    df, clean_stats = LOADERS["url"]()
    parts = split(df)
    tr, va = parts["train"]["raw"].tolist(), parts["val"]["raw"].tolist()
    ytr, yva = parts["train"]["label"].values, parts["val"]["label"].values

    vec, scaler = fit_transformers(tr)
    Xtr, Xva = url_matrix(vec, scaler, tr), url_matrix(vec, scaler, va)
    C, c_scores = _pick_C(lambda C: LogisticRegression(C=C, class_weight="balanced", max_iter=5000,
                                                       random_state=SEED), Xtr, ytr, Xva, yva)
    base = LogisticRegression(C=C, class_weight="balanced", max_iter=5000, random_state=SEED).fit(Xtr, ytr)
    model = _calibrate(base, Xva, yva)

    Ltr, Lva = extract_matrix(tr), extract_matrix(va)
    rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced",
                                n_jobs=-1, random_state=SEED).fit(Ltr, ytr)
    rf = _calibrate(rf, Lva, yva)
    return {
        "format": "url", "kind": "url", "vectoriser": vec, "scaler": scaler, "base": base, "model": model,
        "comparator": rf, "comparator_kind": "lexical",
        "model_name": f"url-charngram+lexical-logreg(C={C})",
        "comparator_name": "url-lexical-randomforest (v0.1.0 design)",
        "feature_names": FEATURE_NAMES, "tuning": {"logreg_val_f1_by_C": c_scores},
        "data": {"cleaning": clean_stats, **{k: describe(v) for k, v in parts.items()}},
    }


def main() -> None:
    MODELS.mkdir(exist_ok=True)
    registry = {"package_version": __version__, "seed": SEED, "thresholds": THRESHOLDS,
                "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "models": {}}
    for fmt in ("email", "sms", "url"):
        t0 = time.time()
        art = train_text(fmt) if fmt != "url" else train_url()
        version = f"{fmt}-v{__version__}"
        art["version"] = version
        art["thresholds"] = THRESHOLDS
        joblib.dump(art, MODELS / f"{fmt}.joblib", compress=3)
        registry["models"][fmt] = {
            "version": version, "model": art["model_name"], "comparator": art["comparator_name"],
            "data": art["data"], "train_seconds": round(time.time() - t0, 1),
            **({"tuning": art["tuning"]} if "tuning" in art else {}),
        }
        print(f"[train] {fmt}: {art['model_name']} saved as {version} ({time.time() - t0:.1f}s)")
    (MODELS / "registry.json").write_text(json.dumps(registry, indent=2))


if __name__ == "__main__":
    main()
