"""Hand-written tests, kept separate so they can be compared with the AI-written tests.

Only add tests you thought of and wrote yourself. Put your name above your tests.
A failing test is useful evidence: keep it, log it in evidence/evidence_log.csv, and
retest after any fix. Run with:  python -m pytest tests/test_manual.py -v

Pattern to copy:

    def test_short_description():
        result = det.analyze("sms", "your own message here")
        assert result["band"] == "high"    # or "uncertain" / "low"

Add `det` as an argument to each test, as in: def test_short_description(det):
"""
import pytest

from phishdetect.pipeline import Detector


@pytest.fixture(scope="module")
def det():
    return Detector()


# ---- Written by: [name] ----


# ---- Written by: [name] ----
