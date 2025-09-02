# Testing Documentation

このプロジェクトでは包括的なテストスイートとCIパイプラインが設定されています。

## テストの概要

### テストカバレッジ
- **83%** の全体テストカバレッジ
- 全主要モジュールの単体テスト実装済み
- モック・パッチによる外部依存関係の隔離

### テストファイル構成
```
tests/
├── __init__.py
├── test_config.py          # 設定モジュールのテスト
├── test_discord_client.py  # Discord連携のテスト
├── test_main.py           # メインロジックのテスト
├── test_utils.py          # ユーティリティ関数のテスト
└── test_x_api_client.py   # X API連携のテスト
```

## ローカルでのテスト実行

### 前提条件
```bash
# 依存関係のインストール
pip install -r requirements.txt
```

### テスト実行コマンド

#### 基本実行
```bash
# 全テスト実行
pytest tests/

# カバレッジレポート付き
pytest tests/ --cov=src --cov-report=term-missing

# HTMLカバレッジレポート生成
pytest tests/ --cov=src --cov-report=html
```

#### Makeコマンド（推奨）
```bash
# 全テスト実行（カバレッジ付き）
make test

# 高速テスト実行（カバレッジなし）
make test-fast

# 全チェック実行（リント・型チェック・セキュリティ・テスト）
make all

# CI用チェック実行
make ci
```

#### 特定のテストファイル実行
```bash
# 特定のテストファイル
pytest tests/test_config.py -v

# 特定のテストメソッド
pytest tests/test_config.py::TestConfig::test_validate_env_vars_all_present -v
```

## コード品質チェック

### リント
```bash
# ruffでのコード品質チェック
make lint
ruff check src/ tests/

# 型チェック（ruffの型関連ルールを使用）
make type-check
ruff check --select=F,E9,W6 src tests
```

### フォーマット
```bash
# コードフォーマット実行
make format
ruff format src/ tests/
ruff check --fix src/ tests/

# フォーマットチェック（変更なし）
make format-check
ruff format --check src/ tests/
ruff check src/ tests/
```

### セキュリティチェック
```bash
# セキュリティスキャン
make security
bandit -r src/
safety check
```

## CIパイプライン（GitHub Actions）

### ワークフロー

#### メインCI（`.github/workflows/ci.yml`）
- **Python 3.12** でのテスト実行
- リント（ruff） 
- テスト実行（pytest + coverage）
- セキュリティチェック（bandit, safety）
- コードフォーマットチェック（ruff）
- Docker イメージビルドテスト
- Codecov連携

#### プリコミットチェック（`.github/workflows/pre-commit.yml`）
- プルリクエスト時の高速チェック
- 基本的なリントとテスト実行
- フォーマットチェック

### トリガー条件
- **Push**: `main`, `develop` ブランチ
- **Pull Request**: `main`, `develop` ブランチへの PR

## テストの特徴

### モッキング戦略
- **外部API**: `responses` ライブラリでHTTPリクエストをモック
- **ファイルシステム**: `tempfile` と `patch` でファイル操作をモック
- **環境変数**: `patch.dict` で環境変数をモック
- **Google Cloud Services**: `MagicMock` でサービスクライアントをモック

### テストカテゴリ
1. **単体テスト**: 各関数・メソッドの動作確認
2. **統合テスト**: モジュール間の連携確認
3. **エラーハンドリング**: 例外処理の確認
4. **エッジケース**: 境界値・特殊ケースの確認

## 新しいテストの追加

### テストファイル作成
```python
import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.append('src')

from src.your_module import your_function

class TestYourModule:
    """your_moduleのテスト"""

    def test_your_function_success(self):
        """正常ケースのテスト"""
        result = your_function("test_input")
        assert result == "expected_output"

    def test_your_function_error(self):
        """エラーケースのテスト"""
        with pytest.raises(ValueError):
            your_function("invalid_input")
```

### テスト実行確認
```bash
# 新しいテストファイルの実行
pytest tests/test_your_module.py -v

# カバレッジの確認
pytest tests/ --cov=src --cov-report=term-missing
```

## ベストプラクティス

### テスト設計
1. **明確なテスト名**: 何をテストしているかが分かる名前
2. **独立性**: テスト間で状態を共有しない
3. **繰り返し可能**: 同じ結果が得られる
4. **高速実行**: 外部依存関係をモック化

### カバレッジ目標
- **最低**: 80%以上
- **推奨**: 90%以上
- **重要コード**: 100%を目指す

### CIでの品質保証
- 全テストが通過
- カバレッジ基準を満たす
- リント・型チェックをクリア
- セキュリティチェックをクリア
- フォーマットが統一されている

## トラブルシューティング

### よくある問題

#### インポートエラー
```bash
# パスの問題
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### モック関連
```python
# パッチのパスは呼び出し側を指定
@patch('src.main.fetch_tweets')  # ❌ 定義側
@patch('src.main.fetch_tweets')  # ✅ 呼び出し側
```

#### カバレッジが低い
```bash
# 対象外ファイルの確認
pytest tests/ --cov=src --cov-report=html
# htmlcov/index.html で詳細確認
```

## 関連ファイル

- `pytest.ini`: pytest設定
- `pyproject.toml`: ツール設定（black, isort, mypy等）
- `.flake8`: flake8設定
- `Makefile`: 開発用コマンド
- `requirements.txt`: テスト依存関係
