import asyncio

from synchronizer.poller import download_photo_with_web_fallback


class FakeMessage:
    def __init__(self, id, media="something"):
        self.id = id
        self.media = media


class FakeTelegramClient:
    def __init__(self, download_result):
        self.download_result = download_result
        self.download_calls = []

    async def download_photo(self, message, dest_dir, file_name):
        self.download_calls.append((message.id, file_name))
        return self.download_result


def run(coro):
    return asyncio.run(coro)


def test_uses_telethon_result_without_falling_back(monkeypatch):
    called = False

    def fake_fallback(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr("synchronizer.poller.download_post_image_from_web_preview", fake_fallback)
    client = FakeTelegramClient(download_result="1_0.jpg")

    result = run(download_photo_with_web_fallback(client, FakeMessage(1), "channel", 1, "1_0.jpg"))

    assert result == "1_0.jpg"
    assert called is False


def test_falls_back_to_web_preview_when_telethon_cannot_decode_media(monkeypatch, tmp_path):
    captured = {}

    def fake_fallback(channel_name, message_id, dest_path, channel_logo_url=None):
        captured["args"] = (channel_name, message_id, dest_path, channel_logo_url)
        return True

    monkeypatch.setattr("synchronizer.poller.download_post_image_from_web_preview", fake_fallback)
    client = FakeTelegramClient(download_result=None)

    result = run(download_photo_with_web_fallback(
        client, FakeMessage(67, media="unsupported"), "mychannel", 67, "67_0.jpg", "https://logo.jpg"
    ))

    assert result == "67_0.jpg"
    assert captured["args"][0] == "mychannel"
    assert captured["args"][1] == 67
    assert captured["args"][3] == "https://logo.jpg"


def test_skips_fallback_when_message_has_no_media(monkeypatch):
    called = False

    def fake_fallback(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr("synchronizer.poller.download_post_image_from_web_preview", fake_fallback)
    client = FakeTelegramClient(download_result=None)

    result = run(download_photo_with_web_fallback(client, FakeMessage(1, media=None), "channel", 1, "1_0.jpg"))

    assert result is None
    assert called is False


def test_returns_none_when_fallback_also_fails(monkeypatch):
    monkeypatch.setattr("synchronizer.poller.download_post_image_from_web_preview", lambda *a, **k: False)
    client = FakeTelegramClient(download_result=None)

    result = run(download_photo_with_web_fallback(client, FakeMessage(1), "channel", 1, "1_0.jpg"))

    assert result is None
