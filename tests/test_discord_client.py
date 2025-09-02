import json
import sys
from unittest.mock import patch

import pytest
import requests.exceptions
import responses

sys.path.append("src")

from src.discord_client import discord_post, get_tweet_url


class TestDiscordClient:
    """discord_clientモジュールのテスト"""

    def _request_json(self, index: int = 0):
        body = responses.calls[index].request.body
        assert body is not None
        if isinstance(body, bytes):
            body = body.decode()
        return json.loads(body)

    @responses.activate
    def test_discord_post_with_content(self):
        """コンテンツありでのDiscord投稿テスト"""
        responses.add(
            responses.POST,
            "https://discord.com/webhook",
            status=200,
        )

        with patch(
            "src.discord_client.WEBHOOK_URL",
            "https://discord.com/webhook",
        ):
            discord_post(content="Test message")

        assert len(responses.calls) == 1
        assert self._request_json() == {"content": "Test message"}

    @responses.activate
    def test_discord_post_with_embed(self):
        """埋め込みありでのDiscord投稿テスト"""
        embed = {
            "title": "Test Embed",
            "description": "Test description",
        }

        responses.add(
            responses.POST,
            "https://discord.com/webhook",
            status=200,
        )

        with patch(
            "src.discord_client.WEBHOOK_URL",
            "https://discord.com/webhook",
        ):
            discord_post(embed=embed)

        assert len(responses.calls) == 1
        assert self._request_json() == {"embeds": [embed]}

    @responses.activate
    def test_discord_post_with_both(self):
        """コンテンツと埋め込み両方でのDiscord投稿テスト"""
        embed = {"title": "Test Embed"}

        responses.add(
            responses.POST,
            "https://discord.com/webhook",
            status=200,
        )

        with patch(
            "src.discord_client.WEBHOOK_URL",
            "https://discord.com/webhook",
        ):
            discord_post(content="Test message", embed=embed)

        expected_payload = {
            "content": "Test message",
            "embeds": [embed],
        }
        assert self._request_json() == expected_payload

    @responses.activate
    def test_discord_post_http_error(self):
        """Discord投稿でHTTPエラーが発生した場合のテスト"""
        responses.add(
            responses.POST,
            "https://discord.com/webhook",
            status=400,
        )

        with patch(
            "src.discord_client.WEBHOOK_URL",
            "https://discord.com/webhook",
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                discord_post(content="Test message")

    @responses.activate
    def test_discord_post_connection_error(self):
        """Discord投稿で接続エラーが発生した場合のテスト"""
        responses.add(
            responses.POST,
            "https://discord.com/webhook",
            body=ConnectionError("Connection failed"),
        )

        with patch(
            "src.discord_client.WEBHOOK_URL",
            "https://discord.com/webhook",
        ):
            with pytest.raises(ConnectionError):
                discord_post(content="Test message")

    def test_get_tweet_url_basic(self):
        """基本的なツイートURLの生成テスト"""
        tweet = {
            "id": "123456789",
            "author_id": "user1",
        }

        users_idx = {
            "user1": {
                "username": "testuser",
            }
        }

        result = get_tweet_url(tweet, users_idx)
        expected = "https://x.com/testuser/status/123456789"

        assert result == expected

    def test_get_tweet_url_unknown_user(self):
        """不明なユーザーのツイートURL生成テスト"""
        tweet = {
            "id": "123456789",
            "author_id": "unknown_user",
        }

        users_idx: dict[str, dict] = {}

        result = get_tweet_url(tweet, users_idx)
        expected = "https://x.com/unknown/status/123456789"

        assert result == expected
