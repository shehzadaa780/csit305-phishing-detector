"""Evaluation harness (Stage 8). Every number reported in the paper comes from here.

Run:  python -m phishdetect.evaluate
Writes results/metrics.json, results/criteria_table.csv, results/challenge_results.csv,
evidence/edge_case_results.csv and figures in results/figures/.

Each model is scored ONCE on its held-out test split, which was never used for
training, C selection or calibration. Formats are reported separately.
"""
from __future__ import annotations

import json
import time

import joblib
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sklearn.calibration import CalibratedClassifierCV, calibration_curve  # noqa: E402
from sklearn.frozen import FrozenEstimator  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import brier_score_loss, confusion_matrix, f1_score  # noqa: E402

from .data import LOADERS, ROOT, SEED, split  # noqa: E402
from .pipeline import Detector  # noqa: E402
from .preprocess import normalise  # noqa: E402
from .train import _vectoriser  # noqa: E402
from .url_features import extract_matrix  # noqa: E402
from .url_model import url_matrix, url_text  # noqa: E402

RESULTS, FIGS, EVIDENCE = ROOT / "results", ROOT / "results" / "figures", ROOT / "evidence"
RNG = np.random.default_rng(SEED)
N_BOOT = 1000
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e",
                     "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})


# ---------------------------------------------------------------- metrics
def detection_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    risk = np.round(100 * p).astype(int)
    pred = (risk >= 70).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    neg = (y == 0)
    return {
        "support": {"phishing": int(y.sum()), "legitimate": int(neg.sum())},
        "confusion_high_band": {"TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn)},
        "precision": round(prec, 4), "recall_high": round(rec, 4),
        "f1": round(2 * prec * rec / (prec + rec), 4) if prec + rec else 0.0,
        "macro_f1": round(f1_score(y, pred, average="macro"), 4),
        "accuracy": round((tp + tn) / len(y), 4),
        "specificity": round(tn / (tn + fp), 4) if tn + fp else 0.0,
        "false_positive_rate_high": round(fp / (fp + tn), 4) if fp + tn else 0.0,
        "recall_high_or_uncertain": round(float(((risk >= 40) & (y == 1)).sum() / max(y.sum(), 1)), 4),
        "uncertain_band_load_legit": round(float(((risk >= 40) & (risk < 70) & neg).sum() / max(neg.sum(), 1)), 4),
        "brier": round(brier_score_loss(y, p), 4),
    }


def f1_high(y, p):
    return f1_score(y, (np.round(100 * p) >= 70).astype(int), zero_division=0)


def bootstrap_f1(y, p_main, p_comp) -> dict:
    n = len(y)
    f_main, diffs = [], []
    for _ in range(N_BOOT):
        i = RNG.integers(0, n, n)
        a, b = f1_high(y[i], p_main[i]), f1_high(y[i], p_comp[i])
        f_main.append(a)
        diffs.append(a - b)
    q = lambda v: [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]  # noqa: E731
    return {"f1_main_95ci": q(f_main), "f1_main_minus_comparator": round(float(np.mean(diffs)), 4),
            "f1_diff_95ci": q(diffs)}


def precision_at_recall_low_prevalence(y, p, prevalence=0.05, target_recall=0.90, reps=200) -> dict:
    """Simulate a realistic inbox: keep every legitimate item, sample phishing to 5%."""
    pos, neg = p[y == 1], p[y == 0]
    n_pos = max(int(round(prevalence * len(neg) / (1 - prevalence))), 10)
    precs = []
    for _ in range(reps):
        s = RNG.choice(pos, size=min(n_pos, len(pos)), replace=len(pos) < n_pos)
        thr = np.quantile(s, 1 - target_recall)          # threshold that keeps 90% recall
        tp, fp = (s >= thr).sum(), (neg >= thr).sum()
        precs.append(tp / (tp + fp))
    return {"prevalence": prevalence, "n_phishing_sampled": n_pos, "n_legitimate": int(len(neg)),
            "precision_at_90_recall_mean": round(float(np.mean(precs)), 4),
            "precision_95ci": [round(float(np.percentile(precs, 2.5)), 4),
                               round(float(np.percentile(precs, 97.5)), 4)]}


# ---------------------------------------------------------------- per format
def test_probabilities(fmt: str, art: dict):
    df, _ = LOADERS[fmt]()
    test = split(df)["test"]
    if fmt == "url":
        urls = test["raw"].tolist()
        X, Xc = url_matrix(art["vectoriser"], art["scaler"], urls), extract_matrix(urls)
    else:
        X = Xc = art["vectoriser"].transform(test["text"])
    return test, art["model"].predict_proba(X)[:, 1], art["comparator"].predict_proba(Xc)[:, 1]


def email_time_split() -> dict:
    """Robustness to newer attacks: train on phishing up to 2019, test on 2020-2022."""
    df, _ = LOADERS["email"]()
    phish, legit = df[df.label == 1].copy(), df[df.label == 0].copy()
    years = phish["date"].dt.year
    old, new = phish[years <= 2019], phish[years >= 2020]
    def thirds(d):  # shuffled 70/15/15 slices
        d = d.sample(frac=1, random_state=SEED)
        n = len(d)
        return d.iloc[: int(.7 * n)], d.iloc[int(.7 * n): int(.85 * n)], d.iloc[int(.85 * n):]
    l_tr, l_va, l_te = thirds(legit)
    o_tr, o_va, o_te = thirds(old)
    tr, va = pd.concat([l_tr, o_tr]), pd.concat([l_va, o_va])
    vec = _vectoriser().fit(tr["text"])
    base = LogisticRegression(C=10.0, class_weight="balanced", max_iter=3000, random_state=SEED).fit(
        vec.transform(tr["text"]), tr["label"])
    model = CalibratedClassifierCV(FrozenEstimator(base), method="sigmoid").fit(vec.transform(va["text"]), va["label"])
    r = lambda d: float((np.round(100 * model.predict_proba(vec.transform(d["text"]))[:, 1]) >= 70).mean())  # noqa: E731
    rec_old, rec_new = r(o_te), r(new)
    fpr = r(l_te)
    return {"train_phishing_years": "2015-2019", "test_phishing_years": "2020-2022",
            "n_old_test": len(o_te), "n_new_test": len(new),
            "recall_high_old": round(rec_old, 4), "recall_high_new": round(rec_new, 4),
            "recall_drop_points": round(100 * (rec_old - rec_new), 1),
            "false_positive_rate_high": round(fpr, 4)}


# ---------------------------------------------------------------- figures
def fig_confusion(results: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.9))
    for ax, (fmt, r) in zip(axes, results.items()):
        c = r["main"]["confusion_high_band"]
        m = np.array([[c["TN"], c["FP"]], [c["FN"], c["TP"]]])
        ax.imshow(m / m.sum(axis=1, keepdims=True), cmap="Blues", vmin=0, vmax=1)
        for (i, j), v in np.ndenumerate(m):
            share = v / m[i].sum()
            ax.text(j, i, f"{v:,}\n({share:.1%})", ha="center", va="center",
                    color="#ffffff" if share > .6 else INK, fontsize=8)
        ax.set_xticks([0, 1], ["legit", "phishing"])
        ax.set_yticks([0, 1], ["legit", "phishing"])
        ax.set_xlabel("predicted (high band = phishing)")
        ax.set_ylabel("actual")
        ax.set_title(f"{fmt.upper()}  (n={m.sum():,})", fontsize=9, color=INK, loc="left")
        ax.spines[:].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGS / "confusion_matrices.png")
    plt.close(fig)


def fig_reliability(probs: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.9), sharey=True)
    for ax, (fmt, (y, p)) in zip(axes, probs.items()):
        frac, mean = calibration_curve(y, p, n_bins=10, strategy="quantile")
        ax.plot([0, 1], [0, 1], color=MUTED, lw=1, ls="--", label="perfect calibration")
        ax.plot(mean, frac, color=BLUE, lw=2, marker="o", ms=4, label="model")
        ax.grid(color=GRID, lw=.6)
        ax.set_title(f"{fmt.upper()}  Brier={brier_score_loss(y, p):.3f}", fontsize=9, color=INK, loc="left")
        ax.set_xlabel("predicted probability")
    axes[0].set_ylabel("observed share phishing")
    axes[0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGS / "reliability.png")
    plt.close(fig)


def fig_risk_hist(probs: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.9))
    bins = np.arange(0, 105, 5)
    for ax, (fmt, (y, p)) in zip(axes, probs.items()):
        risk = np.round(100 * p)
        for cls, col, name in ((0, BLUE, "legitimate"), (1, ORANGE, "phishing / spam")):
            w = np.ones((y == cls).sum()) / (y == cls).sum()
            ax.hist(risk[y == cls], bins=bins, weights=w, color=col, alpha=.75, label=name,
                    edgecolor="#fcfcfb", linewidth=1)
        for t in (40, 70):
            ax.axvline(t, color=MUTED, lw=1, ls=":")
        ax.set_yscale("log")
        ax.set_title(fmt.upper(), fontsize=9, color=INK, loc="left")
        ax.set_xlabel("risk score (bands: 0-39 | 40-69 | 70-100)")
        ax.grid(axis="y", color=GRID, lw=.6)
    axes[0].set_ylabel("share of class (log)")
    axes[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "risk_distribution.png")
    plt.close(fig)


# ---------------------------------------------------------------- challenge / edge / explanations
def run_challenge(det: Detector) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(EVIDENCE / "challenge_set.csv")
    rows = []
    for r in df.itertuples():
        out = det.analyze(r.type, r.text)
        rows.append({"id": r.id, "type": r.type, "label": r.label, "group": r.group, "risk": out["risk"],
                     "band": out["band"], "explanation": out["explanation"],
                     "cues": " | ".join(c["evidence"] for c in out["cues"])})
    res = pd.DataFrame(rows)
    summary = {}
    for t, g in res.groupby("type"):
        ph, lg = g[g.label == 1], g[g.label == 0]
        summary[t] = {"n_phishing": len(ph), "n_legit": len(lg),
                      "recall_high": round(float((ph.band == "high").mean()), 3),
                      "recall_high_or_uncertain": round(float((ph.band != "low").mean()), 3),
                      "false_alarm_high": round(float((lg.band == "high").mean()), 3),
                      "legit_flagged_any": round(float((lg.band != "low").mean()), 3)}
    return res, summary


def explanation_checks(det: Detector) -> dict:
    """Automated parts of the explanation-quality framework (Section 4.3.2)."""
    df = pd.read_csv(EVIDENCE / "challenge_set.csv")
    supported = total = consistent = unsupported = 0
    for r in df.itertuples():
        a, b = det.analyze(r.type, r.text), det.analyze(r.type, r.text)
        consistent += int(a["risk"] == b["risk"] and a["cues"] == b["cues"])
        words = set(normalise(r.text).split())
        for c in a["cues"]:
            total += 1
            if c["source"] == "text":
                ev = c["evidence"]
                for shown, token in (("a link", "urltoken"), ("a phone number", "phonenum"),
                                     ("an e-mail address", "emailaddr")):
                    ev = ev.replace(shown, token)
                ok = all(w in words for w in ev.split())
            elif "fragment" in c:  # the quoted characters must really be in the link
                ok = c["fragment"] in url_text(a["riskiest_url"] or "")
            else:  # readable property: link value must be above the training average
                ok = c["z"] > 0
            supported += ok
            unsupported += (not ok)
    return {"n_inputs": len(df), "n_cues": total,
            "evidence_fidelity_automated": round(float(supported / max(total, 1)), 4),
            "unsupported_claims_per_100_warnings": round(100 * unsupported / max(total, 1), 2),
            "consistency_same_input_twice": round(consistent / len(df), 4),
            "note": "Automated check only: confirms each cue exists in the input / URL features. "
                    "Human rating of clarity, comprehension and Cohen's kappa was NOT performed."}


def run_edge_cases() -> pd.DataFrame:
    from fastapi.testclient import TestClient

    from .api import app
    client = TestClient(app)
    df = pd.read_csv(EVIDENCE / "edge_cases.csv", keep_default_na=False)
    rows = []
    for r in df.itertuples():
        text = ("Hi, meeting notes attached. " + "lorem ipsum " * 5000) if r.text == "GENERATED_LONG_EMAIL" else r.text
        resp = client.post("/analyze", json={"type": r.type, "text": text, "consent": True})
        body = resp.json()
        band = body.get("band", "")
        notes = " ".join(body.get("notes", []))
        exp = r.expected
        if exp.startswith("error"):
            passed = resp.status_code == 422
        elif exp.startswith("high or uncertain") or exp.startswith("uncertain or high"):
            passed = band in ("high", "uncertain")
        elif exp.startswith("low or uncertain"):
            passed = band in ("low", "uncertain")
        elif exp.startswith("low"):
            passed = band == "low" and bool(notes)
        elif "note" in exp:
            passed = resp.status_code == 200 and bool(notes)
        else:
            passed = resp.status_code == 200
        rows.append({"id": r.id, "type": r.type, "why": r.why, "expected": exp, "http_status": resp.status_code,
                     "risk": body.get("risk", ""), "band": band, "notes_or_error": notes or body.get("detail", ""),
                     "pass": "PASS" if passed else "FAIL"})
    # consent and logging checks
    r = client.post("/analyze", json={"type": "sms", "text": "hello", "consent": False})
    rows.append({"id": "E17", "type": "sms", "why": "No consent -> request refused (workflow step 1)",
                 "expected": "error 403", "http_status": r.status_code, "risk": "", "band": "",
                 "notes_or_error": r.json().get("detail", ""), "pass": "PASS" if r.status_code == 403 else "FAIL"})
    r = client.post("/analyze", json={"type": "pdf", "text": "hello", "consent": True})
    rows.append({"id": "E18", "type": "pdf", "why": "Unsupported input type", "expected": "error 422",
                 "http_status": r.status_code, "risk": "", "band": "", "notes_or_error": "validation error",
                 "pass": "PASS" if r.status_code == 422 else "FAIL"})
    return pd.DataFrame(rows)


def latency(det: Detector, samples: dict) -> dict:
    out = {}
    for fmt, texts in samples.items():
        det.analyze(fmt, texts[0])  # warm-up
        cls, tot = [], []
        for t in texts:
            r = det.analyze(fmt, t)
            cls.append(r["timing_ms"]["classify"])
            tot.append(r["timing_ms"]["total"])
        out[fmt] = {"n": len(texts), "classify_ms_median": round(float(np.median(cls)), 1),
                    "classify_ms_p95": round(float(np.percentile(cls, 95)), 1),
                    "total_ms_median": round(float(np.median(tot)), 1),
                    "total_ms_p95": round(float(np.percentile(tot, 95)), 1)}
    return out


# ---------------------------------------------------------------- criteria table
def criteria_rows(m: dict) -> list[dict]:
    rows = []

    def add(group, crit, fmt, target, value, ok):
        rows.append({"group": group, "criterion": crit, "format": fmt, "target": target,
                     "measured": value, "met": ok})

    for fmt, r in m["formats"].items():
        x = r["main"]
        add("core", "Catching phishing (recall, high band)", fmt, ">= 0.90", x["recall_high"], x["recall_high"] >= .90)
        add("core", "Suspicious safety net (recall, 40-100)", fmt, ">= 0.97", x["recall_high_or_uncertain"],
            x["recall_high_or_uncertain"] >= .97)
        add("core", "Avoiding false alarms (legit in high band)", fmt, "<= 2%",
            f"{x['false_positive_rate_high']:.2%}", x["false_positive_rate_high"] <= .02)
        add("core", "Overall balance (F1)", fmt, ">= 0.85",
            f"{x['f1']} (95% CI {r['bootstrap']['f1_main_95ci'][0]}-{r['bootstrap']['f1_main_95ci'][1]})", x["f1"] >= .85)
        add("core", "Reliable risk score (Brier)", fmt, "<= 0.10", x["brier"], x["brier"] <= .10)
        b = r["bootstrap"]
        add("core", f"Baseline vs comparator ({r['comparator_name']}) F1 diff", fmt, "report with 95% CI",
            f"{b['f1_main_minus_comparator']:+.4f} (95% CI {b['f1_diff_95ci'][0]:+.4f} to {b['f1_diff_95ci'][1]:+.4f})",
            "reported")
        lt = m["latency"][fmt]
        add("core", "Response time (classify / full result, median)", fmt, "<= 0.5 s / <= 3 s",
            f"{lt['classify_ms_median']} ms / {lt['total_ms_median']} ms",
            lt["classify_ms_median"] <= 500 and lt["total_ms_median"] <= 3000)
        add("extended", "Uncertain-band load (legit in 40-69)", fmt, "<= 10%",
            f"{x['uncertain_band_load_legit']:.2%}", x["uncertain_band_load_legit"] <= .10)
        if fmt in ("email", "url"):
            pr = r["low_prevalence"]
            add("extended", "Precision at 90% recall, 5% phishing", fmt, ">= 0.75",
                f"{pr['precision_at_90_recall_mean']} (95% CI {pr['precision_95ci'][0]}-{pr['precision_95ci'][1]})",
                pr["precision_at_90_recall_mean"] >= .75)
    ts = m["email_time_split"]
    add("extended", "Robustness to newer attacks (recall drop)", "email", "<= 5 points",
        f"{ts['recall_drop_points']} points ({ts['recall_high_old']} -> {ts['recall_high_new']})",
        ts["recall_drop_points"] <= 5)
    ex = m["explanations"]
    add("extended", "Explanation accuracy (automated evidence check)", "all", ">= 85%",
        f"{ex['evidence_fidelity_automated']:.0%} of {ex['n_cues']} cues", ex["evidence_fidelity_automated"] >= .85)
    add("core", "User understanding", "all", ">= 70% correct", "not measured (needs ethics approval)", "not attempted")
    add("extended", "Rater agreement (Cohen's kappa)", "all", ">= 0.60", "not measured", "not attempted")
    add("extended", "Protective effect (click-through)", "all", "<= 10%", "not measured", "not attempted")
    return rows


def main() -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    det = Detector()
    metrics: dict = {"formats": {}}
    probs, samples = {}, {}
    for fmt in ("email", "sms", "url"):
        art = joblib.load(ROOT / "models" / f"{fmt}.joblib")
        test, p_main, p_comp = test_probabilities(fmt, art)
        y = test["label"].values
        probs[fmt] = (y, p_main)
        samples[fmt] = test["raw"].sample(min(300, len(test)), random_state=SEED).tolist()
        entry = {"model": art["model_name"], "comparator_name": art["comparator_name"],
                 "model_version": art["version"], "main": detection_metrics(y, p_main),
                 "comparator": detection_metrics(y, p_comp), "bootstrap": bootstrap_f1(y, p_main, p_comp)}
        if fmt in ("email", "url"):
            entry["low_prevalence"] = precision_at_recall_low_prevalence(y, p_main)
        metrics["formats"][fmt] = entry
        print(f"[eval] {fmt}: F1={entry['main']['f1']} recall={entry['main']['recall_high']} "
              f"FPR={entry['main']['false_positive_rate_high']} brier={entry['main']['brier']}")

    metrics["email_time_split"] = email_time_split()
    metrics["latency"] = latency(det, samples)
    challenge, metrics["challenge_set"] = run_challenge(det)
    metrics["explanations"] = explanation_checks(det)
    edge = run_edge_cases()
    metrics["edge_cases"] = {"passed": int((edge["pass"] == "PASS").sum()), "total": len(edge)}
    metrics["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    fig_confusion(metrics["formats"])
    fig_reliability(probs)
    fig_risk_hist(probs)
    (RESULTS / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str))
    pd.DataFrame(criteria_rows(metrics)).to_csv(RESULTS / "criteria_table.csv", index=False)
    challenge.to_csv(RESULTS / "challenge_results.csv", index=False)
    edge.to_csv(EVIDENCE / "edge_case_results.csv", index=False)
    print("[eval] time split:", metrics["email_time_split"])
    print("[eval] challenge:", metrics["challenge_set"])
    print("[eval] explanations:", metrics["explanations"])
    print("[eval] edge cases:", metrics["edge_cases"])
    print("[eval] latency:", metrics["latency"])


if __name__ == "__main__":
    main()
