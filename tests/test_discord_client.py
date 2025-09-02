import json
import sys
from unittest.mock import patch

import pytest
import requests.exceptions
import responses

sys.path.append("src")

from src.discord_client import discord_post, to_embed


class TestDiscordClient:
    """discord_clientモジュールのテスト"""

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
        assert json.loads(
            responses.calls[0].request.body
        ) == {"content": "Test message"}

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
        assert json.loads(
            responses.calls[0].request.body
        ) == {"embeds": [embed]}

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
            discord_post(
                content="Test message", embed=embed
            )

        expected_payload = {
            "content": "Test message",
            "embeds": [embed],
        }
        assert (
            json.loads(responses.calls[0].request.body)
            == expected_payload
        )

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
            with pytest.raises(
                requests.exceptions.HTTPError
            ):
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

    def test_to_embed_basic_tweet(self):
        """基本的なツイートの埋め込み変換テスト"""
        tweet = {
            "id": "123456789",
            "author_id": "user1",
            "text": "This is a test tweet",
            "public_metrics": {
                "like_count": 10,
                "retweet_count": 5,
            },
        }

        users_idx = {
            "user1": {
                "username": "testuser",
                "name": "Test User",
                "profile_image_url": "https://example.com/avatar.jpg",
            }
        }

        media_idx: dict[str, dict] = {}

        result = to_embed(tweet, users_idx, media_idx)

        expected = {
            "title": "@testuser",
            "url": "https://x.com/testuser/status/123456789",
            "description": "This is a test tweet",
            "author": {
                "name": "Test User",
                "url": "https://x.com/testuser",
                "icon_url": "https://example.com/avatar.jpg",
            },
            "footer": {"text": "likes: 10  rt: 5"},
        }

        assert result == expected

    def test_to_embed_with_image(self):
        """画像付きツイートの埋め込み変換テスト"""
        tweet = {
            "id": "123456789",
            "author_id": "user1",
            "text": "Tweet with image",
            "public_metrics": {
                "like_count": 20,
                "retweet_count": 8,
            },
            "attachments": {
                "media_keys": ["media1", "media2"]
            },
        }

        users_idx = {
            "user1": {
                "username": "testuser",
                "name": "Test User",
            }
        }

        media_idx = {
            "media1": {
                "type": "photo",
                "url": "https://example.com/image1.jpg",
            },
            "media2": {
                "type": "video",
                "preview_image_url": "https://example.com/video_thumb.jpg",
            },
        }

        result = to_embed(tweet, users_idx, media_idx)

        # 最初の画像が埋め込まれることを確認
        assert "image" in result
        assert (
            result["image"]["url"]
            == "https://example.com/image1.jpg"
        )

    def test_to_embed_unknown_user(self):
        """不明なユーザーのツイート埋め込み変換テスト"""
        tweet = {
            "id": "123456789",
            "author_id": "unknown_user",
            "text": "Tweet from unknown user",
            "public_metrics": {
                "like_count": 0,
                "retweet_count": 0,
            },
        }

        users_idx: dict[str, dict] = {}
        media_idx: dict[str, dict] = {}

        result = to_embed(tweet, users_idx, media_idx)

        assert result["title"] == "@unknown"
        assert result["author"]["name"] == "unknown"
        assert (
            result["url"]
            == "https://x.com/unknown/status/123456789"
        )

    def test_to_embed_long_text(self):
        """長いテキストのツイート埋め込み変換テスト"""
        long_text = (
            "A" * 5000
        )  # 4000文字を超える長いテキスト

        tweet = {
            "id": "123456789",
            "author_id": "user1",
            "text": long_text,
            "public_metrics": {
                "like_count": 1,
                "retweet_count": 0,
            },
        }

        users_idx = {
            "user1": {
                "username": "testuser",
                "name": "Test User",
            }
        }

        media_idx: dict[str, dict] = {}

        result = to_embed(tweet, users_idx, media_idx)

        # テキストが4000文字以下に制限されることを確認
        assert len(result["description"]) <= 4000

    def test_to_embed_html_entities(self):
        """HTMLエンティティを含むツイートの埋め込み変換テスト"""
        tweet = {
            "id": "123456789",
            "author_id": "user1",
            "text": "Test &amp; tweet with &lt;html&gt; entities",
            "public_metrics": {
                "like_count": 5,
                "retweet_count": 2,
            },
        }

        users_idx = {
            "user1": {
                "username": "testuser",
                "name": "Test User",
            }
        }

        media_idx: dict[str, dict] = {}

        result = to_embed(tweet, users_idx, media_idx)

        # HTMLエンティティがデコードされることを確認
        assert (
            result["description"]
            == "Test & tweet with <html> entities"
        )
