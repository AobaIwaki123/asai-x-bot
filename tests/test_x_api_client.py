import sys
from unittest.mock import MagicMock, patch

import pytest
import requests.exceptions
import responses

sys.path.append("src")

from src.x_api_client import (
    fetch_tweets,
    log_rate_limit_info,
)


class TestXApiClient:
    """x_api_clientモジュールのテスト"""

    @responses.activate
    def test_fetch_tweets_success_without_since_id(self):
        """since_idなしでのツイート取得成功テスト"""
        mock_response = {
            "data": [
                {
                    "id": "123",
                    "text": "Test tweet",
                    "author_id": "user1",
                }
            ],
            "includes": {"users": [{"id": "user1", "username": "testuser"}]},
        }

        responses.add(
            responses.GET,
            "https://api.x.com/2/tweets/search/recent",
            json=mock_response,
            status=200,
        )

        with (
            patch(
                "src.x_api_client.get_x_api_headers",
                return_value={"Authorization": "Bearer test"},
            ),
            patch(
                "src.x_api_client.get_x_api_params",
                return_value={
                    "query": "test",
                    "max_results": 50,
                },
            ),
        ):
            result = fetch_tweets()
            assert result == mock_response

    @responses.activate
    def test_fetch_tweets_success_with_since_id(self):
        """since_idありでのツイート取得成功テスト"""
        mock_response = {
            "data": [
                {
                    "id": "124",
                    "text": "New tweet",
                    "author_id": "user1",
                }
            ]
        }

        responses.add(
            responses.GET,
            "https://api.x.com/2/tweets/search/recent",
            json=mock_response,
            status=200,
        )

        with (
            patch(
                "src.x_api_client.get_x_api_headers",
                return_value={"Authorization": "Bearer test"},
            ),
            patch(
                "src.x_api_client.get_x_api_params",
                return_value={
                    "query": "test",
                    "max_results": 50,
                },
            ),
        ):
            result = fetch_tweets(since_id="123")
            assert result == mock_response

    @responses.activate
    def test_fetch_tweets_rate_limit(self):
        """レート制限時のテスト"""
        error_response = {
            "errors": [
                {
                    "code": 88,
                    "message": "Rate limit exceeded",
                }
            ]
        }

        responses.add(
            responses.GET,
            "https://api.x.com/2/tweets/search/recent",
            json=error_response,
            status=429,
            headers={
                "x-rate-limit-limit": "300",
                "x-rate-limit-remaining": "0",
                "x-rate-limit-reset": "1640995200",
            },
        )

        with (
            patch(
                "src.x_api_client.get_x_api_headers",
                return_value={"Authorization": "Bearer test"},
            ),
            patch(
                "src.x_api_client.get_x_api_params",
                return_value={
                    "query": "test",
                    "max_results": 50,
                },
            ),
            patch("src.x_api_client.time.sleep") as mock_sleep,
        ):
            result = fetch_tweets()
            assert result is None
            mock_sleep.assert_called_once_with(60)

    @responses.activate
    def test_fetch_tweets_http_error(self):
        """HTTPエラー時のテスト"""
        responses.add(
            responses.GET,
            "https://api.x.com/2/tweets/search/recent",
            json={"error": "Unauthorized"},
            status=401,
        )

        with (
            patch(
                "src.x_api_client.get_x_api_headers",
                return_value={"Authorization": "Bearer test"},
            ),
            patch(
                "src.x_api_client.get_x_api_params",
                return_value={
                    "query": "test",
                    "max_results": 50,
                },
            ),
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                fetch_tweets()

    @responses.activate
    def test_fetch_tweets_connection_error(self):
        """接続エラー時のテスト"""
        responses.add(
            responses.GET,
            "https://api.x.com/2/tweets/search/recent",
            body=ConnectionError("Connection failed"),
        )

        with (
            patch(
                "src.x_api_client.get_x_api_headers",
                return_value={"Authorization": "Bearer test"},
            ),
            patch(
                "src.x_api_client.get_x_api_params",
                return_value={
                    "query": "test",
                    "max_results": 50,
                },
            ),
        ):
            with pytest.raises(ConnectionError):
                fetch_tweets()

    def test_log_rate_limit_info_all_headers(self):
        """すべてのレート制限ヘッダーが存在する場合のテスト"""
        mock_response = MagicMock()
        mock_response.headers = {
            "x-rate-limit-limit": "300",
            "x-rate-limit-remaining": "250",
            "x-rate-limit-reset": "1640995200",
        }

        with patch("src.x_api_client.logger") as mock_logger:
            log_rate_limit_info(mock_response)
            assert mock_logger.info.call_count == 3

    def test_log_rate_limit_info_partial_headers(self):
        """一部のレート制限ヘッダーのみ存在する場合のテスト"""
        mock_response = MagicMock()
        mock_response.headers = {"x-rate-limit-limit": "300"}

        with patch("src.x_api_client.logger") as mock_logger:
            log_rate_limit_info(mock_response)
            assert mock_logger.info.call_count == 1

    def test_log_rate_limit_info_no_headers(self):
        """レート制限ヘッダーが存在しない場合のテスト"""
        mock_response = MagicMock()
        mock_response.headers = {}

        with patch("src.x_api_client.logger") as mock_logger:
            log_rate_limit_info(mock_response)
            assert mock_logger.info.call_count == 0
