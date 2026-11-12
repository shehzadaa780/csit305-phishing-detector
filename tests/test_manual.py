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


# ---- Written by: Shehzad Siddiqui ----
# Made-up phishing e-mail written by the author, imitating a "Claude Pro" account invitation.
# Expected: high. Author's reason: it looks too real, with colours and layout.
# Kept exactly as written, including the zero-width characters hidden in the postal address
# and the [.] in the e-mail addresses. The "Get Claude Pro" button text has no link behind it.
FAKE_CLAUDE_PRO_EMAIL = """This link has a 48 hour expiry - Contact Contoso Corp IT support if you need assistance or miss the access window. →

Claude
Welcome to Claude Pro
Your organization has set up a business account and provisioned you with Claude Pro access. The link is valid for 48 hours.

Activate your account using the link
Your Claude Pro access is ready to activate. Use the link below to sign in with your company account or continue with Google.

Get Claude Pro
Need help getting started?
Intro to Claude Cowork
Intro to Claude Cowork
Everything from your first task to file workflows, plugins, and more.

Start the course

 \t
Customize Cowork
Set up your workspace
Connect your tools, write your first skill, and bundle it for your team.

Read the guide

Was this email useful?
Thumbs up visual graphic\tThumbs down visual graphic
Claude
Download on the iOS App Store visual graphic\tGet it on Google Play visual graphic
Instagram\tLinkedIn\tX\tYoutube

Anthropic PBC, 54‌8 M‌a‌r‌k‌e‌t S‌t, PMB 9‌0‌3‌7‌5, Sa‌n F‌r‌a‌n‌c‌i‌s‌c‌o, C‌A 9‌4‌1‌0‌4

This email was sent to john[.]doe@mybusiness[.]com. To opt out of future emails, click unsubscribe.

Claude ( claude@cloud-notification-services[.]com )
to john[.]doe@mybusiness[.]com"""


def test_fake_claude_pro_invitation_email(det):
    result = det.analyze("email", FAKE_CLAUDE_PRO_EMAIL)
    assert result["band"] == "high"


# ---- Written by: [name] ----
