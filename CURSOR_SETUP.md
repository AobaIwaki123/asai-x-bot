# 浅井恋乃未 X Bot - Cursor開発環境セットアップ

## 概要
このドキュメントは、Cursor IDEを使用してASAI X Botを開発・実行するためのセットアップガイドです。

## 前提条件
- macOS環境
- Miniconda/Anacondaがインストール済み
- Cursor IDEがインストール済み

## 環境構築手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-username/asai-x-bot.git
cd asai-x-bot
```

### 2. conda環境の作成
```bash
# asai環境を作成（Python 3.12）
conda create -n asai python=3.12 -y

# 環境を有効化
conda activate asai

# 必要なパッケージをインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定
```bash
# example.envをコピーして.envファイルを作成
cp example.env .env

# .envファイルを編集して実際の値を設定
```

`.env`ファイルの内容例：
```env
X_BEARER_TOKEN=your_x_bearer_token_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
QUERY=(#浅井恋乃未) (from:sakurazaka46 OR from:sakura_joqr OR from:anan_mag OR from:Lemino_official)
```

### 4. Cursor設定

#### Python インタープリターの設定
1. Cursor で `Cmd+Shift+P` を押して コマンドパレットを開く
2. "Python: Select Interpreter" を選択
3. conda環境 `asai` のPythonパスを選択
   - 通常: `/opt/homebrew/Caskroom/miniconda/base/envs/asai/bin/python`

#### settings.jsonの設定
Cursorの設定ファイル（`.vscode/settings.json`）に以下を追加：

```json
{
    "python.defaultInterpreterPath": "/opt/homebrew/Caskroom/miniconda/base/envs/asai/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "terminal.integrated.defaultProfile.osx": "zsh",
    "terminal.integrated.profiles.osx": {
        "zsh": {
            "path": "zsh",
            "args": ["-l"]
        }
    },
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

## 実行方法

### ターミナルから実行
```bash
# conda環境を有効化
conda activate asai

# プロジェクトディレクトリに移動
cd /Users/iwakiaoiyou/asai-x-bot

# スクリプトを実行
cd src && python run.py
```

### Cursorの統合ターミナルから実行
1. Cursor内で `Ctrl+` ` ` （バッククォート）を押してターミナルを開く
2. 自動的にconda環境が有効化されることを確認
3. 以下のコマンドを実行：
```bash
cd src && python run.py
```

## デバッグ設定

`.vscode/launch.json`を作成してデバッグ設定を追加：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: ASAI Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/run.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "python": "/opt/homebrew/Caskroom/miniconda/base/envs/asai/bin/python"
        },
        {
            "name": "Python: Debug Main Module",
            "type": "python",
            "request": "launch",
            "module": "src.main",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "python": "/opt/homebrew/Caskroom/miniconda/base/envs/asai/bin/python"
        }
    ]
}
```

## プロジェクト構造

```
asai-x-bot/
├── .env                    # 環境変数（作成必要）
├── .vscode/
│   ├── settings.json      # Cursor設定
│   └── launch.json        # デバッグ設定
├── example.env            # 環境変数のテンプレート
├── requirements.txt       # Python依存関係
├── since_id.txt          # 実行状態管理ファイル
├── README.md             # プロジェクト説明
├── CURSOR_SETUP.md       # このファイル
└── src/
    ├── __init__.py       # パッケージ初期化
    ├── config.py         # 設定管理
    ├── utils.py          # ユーティリティ関数
    ├── discord_client.py # Discord関連機能
    ├── x_api_client.py   # X API関連機能
    ├── main.py           # メイン処理
    ├── run.py            # エントリーポイント
    ├── README.md         # ソースコード説明
    └── asai-radar.py.backup # 元ファイルのバックアップ
```

## 開発時のTips

### 1. 自動フォーマット
- `black`でコードを自動整形
- 保存時に自動実行される設定

### 2. リンティング
- `flake8`でコード品質をチェック
- 問題がある箇所がハイライトされる

### 3. モジュール開発
各モジュールを個別にテスト：
```python
# config.pyのテスト
from src.config import validate_env_vars
result = validate_env_vars()
print(result)

# utils.pyのテスト
from src.utils import load_since_id
since_id = load_since_id()
print(since_id)
```

## トラブルシューティング

### conda環境が認識されない場合
```bash
# conda環境のパスを確認
conda info --envs

# 正しいパスをCursorに設定
# 例: /opt/homebrew/Caskroom/miniconda/base/envs/asai/bin/python
```

### モジュールが見つからない場合
```bash
# PYTHONPATHを設定
export PYTHONPATH="${PYTHONPATH}:/Users/iwakiaoiyou/asai-x-bot/src"

# または、プロジェクトルートから実行
cd /Users/iwakiaoiyou/asai-x-bot
python -m src.run
```

### レート制限エラーの場合
- X APIのレート制限に達した状態
- 約8分後に自動的にリセットされる
- 正常な動作なので待機すること

## 定期実行設定（オプション）

### cronでの定期実行
```bash
# crontabを編集
crontab -e

# 5分おきに実行する例
*/5 * * * * cd /Users/iwakiaoiyou/asai-x-bot && /opt/homebrew/Caskroom/miniconda/base/envs/asai/bin/python src/run.py >> logs/bot.log 2>&1
```

### ログディレクトリの作成
```bash
mkdir logs
```

これで、Cursor IDEを使用したASAI X Botの開発環境が完了です。
