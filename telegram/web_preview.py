import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("uvicorn.info")

REQUEST_TIMEOUT_SECONDS = 10


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
    channel = channel_name.lstrip("@")
    url = f"https://t.me/{channel}/{message_id}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Web preview fallback request failed for {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    tag = soup.find("meta", attrs={"property": "og:description"})
    if tag is None or not tag.get("content"):
        return None
    return tag["content"]
