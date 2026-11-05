"""Draws results/figures/architecture.png (Figure 1 of the report, as implemented in v0.2.0)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results" / "figures" / "architecture.png"
INK, MUTED = "#1d2433", "#5d6678"
BLUE_BG, BLUE_ED = "#e6eefc", "#2a78d6"
GREEN_BG, GREEN_ED = "#e8f5ec", "#1e8a4a"
GREY_BG, GREY_ED = "#f2f2f0", "#8a8a85"
PURP_BG, PURP_ED = "#efeafb", "#6250d6"

fig, ax = plt.subplots(figsize=(12, 6.2), dpi=200)
ax.set_xlim(0, 120)
ax.set_ylim(0, 62)
ax.axis("off")


def box(x, y, w, h, title, body="", bg=BLUE_BG, ed=BLUE_ED, dashed=False, fs=8.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=bg, ec=ed,
                                lw=1.3, ls="--" if dashed else "-"))
    ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=fs, fontweight="bold", color=INK)
    if body:
        ax.text(x + w / 2, y + h - 4.4, body, ha="center", va="top", fontsize=6.6, color=MUTED, linespacing=1.35)


def arrow(x1, y1, x2, y2, label="", dashed=False, color=INK, lx=0, ly=1.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, lw=1.1, color=color,
                                 ls="--" if dashed else "-"))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, ha="center", fontsize=6.4, color=MUTED)


ax.text(1, 60.5, "AI Phishing & Scam Detector - architecture as implemented (v0.2.0)", fontsize=11,
        fontweight="bold", color=INK, va="top")
ax.text(1, 57.6, "Runs locally. Links are parsed, never visited. No external services are called.",
        fontsize=7.5, color=MUTED, va="top")

# user and presentation
box(1, 38, 13, 12, "User", "pastes an e-mail,\nSMS or link\nticks consent", bg="#fdecea", ed="#d64545")
box(1, 20, 13, 13, "Web page  ( / )", "served by the API\ninput type + text\nconsent checkboxes\nresult card")
arrow(7.5, 38, 7.5, 33.6)

# application layer frame
ax.add_patch(FancyBboxPatch((18, 14), 100, 41, boxstyle="round,pad=0.3,rounding_size=1.5", fc="#fbfcfe",
                            ec=GREEN_ED, lw=1.2))
ax.text(20, 54, "Application layer - FastAPI service (src/phishdetect)", fontsize=8.2, fontweight="bold",
        color=GREEN_ED, va="top")
box(20, 20, 13, 30, "REST API", "POST /analyze\nGET /health\nGET /\n\n403 without consent\n422 bad input\n\nreturns JSON:\nlabel, risk, band,\ncues, explanation,\nadvice, notes,\nmodel_version", bg=GREEN_BG, ed=GREEN_ED)
arrow(14.6, 27, 19.6, 27, "request", ly=1.2)
arrow(19.6, 23, 14.6, 23, "result", ly=-2.4)

steps = [
    ("1 Intake & router", "type check\nconsent\nempty / non-URL\nrejected"),
    ("2 Privacy preprocess", "mask e-mails,\nphones; strip HTML;\nextract links\n(never opened)"),
    ("3 Features", "text: TF-IDF words\n+ word pairs\nURL: char 3-5 grams\n+ 21 lexical"),
    ("4 Classifier", "one per format\nlogistic regression\n(e-mail, SMS, URL)"),
]
x = 36
for i, (t, b) in enumerate(steps):
    box(x, 36, 18.5, 13, t, b)
    if i:
        arrow(x - 1.6, 42.5, x - 0.4, 42.5)
    x += 20.3
arrow(33.6, 42.5, 35.6, 42.5)
steps2 = [
    ("5 Calibrate & risk", "sigmoid calibration\nrisk = round(100 x P)\nmax(text, link)\n0-39 | 40-69 | 70-100"),
    ("6 Explanation", "exact contributions\n(value x coefficient)\nonly cues present\nin the input"),
    ("7 Response builder", "label, band,\nplain-language reason,\nsafe next step,\nnotes"),
]
x = 97
pos = []
for t, b in steps2:
    box(x, 19, 18.5, 13, t, b)
    pos.append(x)
    x -= 20.3
arrow(105.5, 35.6, 105.5, 32.6)
arrow(pos[0] - 0.4, 25.5, pos[1] + 18.9, 25.5)
arrow(pos[1] - 0.4, 25.5, pos[2] + 18.9, 25.5)
arrow(pos[2] - 0.4, 25.5, 33.6, 25.5)

# storage
box(1, 1, 22, 10, "Audit log (SQLite)", "format, model version, label,\nrisk, band, latency\nNO message text or URLs",
    bg=PURP_BG, ed=PURP_ED)
arrow(26.5, 19.6, 18, 11.6)
ax.text(24.5, 11.6, "only if allowed", fontsize=6.4, color=MUTED, ha="left")
box(96, 1, 22, 10, "Model registry", "models/*.joblib + registry.json\nvectorisers, models,\ncalibrators, thresholds, version",
    bg=PURP_BG, ed=PURP_ED)
ax.plot([117.2, 117.2], [11.6, 42.5], ls="--", lw=1.1, color=PURP_ED)
arrow(117.2, 42.5, 115.8, 42.5, dashed=True, color=PURP_ED)
ax.text(116.4, 12.0, "models loaded at start-up", fontsize=6.4, color=PURP_ED, ha="right", va="bottom")

# offline pipeline
box(27, 1, 66, 10, "Offline training & evaluation  (train.py, evaluate.py)",
    "datasets -> clean, de-duplicate, 70/15/15 split (URLs grouped by website) -> train -> choose C on validation\n"
    "-> calibrate on validation -> export versioned models -> score once on held-out test + challenge set + edge cases",
    bg=GREY_BG, ed=GREY_ED)
arrow(93.6, 6, 95.6, 6)

fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
