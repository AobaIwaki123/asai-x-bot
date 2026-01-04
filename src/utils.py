import datetime
import logging
import os

from google.api_core import exceptions as gcp_exceptions
from google.cloud import firestore

from config import (
    FIRESTORE_COLLECTION,
    FIRESTORE_DB_NAME,
    FIRESTORE_DOC_ID,
    PROJECT_ID,
    STATE_FILE,
)


logger = logging.getLogger(__name__)


def is_since_id_valid(since_id: str) -> bool:
    """
    since_id が X API の制限内（7日以内）かどうかを確認

    Args:
        since_id: Twitter snowflake ID

    Returns:
        bool: 7日以内なら True、それより古いなら False
    """
    if not since_id:
        return False

    try:
        # Twitter snowflake ID を timestamp に変換
        # Twitter snowflake epoch は 1288834974657 (Nov 4, 2010 01:42:54 UTC)
        twitter_epoch = 1288834974657
        timestamp = ((int(since_id) >> 22) + twitter_epoch) / 1000
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)

        # 現在時刻との差分を計算
        now = datetime.datetime.now(datetime.UTC)
        days_ago = (now - dt).days

        logger.info(f"since_id {since_id} は {days_ago} 日前のツイート")

        # X API の recent search は7日以内のみ
        if days_ago >= 7:
            logger.warning(f"since_id が古すぎます（{days_ago}日前）。リセットします")
            return False

        return True

    except (ValueError, OverflowError) as e:
        logger.warning(f"since_id の変換に失敗: {e}")
        return False


def _get_firestore_client():
    """Firestore クライアントを取得"""
    return firestore.Client(project=PROJECT_ID, database=FIRESTORE_DB_NAME)


def _load_since_id_from_firestore():
    """Firestore から since_id を読み込み"""
    try:
        db = _get_firestore_client()
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(FIRESTORE_DOC_ID)
        doc = doc_ref.get()

        if doc.exists:
            since_id = doc.to_dict().get("since_id")
            if since_id:
                logger.info(f"Firestore から前回の処理IDを読み込み: {since_id}")
                return since_id

        logger.info("Firestore から空の処理IDを読み込み。初回実行として処理します")
        return None
    except Exception as e:
        logger.info(f"Firestore からの読み込みに失敗: {e}")
        return None


def _save_since_id_to_firestore(since_id: str):
    """Firestore に since_id を保存"""
    try:
        db = _get_firestore_client()
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(FIRESTORE_DOC_ID)
        doc_ref.set({"since_id": since_id}, merge=True)
        logger.info(f"Firestore に処理IDを保存: {since_id}")

    except Exception:
        logger.exception("Firestore への保存に失敗")
        raise


def _load_since_id_from_file():
    """ファイルから since_id を読み込み（フォールバック用）"""
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            since_id = f.read().strip() or None
            if since_id:
                logger.info(f"ファイルから前回の処理IDを読み込み: {since_id}")
            else:
                logger.info("ファイルから空の処理IDを読み込み。初回実行として処理します")
            return since_id
    except FileNotFoundError:
        logger.info("状態ファイルが見つかりません。初回実行として処理します")
        return None


def _save_since_id_to_file(since_id: str):
    """ファイルに since_id を保存（フォールバック用）"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(since_id)
    logger.info(f"ファイルに処理IDを保存: {since_id}")


def load_since_id():
    """since_id を読み込み（Secret Manager -> ファイルの順で試行）"""
    # Cloud Run環境では FIRESTORE を優先
    if PROJECT_ID and os.getenv("K_SERVICE"):  # Cloud Run環境の判定
        since_id = _load_since_id_from_firestore()
        if since_id is not None:
            # 7日制限チェック
            if is_since_id_valid(since_id):
                return since_id
            logger.info("Firestore の since_id が古いため、初回実行として処理します")
            return None

    since_id = _load_since_id_from_file()
    if since_id is not None:
        # 7日制限チェック
        if is_since_id_valid(since_id):
            return since_id
        logger.info("ファイルの since_id が古いため、初回実行として処理します")
        return None

    return None


def save_since_id(since_id: str):
    """since_id を保存（Secret Manager -> ファイルの順で試行）"""
    # Cloud Run環境では FIRESTORE を優先
    if PROJECT_ID and os.getenv("K_SERVICE"):  # Cloud Run環境の判定
        try:
            _save_since_id_to_firestore(since_id)
            return
        except Exception as e:
            logger.warning(f"Firestore への保存に失敗。ファイルにフォールバック: {e}")

    _save_since_id_to_file(since_id)


def build_index(data_list, key="id"):
    return {item[key]: item for item in data_list} if data_list else {}
