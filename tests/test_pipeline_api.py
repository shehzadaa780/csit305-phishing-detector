"""Integration tests: trained models, pipeline and REST API.
Requires `python -m phishdetect.train` to have been run first."""
import pytest
from fastapi.testclient import TestClient

from phishdetect.api import app
from phishdetect.pipeline import Detector, InputError, band_for
from phishdetect.preprocess import normalise


@pytest.fixture(scope="module")
def det():
    return Detector()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_band_thresholds():
    t = {"uncertain": 40, "high": 70}
    assert band_for(39, t) == "low" and band_for(40, t) == "uncertain"
    assert band_for(69, t) == "uncertain" and band_for(70, t) == "high"


def test_obvious_phishing_sms_is_high(det):
    r = det.analyze("sms", "URGENT! Your account is suspended. Verify now at secure-bank-verify.com/login")
    assert r["band"] == "high" and r["risk"] >= 70 and r["cues"]


def test_ordinary_sms_is_low(det):
    assert det.analyze("sms", "See you at the library at 3, bring the notes")["band"] == "low"


def test_text_and_link_scores_take_the_maximum(det):
    r = det.analyze("sms", "hi, here is the link http://paypal-login-verify.com/webscr")
    assert r["risk"] == round(100 * max(r["text_probability"], r["url_probability"]))


def test_explanations_only_cite_words_in_the_input(det):
    text = "Congratulations you won a free prize, claim it now by calling 0800 123 4567"
    words = set(normalise(text).split()) | {"a", "link", "phone", "number"}
    for c in det.analyze("sms", text)["cues"]:
        if c["source"] == "text":
            assert set(c["evidence"].split()) <= words


def test_same_input_gives_same_output(det):
    a = det.analyze("email", "Your mailbox is full, validate your account here http://mail-upgrade.com")
    b = det.analyze("email", "Your mailbox is full, validate your account here http://mail-upgrade.com")
    assert a["risk"] == b["risk"] and a["cues"] == b["cues"]


@pytest.mark.parametrize("kind,text", [("sms", ""), ("sms", "   "), ("url", "http://"), ("url", "not a link"),
                                       ("pdf", "hello")])
def test_bad_inputs_raise(det, kind, text):
    with pytest.raises(InputError):
        det.analyze(kind, text)


def test_api_requires_consent(client):
    r = client.post("/analyze", json={"type": "sms", "text": "hello", "consent": False})
    assert r.status_code == 403


def test_api_returns_contract(client):
    r = client.post("/analyze", json={"type": "sms", "text": "Your parcel is held. Pay at delivery-update-example.test",
                                      "consent": True})
    assert r.status_code == 200
    body = r.json()
    for key in ("label", "risk", "band", "cues", "explanation", "advice", "model_version", "timing_ms"):
        assert key in body


def test_audit_log_stores_no_message_text(client, tmp_path):
    from phishdetect import api
    from phishdetect.audit import AuditLog
    api.audit = AuditLog(tmp_path / "audit.sqlite")
    secret = "my secret password is hunter2 http://x-login.com"
    client.post("/analyze", json={"type": "sms", "text": secret, "consent": True, "allow_logging": True})
    client.post("/analyze", json={"type": "sms", "text": "no log please", "consent": True})
    rows = api.audit.rows()
    assert len(rows) == 1
    assert "hunter2" not in str(rows) and "x-login" not in str(rows)


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"
