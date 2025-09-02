import os
import sys
from unittest.mock import patch

# Add src to path before importing
if "src" not in sys.path:
    sys.path.append("src")

from src.config import (  # noqa: E402
    get_x_api_headers,
    get_x_api_params,
    validate_env_vars,
)


class TestConfig:
    """configモジュールのテスト"""

    def test_validate_env_vars_all_present(self):
        """すべての環境変数が設定されている場合のテスト"""
        env_vars = {
            "X_BEARER_TOKEN": "test_token",
            "DISCORD_WEBHOOK_URL": "https://discord.com/webhook",
            "QUERY": "test query",
        }
        with patch.dict(os.environ, env_vars):
            # 環境変数を再読み込み
            with (
                patch("src.config.X_BEARER_TOKEN", "test_token"),
                patch("src.config.WEBHOOK_URL", "https://discord.com/webhook"),
                patch("src.config.QUERY", "test query"),
            ):
                assert validate_env_vars() is True

    def test_validate_env_vars_missing_x_token(self):
        """X_BEARER_TOKENが設定されていない場合のテスト"""
        with (
            patch("src.config.X_BEARER_TOKEN", None),
            patch("src.config.WEBHOOK_URL", "https://discord.com/webhook"),
            patch("src.config.QUERY", "test query"),
        ):
            assert validate_env_vars() is False

    def test_validate_env_vars_missing_webhook_url(self):
        """DISCORD_WEBHOOK_URLが設定されていない場合のテスト"""
        with (
            patch("src.config.X_BEARER_TOKEN", "test_token"),
            patch("src.config.WEBHOOK_URL", None),
            patch("src.config.QUERY", "test query"),
        ):
            assert validate_env_vars() is False

    def test_validate_env_vars_missing_query(self):
        """QUERYが設定されていない場合のテスト"""
        with (
            patch("src.config.X_BEARER_TOKEN", "test_token"),
            patch("src.config.WEBHOOK_URL", "https://discord.com/webhook"),
            patch("src.config.QUERY", None),
        ):
            assert validate_env_vars() is False

    def test_get_x_api_headers(self):
        """X APIヘッダーの生成テスト"""
        with patch("src.config.X_BEARER_TOKEN", "test_token_123"):
            headers = get_x_api_headers()
            assert headers == {"Authorization": "Bearer test_token_123"}

    def test_get_x_api_params(self):
        """X APIパラメータの生成テスト"""
        with patch("src.config.QUERY", "test_query"):
            params = get_x_api_params()
            expected_params = {
                "query": "test_query",
                "max_results": 50,
                "tweet.fields": "created_at,lang,public_metrics,author_id",
                "user.fields": "name,username,profile_image_url",
                "media.fields": "url,preview_image_url,type",
                "expansions": "author_id,attachments.media_keys",
            }
            assert params == expected_params
