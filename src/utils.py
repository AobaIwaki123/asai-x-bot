import logging
import os

from google.api_core import exceptions as gcp_exceptions
from google.cloud import secretmanager

from .config import (
    PROJECT_ID,
    SINCE_ID_SECRET_NAME,
    STATE_FILE,
)

logger = logging.getLogger(__name__)


def _get_secret_manager_client():
    """Secret Manager クライアントを取得"""
    return secretmanager.SecretManagerServiceClient()


def _get_secret_path():
    """Secret Managerのシークレットパスを取得"""
    return f"projects/{PROJECT_ID}/secrets/{SINCE_ID_SECRET_NAME}"


def _load_since_id_from_secret_manager():
    """Secret Manager から since_id を読み込み"""
    try:
        client = _get_secret_manager_client()
        name = f"{_get_secret_path()}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        since_id = response.payload.data.decode("UTF-8").strip()

        if since_id:
            logger.info(f"Secret Manager から前回の処理IDを読み込み: {since_id}")
            return since_id
        else:
            logger.info("Secret Manager から空の処理IDを読み込み。初回実行として処理します")
            return None
    except Exception as e:
        logger.info(f"Secret Manager からの読み込みに失敗: {e}")
        return None


def _save_since_id_to_secret_manager(since_id: str):
    """Secret Manager に since_id を保存"""
    try:
        client = _get_secret_manager_client()
        parent = f"projects/{PROJECT_ID}"
        secret_id = SINCE_ID_SECRET_NAME

        # シークレットが存在しない場合は作成
        try:
            client.get_secret(request={"name": _get_secret_path()})
        except gcp_exceptions.NotFound:
            logger.info(f"Secret Manager にシークレット {secret_id} を作成中...")
            client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
            logger.info(f"Secret Manager にシークレット {secret_id} を作成しました")

        # バージョンを追加
        response = client.add_secret_version(
            request={
                "parent": _get_secret_path(),
                "payload": {"data": since_id.encode("UTF-8")},
            }
        )
        version_info = f"version: {response.name}"
        logger.info(f"Secret Manager に処理IDを保存: {since_id} ({version_info})")

    except Exception as e:
        logger.error(f"Secret Manager への保存に失敗: {e}")
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
    # Cloud Run環境では SECRET_MANAGER を優先
    if PROJECT_ID and os.getenv("K_SERVICE"):  # Cloud Run環境の判定
        since_id = _load_since_id_from_secret_manager()
        if since_id is not None:
            return since_id

    # フォールバック: ローカルファイル
    return _load_since_id_from_file()


def save_since_id(since_id: str):
    """since_id を保存（Secret Manager -> ファイルの順で試行）"""
    # Cloud Run環境では SECRET_MANAGER を優先
    if PROJECT_ID and os.getenv("K_SERVICE"):  # Cloud Run環境の判定
        try:
            _save_since_id_to_secret_manager(since_id)
            return
        except Exception as e:
            logger.warning(f"Secret Manager への保存に失敗。ファイルにフォールバック: {e}")

    # フォールバック: ローカルファイル
    _save_since_id_to_file(since_id)


def build_index(data_list, key="id"):
    return {item[key]: item for item in data_list} if data_list else {}
