import requests

from telegram.web_preview import fetch_post_text_from_web_preview

OG_DESCRIPTION_HTML = """
<html><head>
<meta property="og:description" content="Real post text, truncated&hellip;">
</head></html>
"""


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")


def test_extracts_og_description_and_strips_leading_at(monkeypatch):
    captured_url = {}

    def fake_get(url, timeout):
        captured_url["url"] = url
        return FakeResponse(OG_DESCRIPTION_HTML)

    monkeypatch.setattr("telegram.web_preview.requests.get", fake_get)

    text = fetch_post_text_from_web_preview("@blackholelogs", 67)

    assert text == "Real post text, truncated…"
    assert captured_url["url"] == "https://t.me/blackholelogs/67"


def test_returns_none_when_meta_tag_missing(monkeypatch):
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse("<html><head></head></html>"),
    )

    assert fetch_post_text_from_web_preview("blackholelogs", 1) is None


def test_returns_none_on_request_failure(monkeypatch):
    def fake_get(url, timeout):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr("telegram.web_preview.requests.get", fake_get)

    assert fetch_post_text_from_web_preview("blackholelogs", 1) is None


def test_returns_none_on_http_error_status(monkeypatch):
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse("not found", status_code=404),
    )

    assert fetch_post_text_from_web_preview("blackholelogs", 1) is None
