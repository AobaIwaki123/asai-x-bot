import sys
from unittest.mock import patch

import pytest

sys.path.append("src")

from src.main import fetch_and_forward, main


class TestMain:
    """mainモジュールのテスト"""

    @patch("src.main.save_since_id")
    @patch("src.main.discord_post")
    @patch("src.main.to_embed")
    @patch("src.main.build_index")
    @patch("src.main.fetch_tweets")
    @patch("src.main.load_since_id")
    def test_fetch_and_forward_success(
        self, mock_load_since_id, mock_fetch_tweets, mock_build_index, mock_to_embed, mock_discord_post, mock_save_since_id
    ):
        """正常なツイート取得と転送のテスト"""
        # モックの設定
        mock_load_since_id.return_value = "123"
        mock_fetch_tweets.return_value = {
            "data": [
                {"id": "125", "author_id": "user1", "text": "New tweet"},
                {"id": "124", "author_id": "user2", "text": "Another tweet"},
            ],
            "includes": {
                "users": [{"id": "user1", "username": "testuser1"}, {"id": "user2", "username": "testuser2"}],
                "media": [],
            },
        }
        mock_build_index.side_effect = [{"user1": {"username": "testuser1"}, "user2": {"username": "testuser2"}}, {}]
        mock_to_embed.return_value = {"title": "Test embed"}

        fetch_and_forward()

        # 各関数が適切に呼ばれることを確認
        mock_load_since_id.assert_called_once()
        mock_fetch_tweets.assert_called_once_with("123")
        assert mock_build_index.call_count == 2
        assert mock_to_embed.call_count == 2
        assert mock_discord_post.call_count == 2
        mock_save_since_id.assert_called_once_with("125")

    @patch("src.main.fetch_tweets")
    @patch("src.main.load_since_id")
    def test_fetch_and_forward_no_payload(self, mock_load_since_id, mock_fetch_tweets):
        """fetch_tweetsがNoneを返す場合のテスト"""
        mock_load_since_id.return_value = "123"
        mock_fetch_tweets.return_value = None

        # 例外が発生しないことを確認
        fetch_and_forward()

        mock_load_since_id.assert_called_once()
        mock_fetch_tweets.assert_called_once_with("123")

    @patch("src.main.build_index")
    @patch("src.main.fetch_tweets")
    @patch("src.main.load_since_id")
    def test_fetch_and_forward_no_tweets(self, mock_load_since_id, mock_fetch_tweets, mock_build_index):
        """ツイートが空の場合のテスト"""
        mock_load_since_id.return_value = "123"
        mock_fetch_tweets.return_value = {"data": [], "includes": {"users": [], "media": []}}
        mock_build_index.return_value = {}

        # 例外が発生しないことを確認
        fetch_and_forward()

        mock_load_since_id.assert_called_once()
        mock_fetch_tweets.assert_called_once_with("123")

    @patch("src.main.save_since_id")
    @patch("src.main.discord_post")
    @patch("src.main.to_embed")
    @patch("src.main.build_index")
    @patch("src.main.fetch_tweets")
    @patch("src.main.load_since_id")
    def test_fetch_and_forward_tweet_sorting(
        self, mock_load_since_id, mock_fetch_tweets, mock_build_index, mock_to_embed, mock_discord_post, mock_save_since_id
    ):
        """ツイートがID順でソートされることのテスト"""
        # IDが逆順のツイート
        mock_load_since_id.return_value = "120"
        mock_fetch_tweets.return_value = {
            "data": [
                {"id": "125", "author_id": "user1", "text": "Latest tweet"},
                {"id": "122", "author_id": "user2", "text": "Earlier tweet"},
                {"id": "124", "author_id": "user3", "text": "Middle tweet"},
            ],
            "includes": {
                "users": [
                    {"id": "user1", "username": "testuser1"},
                    {"id": "user2", "username": "testuser2"},
                    {"id": "user3", "username": "testuser3"},
                ],
                "media": [],
            },
        }
        mock_build_index.side_effect = [
            {"user1": {"username": "testuser1"}, "user2": {"username": "testuser2"}, "user3": {"username": "testuser3"}},
            {},
        ]
        mock_to_embed.return_value = {"title": "Test embed"}

        fetch_and_forward()

        # to_embedが呼ばれた順序を確認（ID順になっているはず）
        calls = mock_to_embed.call_args_list
        assert len(calls) == 3
        assert calls[0][0][0]["id"] == "122"  # 最初に処理されるべき
        assert calls[1][0][0]["id"] == "124"  # 2番目
        assert calls[2][0][0]["id"] == "125"  # 最後

        # 最大IDで保存されることを確認
        mock_save_since_id.assert_called_once_with("125")

    @patch("src.main.fetch_and_forward")
    @patch("src.main.validate_env_vars")
    def test_main_success(self, mock_validate_env_vars, mock_fetch_and_forward):
        """メイン関数の正常実行テスト"""
        mock_validate_env_vars.return_value = True

        main()

        mock_validate_env_vars.assert_called_once()
        mock_fetch_and_forward.assert_called_once()

    @patch("src.main.validate_env_vars")
    def test_main_env_validation_failure(self, mock_validate_env_vars):
        """環境変数検証失敗時のテスト"""
        mock_validate_env_vars.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_validate_env_vars.assert_called_once()

    @patch("src.main.fetch_and_forward")
    @patch("src.main.validate_env_vars")
    def test_main_fetch_and_forward_exception(self, mock_validate_env_vars, mock_fetch_and_forward):
        """fetch_and_forward関数で例外が発生した場合のテスト"""
        mock_validate_env_vars.return_value = True
        mock_fetch_and_forward.side_effect = Exception("Test error")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_validate_env_vars.assert_called_once()
        mock_fetch_and_forward.assert_called_once()
