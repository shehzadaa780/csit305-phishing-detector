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


# Each case and expected band below was chosen by the named group member before the test was run.
# Claude (AI) typed the cases into this file and ran them; it did not choose the cases or bands.


# ---- Written by: Abdullah Al Faqih ----
# Real SMS received by the author. Expected: uncertain.
# Case description (drafted by Claude at the group's request, not the author's own words):
# reads like a genuine bank card-delivery text and has no link, but asks the reader to call an
# unfamiliar landline about a shipment, which is also how delivery scams start.
def test_adib_card_delivery_call_request(det):
    result = det.analyze(
        "sms",
        "Hello, please call us on 045031998 to arrange the delivery of your Abu Dhabi Islamic Bank "
        "(Minor Debit Consignee Deli shipment 51423306815. Thanks",
    )
    assert result["band"] == "uncertain"


# ---- Written by: Imad Rahman ----
# Real phishing e-mail received by the author. Expected: high.
# Author's reason: people would likely believe it.
# The sender's address (probably a hacked real account) was replaced with sender@example.com;
# the detector masks every e-mail address the same way, so this does not change the score.
def test_fake_salik_toll_fine_email(det):
    result = det.analyze(
        "email",
        "sender@example.com\n\n"
        "[Salik] ADMIN NOTICE: As of 2026-04-15 12:47, a toll balance of AED 4.00 remains OUTSTANDING "
        "for settlement under your account. Ref: AE-SAL-001847. Settle before 11:59 PM TODAY to avoid "
        "an AED 50.00 fine and RESTRICTIONS on vehicle registration renewal in RTA system.\n\n"
        "To settle, visit:\n"
        "https://salik.ae.tiicyv.top/ae\n\n"
        "[RTA-SALIK Official]\n"
        "Call 80072545",
    )
    assert result["band"] == "high"


# ---- Written by: [name] ----
