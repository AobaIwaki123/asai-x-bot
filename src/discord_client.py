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
    except Exception:
        logger.exception("Discordへの投稿に失敗しました")
        raise


def get_tweet_url(tweet, users_idx):
    """ツイートのURLを生成する"""
    author = users_idx.get(tweet["author_id"], {})
    t_id = tweet["id"]
    username = author.get("username", "unknown")
    return f"https://x.com/{username}/status/{t_id}"
