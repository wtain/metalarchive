def get_message_photos(message):
    """All downloadable Photo objects for a message: the regular single
    photo, or every photo in its rich-message collage when there's no
    regular photo. Telegram's newer "rich message" post format (a
    Telegraph-style document of formatted text + a photo collage) replaces
    message.text/message.media with message.rich_message for clients recent
    enough to understand it (Telethon >=1.42, API layer >=220ish) - older
    clients instead see empty text and MessageMediaUnsupported, which is
    what originally hid these posts' images (and truncated their text - see
    extract_text below, and telegram/web_preview.py for the pre-upgrade
    workaround this made mostly unnecessary)."""
    if message.photo is not None:
        return [message.photo]
    if getattr(message, "rich_message", None) is not None:
        return list(message.rich_message.photos)
    return []


def extract_text(rich_message):
    """Flattens a RichMessage's paragraph blocks into plain text, one
    paragraph per line. Non-text blocks (currently just the photo collage)
    are skipped - photos are handled separately via get_message_photos."""
    paragraphs = []
    for block in rich_message.blocks:
        if type(block).__name__ == "PageBlockParagraph":
            paragraphs.append(_flatten_text(block.text))
    return "\n".join(paragraphs)


def _flatten_text(node):
    type_name = type(node).__name__
    if type_name == "TextEmpty":
        return ""
    if type_name == "TextPlain":
        return node.text
    if type_name == "TextConcat":
        return "".join(_flatten_text(part) for part in node.texts)
    if hasattr(node, "text"):
        # Formatting wrappers (bold/italic/underline/url/button/...) all
        # carry a single inner text node under .text - plain text has no
        # formatting to preserve, so just recurse into it.
        return _flatten_text(node.text)
    return ""
