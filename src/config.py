import logging
import os

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
def validate_env_vars():
    if not X_BEARER_TOKEN:
        logger.error("X_BEARER_TOKEN が設定されていません")
        return False
    if not WEBHOOK_URL:
        logger.error(
            "DISCORD_WEBHOOK_URL が設定されていません"
        )
        return False
    if not QUERY:
        logger.error("QUERY が設定されていません")
        return False
    return True


# 設定値
STATE_FILE = "since_id.txt"
SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


# X API用のヘッダーとパラメータ
def get_x_api_headers():
    return {"Authorization": f"Bearer {X_BEARER_TOKEN}"}


def get_x_api_params():
    return {
        "query": QUERY,
        "max_results": 50,  # 10〜100
        "tweet.fields": "created_at,lang,public_metrics,author_id",
        "user.fields": "name,username,profile_image_url",
        "media.fields": "url,preview_image_url,type",
        "expansions": "author_id,attachments.media_keys",
    }
