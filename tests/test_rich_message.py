from telegram.rich_message import extract_text, get_message_photos


class FakePhoto:
    def __init__(self, id):
        self.id = id


class FakeMessage:
    def __init__(self, photo=None, rich_message=None):
        self.photo = photo
        self.rich_message = rich_message


class FakeRichMessage:
    def __init__(self, blocks=None, photos=None):
        self.blocks = blocks or []
        self.photos = photos or []


class TextEmpty:
    pass


class TextPlain:
    def __init__(self, text):
        self.text = text


class TextConcat:
    def __init__(self, texts):
        self.texts = texts


class TextBold:
    def __init__(self, text):
        self.text = text


class TextUrl:
    def __init__(self, text, url):
        self.text = text
        self.url = url


class PageBlockParagraph:
    def __init__(self, text):
        self.text = text


class PageBlockCollage:
    def __init__(self, items):
        self.items = items


def test_get_message_photos_prefers_the_regular_photo():
    photo = FakePhoto(1)
    message = FakeMessage(photo=photo, rich_message=FakeRichMessage(photos=[FakePhoto(2)]))

    assert get_message_photos(message) == [photo]


def test_get_message_photos_falls_back_to_rich_message_collage():
    photos = [FakePhoto(1), FakePhoto(2), FakePhoto(3)]
    message = FakeMessage(photo=None, rich_message=FakeRichMessage(photos=photos))

    assert get_message_photos(message) == photos


def test_get_message_photos_empty_when_neither_present():
    message = FakeMessage(photo=None, rich_message=None)

    assert get_message_photos(message) == []


def test_extract_text_joins_paragraphs_with_newlines():
    rich_message = FakeRichMessage(blocks=[
        PageBlockParagraph(TextPlain("First paragraph")),
        PageBlockParagraph(TextPlain("Second paragraph")),
    ])

    assert extract_text(rich_message) == "First paragraph\nSecond paragraph"


def test_extract_text_flattens_concat_and_formatting_wrappers():
    rich_message = FakeRichMessage(blocks=[
        PageBlockParagraph(TextConcat([
            TextPlain("Hello "),
            TextBold(TextPlain("bold")),
            TextPlain(" and "),
            TextUrl(TextPlain("a link"), url="https://example.com"),
        ])),
    ])

    assert extract_text(rich_message) == "Hello bold and a link"


def test_extract_text_treats_empty_text_as_blank():
    rich_message = FakeRichMessage(blocks=[PageBlockParagraph(TextEmpty())])

    assert extract_text(rich_message) == ""


def test_extract_text_skips_non_paragraph_blocks():
    rich_message = FakeRichMessage(blocks=[
        PageBlockParagraph(TextPlain("Caption text")),
        PageBlockCollage(items=["photo-block-1", "photo-block-2"]),
    ])

    assert extract_text(rich_message) == "Caption text"
