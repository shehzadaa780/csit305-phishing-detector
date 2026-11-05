"""Score the expert explanation rubric (report Section 4.3.2).

Two raters fill in evidence/rubric/rater_A.csv and rater_B.csv separately, then run:
    python scripts/score_rubric.py
Prints each rater's mean score, percentage agreement and Cohen's kappa (target >= 0.60).
"""
import csv
from collections import Counter
from pathlib import Path

RUBRIC = Path(__file__).resolve().parents[1] / "evidence" / "rubric"


def load(name: str) -> dict:
    with open(RUBRIC / name, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    scores = {}
    for r in rows:
        value = r["score_0_1_2"].strip()
        if value not in {"0", "1", "2"}:
            raise SystemExit(f"{name}: item {r['item']} needs a score of 0, 1 or 2 (found '{value}')")
        scores[r["item"]] = int(value)
    return scores


def cohen_kappa(a: list, b: list) -> float:
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    count_a, count_b = Counter(a), Counter(b)
    expected = sum(count_a[k] * count_b[k] for k in {0, 1, 2}) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def main() -> None:
    rater_a, rater_b = load("rater_A.csv"), load("rater_B.csv")
    if rater_a.keys() != rater_b.keys():
        raise SystemExit("The two rater files do not contain the same items.")
    items = sorted(rater_a)
    a = [rater_a[i] for i in items]
    b = [rater_b[i] for i in items]
    agreement = sum(x == y for x, y in zip(a, b)) / len(items)
    print(f"Items rated:        {len(items)}")
    print(f"Mean score, rater A: {sum(a) / len(a):.2f} / 2")
    print(f"Mean score, rater B: {sum(b) / len(b):.2f} / 2")
    print(f"Exact agreement:     {agreement:.0%}")
    print(f"Cohen's kappa:       {cohen_kappa(a, b):.2f} (target >= 0.60)")


if __name__ == "__main__":
    main()
