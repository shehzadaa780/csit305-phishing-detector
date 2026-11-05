"""Dataset loading, cleaning, de-duplication and 70/15/15 splits (Stages 1-4).

Label definitions (Stage 1):
  email : 1 = phishing (Nazario corpus), 0 = legitimate (Enron ham only;
          Enron 'spam' rows are dropped because spam is not phishing)
  sms   : 1 = spam (UCI SMS Spam Collection), 0 = ham.
          NOTE: spam is NOT the same as smishing - see README limitations.
  url   : 1 = phishing, 0 = legitimate (Sahingoz et al. dataset [2])
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from .preprocess import normalise, truncate
from .url_features import normalise_url, registered_domain, split_url

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SEED = 42


def _hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8", "ignore")).hexdigest()


def _dedupe(df: pd.DataFrame, key: str) -> tuple[pd.DataFrame, dict]:
    """Remove exact duplicates and near-duplicates (same first 300 normalised
    characters), and drop any item that appears with BOTH labels."""
    n0 = len(df)
    df = df[df[key].str.len() > 0]
    n_empty = n0 - len(df)
    df = df.assign(_h=df[key].map(_hash), _nh=df[key].str[:300].map(_hash))
    n_nonempty = len(df)
    conflict = df.groupby("_h")["label"].nunique()
    conflict_ids = set(conflict[conflict > 1].index)
    df = df[~df["_h"].isin(conflict_ids)]
    n1 = len(df)
    df = df.drop_duplicates("_h").drop_duplicates("_nh")
    stats = {"raw": n0, "empty_removed": n_empty, "conflicting_labels_removed": n_nonempty - n1,
             "duplicates_removed": n1 - len(df), "final": len(df)}
    return df.drop(columns=["_h", "_nh"]).reset_index(drop=True), stats


def load_email() -> tuple[pd.DataFrame, dict]:
    naz = pd.read_csv(RAW / "email" / "Nazario.csv")
    # drop mailbox-system placeholder messages that are not real e-mails
    naz = naz[~naz["subject"].fillna("").str.contains("FOLDER INTERNAL DATA", case=False)]
    naz = naz.assign(raw=(naz["subject"].fillna("") + " \n " + naz["body"].fillna("")).map(truncate),
                     label=1, date=pd.to_datetime(naz["date"], errors="coerce", utc=True, format="mixed"))
    enr = pd.read_csv(RAW / "email" / "Enron.csv")
    enr = enr[enr["label"] == 0]
    enr = enr.assign(raw=(enr["subject"].fillna("") + " \n " + enr["body"].fillna("")).map(truncate),
                     label=0, date=pd.NaT)
    df = pd.concat([naz[["raw", "label", "date"]], enr[["raw", "label", "date"]]], ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df["text"] = df["raw"].map(normalise)
    return _dedupe(df, "text")


def load_sms() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(RAW / "sms" / "SMSSpamCollection.tsv", sep="\t", header=None,
                     names=["tag", "raw"], quoting=3)
    df = df.assign(label=(df["tag"] == "spam").astype(int))
    df["text"] = df["raw"].map(normalise)
    return _dedupe(df[["raw", "text", "label"]], "text")


def load_url() -> tuple[pd.DataFrame, dict]:
    phish = json.loads((RAW / "url" / "data_phishing_37175.json").read_text())
    legit = json.loads((RAW / "url" / "data_legitimate_36400.json").read_text())
    df = pd.DataFrame({"raw": phish + legit, "label": [1] * len(phish) + [0] * len(legit)})
    df["text"] = df["raw"].map(lambda u: normalise_url(u).lower().rstrip("/"))
    df, stats = _dedupe(df, "text")
    # group = registered domain, so the same website never appears in both train and test
    df["group"] = df["raw"].map(lambda u: registered_domain(split_url(u)[0]))
    return df, stats


def split(df: pd.DataFrame, seed: int = SEED) -> dict[str, pd.DataFrame]:
    """70 / 15 / 15 train / validation / test split.

    Text formats: stratified by label. URLs: grouped by registered domain
    (added in v0.2.0) - in v0.1.0 66% of test URLs shared a website with a
    training URL, which inflated nothing useful and hid over-fitting to sites."""
    if "group" in df.columns:
        gss = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
        i, j = next(gss.split(df, groups=df["group"]))
        train, rest = df.iloc[i], df.iloc[j]
        gss = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=seed)
        i, j = next(gss.split(rest, groups=rest["group"]))
        val, test = rest.iloc[i], rest.iloc[j]
    else:
        train, rest = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=seed)
        val, test = train_test_split(rest, test_size=0.50, stratify=rest["label"], random_state=seed)
    return {"train": train.reset_index(drop=True), "val": val.reset_index(drop=True),
            "test": test.reset_index(drop=True)}


LOADERS = {"email": load_email, "sms": load_sms, "url": load_url}


def describe(df: pd.DataFrame) -> dict:
    return {"n": int(len(df)), "positives": int(df["label"].sum()),
            "negatives": int((df["label"] == 0).sum()),
            "positive_rate": round(float(df["label"].mean()), 4)}


if __name__ == "__main__":
    for name, loader in LOADERS.items():
        df, stats = loader()
        print(name, stats, describe(df))
        for part, d in split(df).items():
            print("   ", part, describe(d))
