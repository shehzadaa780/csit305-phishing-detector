"""Unit tests for privacy preprocessing and URL features (no models needed)."""
from phishdetect.preprocess import extract_urls, normalise, preprocess
from phishdetect.url_features import extract, normalise_url


def test_email_addresses_and_phones_are_masked():
    out = normalise("Mail john.doe@uni.edu or call +971 50 123 4567 now")
    assert "john" not in out and "doe" not in out
    assert "emailaddr" in out and "phonenum" in out


def test_email_address_is_not_a_link():
    assert extract_urls("write to support@bank.com") == []


def test_explicit_and_bare_links_are_extracted():
    urls = extract_urls("Pay at delivery-update.example.test/pay or http://a.com/x.")
    assert "http://a.com/x" in urls
    assert "delivery-update.example.test/pay" in urls


def test_at_symbol_url_is_kept_whole():
    assert extract_urls("see http://www.paypal.com@evil.xyz/a") == ["http://www.paypal.com@evil.xyz/a"]


def test_file_names_are_not_links():
    assert extract_urls("see attached report.pdf and data.xlsx") == []


def test_html_href_links_are_found():
    out = preprocess('<a href="http://bad.tk/login">Click</a>')
    assert out["urls"] == ["http://bad.tk/login"]
    assert out["clean_text"] == "click"


def test_scheme_and_www_removed_before_features():
    assert normalise_url("HTTPS://www.example.com/a") == "example.com/a"
    assert extract("http://example.com") == extract("https://www.example.com")


def test_suspicious_url_features():
    f = extract("http://192.168.0.1:8080/login")
    assert f["has_ip_host"] == 1 and f["has_port"] == 1 and f["suspicious_words"] >= 1
    assert extract("https://bit.ly/abc")["is_shortener"] == 1
    assert extract("http://paypal-secure.com/x")["brand_outside_domain"] == 1
    assert extract("https://paypal.com/x")["brand_outside_domain"] == 0
