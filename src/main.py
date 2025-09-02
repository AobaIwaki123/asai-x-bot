import logging

from config import validate_env_vars
from discord_client import discord_post, to_embed
from utils import build_index, load_since_id, save_since_id
from x_api_client import fetch_tweets

logger = logging.getLogger(__name__)


def fetch_and_forward():
    """ツイートの取得と転送を実行する"""
    logger.info("ツイートの取得と転送を開始")

    since_id = load_since_id()

    # X APIからツイートを取得
    payload = fetch_tweets(since_id)
    if payload is None:
        return

    tweets = payload.get("data", [])
    includes = payload.get("includes", {})
    users_idx = build_index(includes.get("users", []))
    media_idx = build_index(includes.get("media", []), key="media_key")

    if not tweets:
        logger.info("新しいツイートはありません")
        return

    logger.info(f"取得したツイート数: {len(tweets)}")
    logger.info(f"取得したユーザー数: {len(includes.get('users', []))}")
    logger.info(f"取得したメディア数: {len(includes.get('media', []))}")

    # 古い順に送る（Discordの読みやすさ配慮）
    tweets_sorted = sorted(tweets, key=lambda t: t["id"])
    logger.info("ツイートをDiscordに転送中...")

    for i, tw in enumerate(tweets_sorted, 1):
        username = users_idx.get(tw["author_id"], {}).get("username", "unknown")
        logger.info(f"ツイート {i}/{len(tweets_sorted)} を処理中: @{username}")
        embed = to_embed(tw, users_idx, media_idx)
        discord_post(embed=embed)

    # 次回用に最大IDを保存
    max_id = max(t["id"] for t in tweets_sorted)
    save_since_id(max_id)
    logger.info(f"処理完了。{len(tweets)}件のツイートを転送しました")


def main():
    """メイン関数"""
    # 単発実行（cronやサーバーレスで1分〜5分おき推奨）
    logger.info("=== ASAI X Bot 開始 ===")

    # 環境変数の検証
    if not validate_env_vars():
        logger.error("環境変数の検証に失敗しました")
        exit(1)

    try:
        fetch_and_forward()
        logger.info("=== ASAI X Bot 正常終了 ===")
    except Exception as e:
        logger.error(f"=== ASAI X Bot 異常終了: {e} ===")
        exit(1)


if __name__ == "__main__":
    main()
