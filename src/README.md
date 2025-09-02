# ASAI X Bot - ファイル構造

## 概要
元の`asai-radar.py`（298行）を以下のように分割し、保守性を向上させました。

## ファイル構成

### 1. `config.py` - 設定管理
- 環境変数の読み込みと検証
- X API用の設定値
- ログ設定

### 2. `utils.py` - ユーティリティ関数
- `since_id`の読み書き（Secret Manager + ローカルファイルフォールバック）
- Cloud Run環境自動判定
- データのインデックス化

### 3. `discord_client.py` - Discord関連
- Discord Webhookへの投稿
- ツイートのEmbed作成

### 4. `x_api_client.py` - X API関連
- X APIからのツイート取得
- レート制限の処理
- エラーハンドリング

### 5. `main.py` - メイン処理
- 全体の処理フロー制御
- 各モジュールの連携

### 6. `run.py` - エントリーポイント
- 直接実行用のスクリプト
- 元の`asai-radar.py`と同じ動作

## 使用方法

### 直接実行
```bash
cd src
python run.py
```

### モジュールとして使用
```python
from src.main import main
main()
```

## 利点

1. **保守性向上**: 各機能が独立したファイルに分離
2. **可読性向上**: ファイルサイズが適切な範囲に
3. **再利用性**: 個別の機能を他のプロジェクトで使用可能
4. **テスト容易性**: 各モジュールを個別にテスト可能
5. **拡張性**: 新機能の追加が容易
6. **永続化**: Secret Managerで状態管理がデプロイでリセットされない
7. **フォールバック**: ローカル開発時はファイルベースで動作

## Secret Manager 対応

### 環境判定
- Cloud Run環境: `K_SERVICE`環境変数で判定
- ローカル環境: ファイルベースの`since_id.txt`を使用

### フォールバック機構
1. Secret Managerへの接続を試行
2. 失敗時はローカルファイルにフォールバック
3. 開発と本番で同じコードで動作

### Secret Manager シークレット
- `asai-x-bot-since-id`: 最終処理ツイートIDの永続化
- 自動作成: シークレットが存在しない場合は自動で作成

## 元ファイル
元の`asai-radar.py`は`asai-radar.py.backup`としてバックアップ保存されています。
