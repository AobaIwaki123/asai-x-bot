# Linter・Formatter統一移行ドキュメント

## 移行概要

プロジェクトのlinterとformatterをRuffに統一しました。これにより、開発ツールが簡潔になり、実行速度が向上します。

## 変更内容

### 1. 削除されたツール

以下のツールをRuffに統一して削除しました：

- **black** → `ruff format` に統一
- **flake8** → `ruff check` に統一
- **isort** → `ruff check --select I` に統一
- **mypy** → ruffの型チェックルールに統一（オプションで復活可能）

### 2. 維持されたツール

以下のツールは特定の用途で継続使用：

- **bandit** → セキュリティチェック専用
- **safety** → 依存関係の脆弱性チェック専用
- **pytest** → テスト実行
- **coverage** → カバレッジ測定

### 3. 設定ファイルの変更

#### `pyproject.toml`
- `[tool.black]`, `[tool.isort]`, `[tool.mypy]` セクションを削除
- `[tool.ruff]` セクションを拡張：
  - より多くのlintルールを追加
  - プロジェクト固有の無視ルールを設定
  - フォーマット設定を詳細化

#### `requirements.txt`
- `black`, `flake8`, `mypy`, `isort` を削除
- `ruff>=0.6.0` のバージョンを更新

#### `Makefile`
- `lint`: ruffのみ実行
- `format`: ruffのフォーマットと自動修正
- `format-check`: ruffのフォーマットチェック
- `type-check`: ruffの型関連ルールに簡素化
- `all` と `ci` からmypy依存を削除

## 新しいコマンド

### 基本的な使用方法

```bash
# lint実行
make lint
# または
ruff check src tests

# フォーマット実行
make format
# または
ruff format src tests
ruff check --fix src tests

# フォーマットチェック（CI用）
make format-check
# または
ruff format --check src tests
ruff check src tests

# 全体チェック
make all
```

### ruffの直接実行

```bash
# 基本チェック
ruff check .

# 自動修正付き
ruff check --fix .

# フォーマット
ruff format .

# 特定ルールのみ
ruff check --select F,E src/
```

## Ruffの設定詳細

### 有効化されたルールセット

- **E/W**: pycodestyle（PEP 8準拠）
- **F**: pyflakes（未使用変数、importエラーなど）
- **I**: isort（import順序）
- **B**: flake8-bugbear（バグの原因となりやすいパターン）
- **C4**: flake8-comprehensions（リスト内包表記の改善）
- **UP**: pyupgrade（Python新機能への更新提案）
- **N**: pep8-naming（命名規則）
- **S**: flake8-bandit（セキュリティ）
- **T20**: flake8-print（print文チェック）
- **PT**: flake8-pytest-style（pytest スタイル）
- **Q**: flake8-quotes（引用符スタイル）
- **RET**: flake8-return（return文の改善）
- **SIM**: flake8-simplify（コード簡素化）
- **TID**: flake8-tidy-imports（import整理）
- **ARG**: flake8-unused-arguments（未使用引数）
- **ERA**: eradicate（コメントアウトされたコード）
- **PL**: pylint（総合的なコード品質）
- **TRY**: tryceratops（例外処理のベストプラクティス）

### 無視されるルール

プロジェクトの性質上、以下のルールを無視設定：

- **E501**: 行長制限（formatterが処理）
- **S101**: assert使用（テストで必要）
- **S104**: 全インターフェースbind（Cloud Run用）
- **S105**: ハードコードされたパスワード（nosecコメントで管理）
- **PLR0913**: 引数多数（必要な場合がある）
- **PLR2004**: マジックナンバー（設定値で正当）
- **TRY003**: 例外メッセージ（現在のパターンで問題なし）

## 移行後の利点

### 1. 実行速度向上
- Rustで書かれたRuffはPythonツールより大幅に高速
- CI/CDでの実行時間短縮

### 2. 設定統一
- 1つのツールで複数機能を統合
- 設定ファイルの簡素化

### 3. メンテナンス性向上
- 依存関係の削減
- バージョン管理の簡素化

### 4. 機能向上
- より多くのlintルールを有効化
- 自動修正機能の充実

## 困った時の対処法

### よくある問題

1. **新しいlintエラーが大量発生**
   ```bash
   # 自動修正で解決可能な場合
   ruff check --fix .

   # 特定ルールを一時的に無視
   ruff check --ignore E501,F401 .
   ```

2. **フォーマット済みファイルが意図と異なる**
   ```bash
   # 設定確認
   ruff format --check --diff .

   # 元に戻す（Git使用）
   git checkout -- <file>
   ```

3. **旧ツールコマンドの置き換え**
   ```bash
   # 旧: black src/
   ruff format src/

   # 旧: flake8 src/
   ruff check src/

   # 旧: isort src/
   ruff check --select I --fix src/
   ```

## 今後の計画

### オプション機能

- 必要に応じてmypyを復活（型チェック強化）
- 新しいruffルールセットの随時導入
- CI/CDでのruff cache活用検討

### 移行完了の確認

```bash
# 全体チェック
make ci

# カバレッジ付きテスト
make test

# セキュリティチェック
make security
```

---

**移行完了日**: 2025年09月02日
**Ruffバージョン**: 0.6.0以上
**対象プロジェクト**: ASAI X Bot
