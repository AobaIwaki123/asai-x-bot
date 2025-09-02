import datetime
import logging
import time
from urllib.parse import urlencode

import requests

from config import (
    SEARCH_URL,
    get_x_api_headers,
    get_x_api_params,
)

logger = logging.getLogger(__name__)


def fetch_tweets(since_id=None):
    """X APIからツイートを取得する"""
    params = get_x_api_params().copy()
    if since_id:
        params["since_id"] = since_id
        logger.info(f"前回のID以降のツイートを取得: {since_id}")
    else:
        logger.info("初回実行のため、最新のツイートを取得")

    url = f"{SEARCH_URL}?{urlencode(params, doseq=True)}"
    logger.info(f"X APIにリクエスト送信中: {url}")

    try:
        res = requests.get(url, headers=get_x_api_headers(), timeout=30)

        # HTTPレスポンスコードとヘッダーの詳細ログ
        logger.info(f"X API レスポンスコード: {res.status_code}")

        # レート制限関連のヘッダーをログ出力
        log_rate_limit_info(res)

        if res.status_code == 429:
            # レート制限時は詳細なエラー情報をログ出力
            logger.warning("レート制限に達しました (HTTP 429)")
            try:
                error_payload = res.json()
                if "errors" in error_payload:
                    for error in error_payload["errors"]:
                        error_code = error.get("code")
                        error_message = error.get("message")
                        detail = f"コード: {error_code}, メッセージ: {error_message}"
                        logger.warning(f"エラー詳細 - {detail}")
            except Exception as parse_error:
                logger.warning(f"エラーレスポンスの解析に失敗: {parse_error}")

            logger.info("15分待機してリトライします")
            time.sleep(900)
            return None

        res.raise_for_status()
        payload = res.json()
        logger.info("X APIからのレスポンス取得成功")
        return payload
    except Exception:
        logger.exception("X APIからのレスポンス取得に失敗")
        raise


def log_rate_limit_info(res):
    """レート制限情報をログ出力する"""
    rate_limit_limit = res.headers.get("x-rate-limit-limit")
    rate_limit_remaining = res.headers.get("x-rate-limit-remaining")
    rate_limit_reset = res.headers.get("x-rate-limit-reset")

    if rate_limit_limit:
        logger.info(f"レート制限上限: {rate_limit_limit}")
    if rate_limit_remaining:
        logger.info(f"残りリクエスト数: {rate_limit_remaining}")
    if rate_limit_reset:
        utc_time = datetime.datetime.fromtimestamp(
            int(rate_limit_reset),
            tz=datetime.timezone.utc,  # noqa
        )
        jst_offset = datetime.timedelta(hours=9)
        jst_time = utc_time.astimezone(datetime.timezone(jst_offset))
        reset_time = jst_time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"レート制限リセット時刻: JST {reset_time}")
