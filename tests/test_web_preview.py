import requests

from telegram.web_preview import (
    download_post_image_from_web_preview,
    fetch_channel_logo_url,
    fetch_post_image_url_from_web_preview,
    fetch_post_text_from_web_preview,
)

OG_DESCRIPTION_HTML = """
<html><head>
<meta property="og:description" content="Real post text, truncated&hellip;">
</head></html>
"""

OG_IMAGE_HTML = """
<html><head>
<meta property="og:image" content="https://cdn4.telesco.pe/file/abc123.jpg">
</head></html>
"""


class FakeResponse:
    def __init__(self, text=None, content=None, status_code=200):
        self.text = text
        self.content = content
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


def test_extracts_og_image_url(monkeypatch):
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse(text=OG_IMAGE_HTML),
    )

    url = fetch_post_image_url_from_web_preview("blackholelogs", 67)

    assert url == "https://cdn4.telesco.pe/file/abc123.jpg"


def test_fetch_post_image_url_returns_none_when_meta_tag_missing(monkeypatch):
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse(text="<html><head></head></html>"),
    )

    assert fetch_post_image_url_from_web_preview("blackholelogs", 1) is None


def test_download_post_image_writes_bytes_to_dest_path(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        if url == "https://t.me/blackholelogs/67":
            return FakeResponse(text=OG_IMAGE_HTML)
        assert url == "https://cdn4.telesco.pe/file/abc123.jpg"
        return FakeResponse(content=b"fake-jpeg-bytes")

    monkeypatch.setattr("telegram.web_preview.requests.get", fake_get)
    dest_path = tmp_path / "67_0.jpg"

    result = download_post_image_from_web_preview("blackholelogs", 67, str(dest_path))

    assert result is True
    assert dest_path.read_bytes() == b"fake-jpeg-bytes"


def test_download_post_image_returns_false_when_no_og_image(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse(text="<html><head></head></html>"),
    )

    result = download_post_image_from_web_preview("blackholelogs", 1, str(tmp_path / "1_0.jpg"))

    assert result is False
    assert not (tmp_path / "1_0.jpg").exists()


def test_fetch_channel_logo_url_hits_the_bare_channel_page(monkeypatch):
    captured_url = {}

    def fake_get(url, timeout):
        captured_url["url"] = url
        return FakeResponse(text=OG_IMAGE_HTML)

    monkeypatch.setattr("telegram.web_preview.requests.get", fake_get)

    url = fetch_channel_logo_url("@blackholelogs")

    assert url == "https://cdn4.telesco.pe/file/abc123.jpg"
    assert captured_url["url"] == "https://t.me/blackholelogs"


def test_fetch_post_image_url_filters_out_the_channel_logo(monkeypatch):
    # Telegram falls back to the channel's own avatar for og:image when it
    # can't render the post's actual media - this must not look like a
    # recovered post image.
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse(text=OG_IMAGE_HTML),
    )

    url = fetch_post_image_url_from_web_preview(
        "blackholelogs", 67, channel_logo_url="https://cdn4.telesco.pe/file/abc123.jpg"
    )

    assert url is None


def test_fetch_post_image_url_keeps_a_distinct_image(monkeypatch):
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse(text=OG_IMAGE_HTML),
    )

    url = fetch_post_image_url_from_web_preview(
        "blackholelogs", 66, channel_logo_url="https://cdn4.telesco.pe/file/different-logo.jpg"
    )

    assert url == "https://cdn4.telesco.pe/file/abc123.jpg"


def test_download_post_image_skips_the_channel_logo(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "telegram.web_preview.requests.get",
        lambda url, timeout: FakeResponse(text=OG_IMAGE_HTML),
    )
    dest_path = tmp_path / "67_0.jpg"

    result = download_post_image_from_web_preview(
        "blackholelogs", 67, str(dest_path), channel_logo_url="https://cdn4.telesco.pe/file/abc123.jpg"
    )

    assert result is False
    assert not dest_path.exists()
