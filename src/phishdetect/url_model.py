"""v0.2.0 URL model input: character n-grams of the URL string (TF-IDF, 3-5
characters) joined with the standardised lexical features from url_features.
A single logistic regression is trained on both, so every prediction can be
traced back exactly to (a) readable link properties and (b) text fragments."""
from __future__ import annotations

from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

from .url_features import extract_matrix, normalise_url


def url_text(u: str) -> str:
    return normalise_url(u).lower().rstrip("/")


def make_char_vectoriser() -> TfidfVectorizer:
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True,
                           max_features=200_000)


def fit_transformers(urls: list[str]) -> tuple[TfidfVectorizer, StandardScaler]:
    vec = make_char_vectoriser().fit([url_text(u) for u in urls])
    scaler = StandardScaler().fit(extract_matrix(urls))
    return vec, scaler


def url_matrix(vec: TfidfVectorizer, scaler: StandardScaler, urls: list[str]):
    chars = vec.transform([url_text(u) for u in urls])
    lex = csr_matrix(scaler.transform(extract_matrix(urls)))
    return hstack([chars, lex]).tocsr()
