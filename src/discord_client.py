import html
import logging
from typing import cast

import requests

from config import WEBHOOK_URL

logger = logging.getLogger(__name__)


def discord_post(content=None, embed=None):
    payload = {}
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]

    try:
        logger.info("Discordに投稿中...")
        r = requests.post(cast(str, WEBHOOK_URL), json=payload, timeout=15)
        r.raise_for_status()
        logger.info("Discordへの投稿が完了しました")
    except Exception as e:
        logger.error(f"Discordへの投稿に失敗しました: {e}")
        raise


def to_embed(tweet, users_idx, media_idx):
    author = users_idx.get(tweet["author_id"], {})
    t_id = tweet["id"]
    username = author.get("username", "unknown")
    screen_url = f"https://x.com/{username}/status/{t_id}"

    # 画像があれば最初の1枚を埋め込み
    image_url = None
    if "attachments" in tweet and "media_keys" in tweet["attachments"]:
        for mk in tweet["attachments"]["media_keys"]:
            m = media_idx.get(mk)
            if m and m.get("type") == "photo":
                image_url = m.get("url") or m.get("preview_image_url")
                break

    # Embed
    title = f"@{username}"
    description = html.unescape(tweet.get("text", ""))[:4000]  # Discord制限対策
    author_name = author.get("name", username)
    author_icon = author.get("profile_image_url")

    embed = {
        "title": title,
        "url": screen_url,
        "description": description,
        "author": {
            "name": author_name,
            "url": f"https://x.com/{username}",
            "icon_url": author_icon,
        },
        "footer": {
            "text": f"likes: {tweet['public_metrics']['like_count']}  rt: {tweet['public_metrics']['retweet_count']}"  # noqa: E501
        },
    }
    if image_url:
        embed["image"] = {"url": image_url}
    return embed
