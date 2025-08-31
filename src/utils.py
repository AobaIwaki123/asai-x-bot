import logging

from config import STATE_FILE  # type: ignore

logger = logging.getLogger(__name__)


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
