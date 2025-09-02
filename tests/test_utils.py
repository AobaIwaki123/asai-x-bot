import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

sys.path.append("src")

from src.utils import (
    _load_since_id_from_file,
    _load_since_id_from_secret_manager,
    _save_since_id_to_file,
    _save_since_id_to_secret_manager,
    build_index,
    load_since_id,
    save_since_id,
)


class TestUtils:
    """utilsモジュールのテスト"""

    def test_build_index_with_default_key(self):
        """デフォルトキーでのインデックス構築テスト"""
        data = [{"id": "1", "name": "item1"}, {"id": "2", "name": "item2"}]
        result = build_index(data)
        expected = {"1": {"id": "1", "name": "item1"}, "2": {"id": "2", "name": "item2"}}
        assert result == expected

    def test_build_index_with_custom_key(self):
        """カスタムキーでのインデックス構築テスト"""
        data = [{"media_key": "key1", "url": "url1"}, {"media_key": "key2", "url": "url2"}]
        result = build_index(data, key="media_key")
        expected = {"key1": {"media_key": "key1", "url": "url1"}, "key2": {"media_key": "key2", "url": "url2"}}
        assert result == expected

    def test_build_index_empty_list(self):
        """空のリストでのインデックス構築テスト"""
        result = build_index([])
        assert result == {}

    def test_build_index_none_input(self):
        """Noneが渡された場合のテスト"""
        result = build_index(None)
        assert result == {}

    def test_load_since_id_from_file_exists(self):
        """ファイルが存在する場合のsince_id読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("123456789")
            tmp_path = tmp.name

        try:
            with patch("src.utils.STATE_FILE", tmp_path):
                result = _load_since_id_from_file()
                assert result == "123456789"
        finally:
            os.unlink(tmp_path)

    def test_load_since_id_from_file_not_exists(self):
        """ファイルが存在しない場合のsince_id読み込みテスト"""
        with patch("src.utils.STATE_FILE", "/nonexistent/file.txt"):
            result = _load_since_id_from_file()
            assert result is None

    def test_load_since_id_from_file_empty(self):
        """空のファイルの場合のsince_id読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("")
            tmp_path = tmp.name

        try:
            with patch("src.utils.STATE_FILE", tmp_path):
                result = _load_since_id_from_file()
                assert result is None
        finally:
            os.unlink(tmp_path)

    def test_save_since_id_to_file(self):
        """ファイルへのsince_id保存テスト"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch("src.utils.STATE_FILE", tmp_path):
                _save_since_id_to_file("987654321")

                with open(tmp_path) as f:
                    content = f.read()
                assert content == "987654321"
        finally:
            os.unlink(tmp_path)

    @patch("src.utils.secretmanager.SecretManagerServiceClient")
    def test_load_since_id_from_secret_manager_success(self, mock_client_class):
        """Secret Managerからの正常な読み込みテスト"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret_id_123"
        mock_client.access_secret_version.return_value = mock_response

        with patch("src.utils.PROJECT_ID", "test-project"), patch("src.utils.SINCE_ID_SECRET_NAME", "test-secret"):
            result = _load_since_id_from_secret_manager()
            assert result == "secret_id_123"

    @patch("src.utils.secretmanager.SecretManagerServiceClient")
    def test_load_since_id_from_secret_manager_exception(self, mock_client_class):
        """Secret Managerからの読み込み失敗テスト"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.access_secret_version.side_effect = Exception("API Error")

        with patch("src.utils.PROJECT_ID", "test-project"), patch("src.utils.SINCE_ID_SECRET_NAME", "test-secret"):
            result = _load_since_id_from_secret_manager()
            assert result is None

    @patch("src.utils.secretmanager.SecretManagerServiceClient")
    def test_save_since_id_to_secret_manager_new_secret(self, mock_client_class):
        """新しいシークレット作成時の保存テスト"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # シークレットが存在しない（NotFound例外）
        from google.api_core import exceptions as gcp_exceptions

        mock_client.get_secret.side_effect = gcp_exceptions.NotFound("Secret not found")

        mock_response = MagicMock()
        mock_response.name = "projects/test-project/secrets/test-secret/versions/1"
        mock_client.add_secret_version.return_value = mock_response

        with patch("src.utils.PROJECT_ID", "test-project"), patch("src.utils.SINCE_ID_SECRET_NAME", "test-secret"):
            _save_since_id_to_secret_manager("new_id_456")

            # シークレット作成が呼ばれることを確認
            mock_client.create_secret.assert_called_once()
            mock_client.add_secret_version.assert_called_once()

    def test_load_since_id_cloud_run_environment(self):
        """Cloud Run環境でのsince_id読み込みテスト"""
        with (
            patch("src.utils.PROJECT_ID", "test-project"),
            patch.dict(os.environ, {"K_SERVICE": "test-service"}),
            patch("src.utils._load_since_id_from_secret_manager", return_value="cloud_id"),
            patch("src.utils._load_since_id_from_file", return_value="file_id"),
        ):
            result = load_since_id()
            assert result == "cloud_id"

    def test_load_since_id_local_environment(self):
        """ローカル環境でのsince_id読み込みテスト"""
        with patch("src.utils.PROJECT_ID", None), patch("src.utils._load_since_id_from_file", return_value="file_id"):
            result = load_since_id()
            assert result == "file_id"

    def test_save_since_id_cloud_run_environment(self):
        """Cloud Run環境でのsince_id保存テスト"""
        with (
            patch("src.utils.PROJECT_ID", "test-project"),
            patch.dict(os.environ, {"K_SERVICE": "test-service"}),
            patch("src.utils._save_since_id_to_secret_manager") as mock_secret_save,
            patch("src.utils._save_since_id_to_file") as mock_file_save,
        ):
            save_since_id("test_id")
            mock_secret_save.assert_called_once_with("test_id")
            mock_file_save.assert_not_called()

    def test_save_since_id_local_environment(self):
        """ローカル環境でのsince_id保存テスト"""
        with patch("src.utils.PROJECT_ID", None), patch("src.utils._save_since_id_to_file") as mock_file_save:
            save_since_id("test_id")
            mock_file_save.assert_called_once_with("test_id")
