"""
ASAI X Bot Package

X APIからツイートを取得してDiscordに転送するボット
"""

from .config import validate_env_vars
from .discord_client import discord_post, get_tweet_url
from .main import fetch_and_forward, main
from .utils import build_index, load_since_id, save_since_id
from .x_api_client import fetch_tweets

__version__ = "2.0.0"
__all__ = [
    "main",
    "fetch_and_forward",
    "validate_env_vars",
    "load_since_id",
    "save_since_id",
    "build_index",
    "fetch_tweets",
    "discord_post",
    "get_tweet_url",
]
