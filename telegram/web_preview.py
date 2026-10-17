import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("uvicorn.info")

REQUEST_TIMEOUT_SECONDS = 10


def _fetch_soup(url):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Web preview fallback request failed for {url}: {e}")
        return None

    return BeautifulSoup(response.text, "html.parser")


def _fetch_preview_soup(channel_name, message_id):
    channel = channel_name.lstrip("@")
    return _fetch_soup(f"https://t.me/{channel}/{message_id}")


def _og_content(soup, property_name):
    tag = soup.find("meta", attrs={"property": property_name})
    if tag is None or not tag.get("content"):
        return None
    return tag["content"]


# Best-effort fallback for posts where Telethon returns empty text despite
# real content existing - observed on a post using a newer Telegram message
# format (multiple photos attached to a single message, rather than the
# classic multi-message grouped_id album) that neither Telethon nor even
# Telegram's own web client can render (t.me/s/<channel>/<id> shows "Please
# open Telegram to view this post" for it). Telegram still populates the
# og:description meta tag on the plain (non-/s/) preview page from the real
# underlying text, independent of that rendering gap - but it's truncated
# (observed ~900-1000 chars against this channel's normal 1500-3800), so this
# recovers partial text, not the original in full.
def fetch_post_text_from_web_preview(channel_name, message_id):
    soup = _fetch_preview_soup(channel_name, message_id)
    if soup is None:
        return None
    return _og_content(soup, "og:description")


# The channel's own avatar, as exposed via its web preview og:image. Needed
# to filter fetch_post_image_url_from_web_preview below: for a post whose
# media Telegram can't render at all, og:image silently falls back to this
# same channel-logo image rather than omitting the tag - confirmed by
# comparing https://t.me/<channel> against such a post, both returning the
# identical image URL. Without filtering it out, "recovered" images for
# those posts are actually just the channel logo, not post content.
def fetch_channel_logo_url(channel_name):
    channel = channel_name.lstrip("@")
    soup = _fetch_soup(f"https://t.me/{channel}")
    if soup is None:
        return None
    return _og_content(soup, "og:image")


# Same gap as fetch_post_text_from_web_preview above, but for the photo: when
# Telethon can't decode the message's media at all, og:image on the same
# preview page points at a directly downloadable image - except when it's
# actually just the channel logo (see fetch_channel_logo_url above), which
# channel_logo_url lets the caller filter out. For a multi-photo post this
# only recovers the first/representative photo, not every one attached - a
# different gap than the text truncation above, but the same "best-effort,
# not the original in full" situation.
def fetch_post_image_url_from_web_preview(channel_name, message_id, channel_logo_url=None):
    soup = _fetch_preview_soup(channel_name, message_id)
    if soup is None:
        return None

    image_url = _og_content(soup, "og:image")
    if image_url is None:
        return None
    if channel_logo_url is not None and image_url == channel_logo_url:
        return None
    return image_url


def download_post_image_from_web_preview(channel_name, message_id, dest_path, channel_logo_url=None):
    """Downloads the recovered og:image to dest_path. Returns True on success."""
    image_url = fetch_post_image_url_from_web_preview(channel_name, message_id, channel_logo_url)
    if image_url is None:
        return False

    try:
        response = requests.get(image_url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Web preview image download failed for {image_url}: {e}")
        return False

    with open(dest_path, "wb") as f:
        f.write(response.content)
    return True
