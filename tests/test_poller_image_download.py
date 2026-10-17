import asyncio

from synchronizer.poller import collect_post_photos, download_post_images


class FakePhoto:
    def __init__(self, id):
        self.id = id


class FakeMessage:
    def __init__(self, id, photo=None, rich_message=None, media="something"):
        self.id = id
        self.photo = photo
        self.rich_message = rich_message
        self.media = media


class FakeRichMessage:
    def __init__(self, photos):
        self.photos = photos


class FakeTelegramClient:
    def __init__(self, results_by_photo_id=None):
        # results_by_photo_id: {photo.id: file_name_or_None}; defaults to
        # "always succeeds, named after the photo id" when not given.
        self.results_by_photo_id = results_by_photo_id or {}
        self.download_calls = []

    async def download_photo(self, photo, dest_dir, file_name):
        self.download_calls.append((photo.id, file_name))
        if photo.id in self.results_by_photo_id:
            return self.results_by_photo_id[photo.id]
        return file_name


def run(coro):
    return asyncio.run(coro)


def test_collect_post_photos_uses_regular_photo_per_message():
    group = [FakeMessage(1, photo=FakePhoto("a")), FakeMessage(2, photo=FakePhoto("b"))]

    photos = collect_post_photos(group)

    assert [p.id for p in photos] == ["a", "b"]


def test_collect_post_photos_uses_rich_message_collage_when_no_regular_photo():
    group = [FakeMessage(67, photo=None, rich_message=FakeRichMessage(
        [FakePhoto("x"), FakePhoto("y"), FakePhoto("z")]
    ))]

    photos = collect_post_photos(group)

    assert [p.id for p in photos] == ["x", "y", "z"]


def test_download_post_images_names_files_sequentially_per_logical_post():
    group = [FakeMessage(67, photo=None, rich_message=FakeRichMessage(
        [FakePhoto("x"), FakePhoto("y")]
    ))]
    client = FakeTelegramClient()

    result = run(download_post_images(client, group, "channel", canonical_message_id=67))

    assert result == ["67_0.jpg", "67_1.jpg"]
    assert client.download_calls == [("x", "67_0.jpg"), ("y", "67_1.jpg")]


def test_download_post_images_skips_failed_downloads_without_gap_in_remaining_names(monkeypatch):
    group = [FakeMessage(67, photo=None, rich_message=FakeRichMessage(
        [FakePhoto("x"), FakePhoto("y")]
    ))]
    client = FakeTelegramClient(results_by_photo_id={"x": None})

    result = run(download_post_images(client, group, "channel", canonical_message_id=67))

    # "x" failed and contributed nothing; "y" is still named _0 since
    # file names are assigned by how many images have been saved so far.
    assert result == ["67_0.jpg"]
    assert client.download_calls == [("x", "67_0.jpg"), ("y", "67_0.jpg")]


def test_download_post_images_falls_back_to_web_preview_when_nothing_downloaded(monkeypatch):
    captured = {}

    def fake_fallback(channel_name, message_id, dest_path, channel_logo_url=None):
        captured["args"] = (channel_name, message_id, dest_path, channel_logo_url)
        return True

    monkeypatch.setattr("synchronizer.poller.download_post_image_from_web_preview", fake_fallback)
    group = [FakeMessage(67, photo=None, rich_message=None, media="unsupported")]
    client = FakeTelegramClient()

    result = run(download_post_images(client, group, "mychannel", canonical_message_id=67, channel_logo_url="logo"))

    assert result == ["67_0.jpg"]
    assert captured["args"][0] == "mychannel"
    assert captured["args"][1] == 67
    assert captured["args"][3] == "logo"


def test_download_post_images_skips_fallback_when_no_message_has_media(monkeypatch):
    called = False

    def fake_fallback(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr("synchronizer.poller.download_post_image_from_web_preview", fake_fallback)
    group = [FakeMessage(1, photo=None, rich_message=None, media=None)]
    client = FakeTelegramClient()

    result = run(download_post_images(client, group, "channel", canonical_message_id=1))

    assert result == []
    assert called is False


def test_download_post_images_skips_fallback_when_something_was_already_downloaded(monkeypatch):
    called = False

    def fake_fallback(*args, **kwargs):
        nonlocal called
        called = True
        return True

    monkeypatch.setattr("synchronizer.poller.download_post_image_from_web_preview", fake_fallback)
    group = [FakeMessage(1, photo=FakePhoto("a"))]
    client = FakeTelegramClient()

    result = run(download_post_images(client, group, "channel", canonical_message_id=1))

    assert result == ["1_0.jpg"]
    assert called is False
