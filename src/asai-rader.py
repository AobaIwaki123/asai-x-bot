import datetime
import html
import logging
import os
import time
from urllib.parse import urlencode

import requests  # type: ignore
from dotenv import load_dotenv

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# .env を読み込み
logger.info("環境変数の読み込みを開始")
load_dotenv()

# 値を取得
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
QUERY = os.getenv("QUERY")

# 環境変数の検証
if not X_BEARER_TOKEN:
    logger.error("X_BEARER_TOKEN が設定されていません")
    exit(1)
if not WEBHOOK_URL:
    logger.error("DISCORD_WEBHOOK_URL が設定されていません")
    exit(1)
if not QUERY:
    logger.error("QUERY が設定されていません")
    exit(1)

logger.info(f"検索クエリ: {QUERY}")
logger.info(f"Discord Webhook URL: {WEBHOOK_URL[:50]}...")

STATE_FILE = "since_id.txt"

SEARCH_URL = "https://api.x.com/2/tweets/search/recent"
HEADERS = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}

# fields / expansions（画像や著者名をEmbedに載せるため）
PARAMS_BASE = {
    "query": QUERY,
    "max_results": 50,  # 10〜100
    "tweet.fields": "created_at,lang,public_metrics,author_id",
    "user.fields": "name,username,profile_image_url",
    "media.fields": "url,preview_image_url,type",
    "expansions": "author_id,attachments.media_keys",
}


def load_since_id():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            since_id = f.read().strip() or None
            if since_id:
                logger.info(
                    f"前回の処理IDを読み込み: {since_id}"
                )
            else:
                logger.info(
                    "前回の処理IDが見つかりません。初回実行として処理します"
                )
            return since_id
    except FileNotFoundError:
        logger.info(
            "状態ファイルが見つかりません。初回実行として処理します"
        )
        return None


def save_since_id(since_id: str):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(since_id)
    logger.info(f"処理IDを保存: {since_id}")


def build_index(data_list, key="id"):
    return (
        {item[key]: item for item in data_list}
        if data_list
        else {}
    )


def discord_post(content=None, embed=None):
    payload = {}
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]

    try:
        logger.info("Discordに投稿中...")
        r = requests.post(
            WEBHOOK_URL, json=payload, timeout=15
        )
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
    if (
        "attachments" in tweet
        and "media_keys" in tweet["attachments"]
    ):
        for mk in tweet["attachments"]["media_keys"]:
            m = media_idx.get(mk)
            if m and m.get("type") == "photo":
                image_url = m.get("url") or m.get(
                    "preview_image_url"
                )
                break

    # Embed
    title = f"@{username}"
    description = html.unescape(tweet.get("text", ""))[
        :4000
    ]  # Discord制限対策
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


def fetch_and_forward():
    logger.info("ツイートの取得と転送を開始")

    params = PARAMS_BASE.copy()
    since_id = load_since_id()
    if since_id:
        params["since_id"] = since_id
        logger.info(
            f"前回のID以降のツイートを取得: {since_id}"
        )
    else:
        logger.info("初回実行のため、最新のツイートを取得")

    url = f"{SEARCH_URL}?{urlencode(params, doseq=True)}"
    logger.info(f"X APIにリクエスト送信中: {url}")

    try:
        res = requests.get(url, headers=HEADERS, timeout=30)

        # HTTPレスポンスコードとヘッダーの詳細ログ
        logger.info(
            f"X API レスポンスコード: {res.status_code}"
        )

        # レート制限関連のヘッダーをログ出力
        rate_limit_limit = res.headers.get(
            "x-rate-limit-limit"
        )
        rate_limit_remaining = res.headers.get(
            "x-rate-limit-remaining"
        )
        rate_limit_reset = res.headers.get(
            "x-rate-limit-reset"
        )

        if rate_limit_limit:
            logger.info(
                f"レート制限上限: {rate_limit_limit}"
            )
        if rate_limit_remaining:
            logger.info(
                f"残りリクエスト数: {rate_limit_remaining}"
            )
        if rate_limit_reset:
            utc_time = datetime.datetime.fromtimestamp(
                int(rate_limit_reset),
                tz=datetime.timezone.utc,
            )
            jst_time = utc_time.astimezone(
                datetime.timezone(
                    datetime.timedelta(hours=9)
                )
            )
            logger.info(
                f"レート制限リセット時刻: JST {jst_time.strftime('%Y-%m-%d %H:%M:%S')} "
            )

        if res.status_code == 429:
            # レート制限時は詳細なエラー情報をログ出力
            logger.warning(
                "レート制限に達しました (HTTP 429)"
            )
            try:
                error_payload = res.json()
                if "errors" in error_payload:
                    for error in error_payload["errors"]:
                        error_code = error.get("code")
                        error_message = error.get("message")
                        logger.warning(
                            f"エラー詳細 - コード: {error_code}, "
                            f"メッセージ: {error_message}"
                        )
            except Exception as parse_error:
                logger.warning(
                    f"エラーレスポンスの解析に失敗: {parse_error}"
                )

            logger.info("60秒待機してリトライします")
            time.sleep(60)
            return

        res.raise_for_status()
        payload = res.json()
        logger.info("X APIからのレスポンス取得成功")
    except Exception as e:
        logger.error(
            f"X APIからのレスポンス取得に失敗: {e}"
        )
        raise

    tweets = payload.get("data", [])
    includes = payload.get("includes", {})
    users_idx = build_index(includes.get("users", []))
    media_idx = build_index(
        includes.get("media", []), key="media_key"
    )

    if not tweets:
        logger.info("新しいツイートはありません")
        return

    logger.info(f"取得したツイート数: {len(tweets)}")
    logger.info(
        f"取得したユーザー数: {len(includes.get('users', []))}"
    )
    logger.info(
        f"取得したメディア数: {len(includes.get('media', []))}"
    )

    # 古い順に送る（Discordの読みやすさ配慮）
    tweets_sorted = sorted(tweets, key=lambda t: t["id"])
    logger.info("ツイートをDiscordに転送中...")

    for i, tw in enumerate(tweets_sorted, 1):
        username = users_idx.get(tw["author_id"], {}).get(
            "username", "unknown"
        )
        logger.info(
            f"ツイート {i}/{len(tweets_sorted)} を処理中: "
            f"@{username}"
        )
        embed = to_embed(tw, users_idx, media_idx)
        discord_post(embed=embed)

    # 次回用に最大IDを保存
    max_id = max(t["id"] for t in tweets_sorted)
    save_since_id(max_id)
    logger.info(
        f"処理完了。{len(tweets)}件のツイートを転送しました"
    )


if __name__ == "__main__":
    # 単発実行（cronやサーバーレスで1分〜5分おき推奨）
    logger.info("=== ASAI X Bot 開始 ===")
    try:
        fetch_and_forward()
        logger.info("=== ASAI X Bot 正常終了 ===")
    except Exception as e:
        logger.error(f"=== ASAI X Bot 異常終了: {e} ===")
        exit(1)
