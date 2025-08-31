# 浅井恋乃未 X Bot

## 概要

`#浅井恋乃未`がついたポストをX（旧Twitter）から監視し、Discordに自動転送するPython製のbotです。

## 機能

- X APIを使用したリアルタイム投稿監視
- 特定のハッシュタグとアカウントからの投稿を自動検出
- Discord Webhookを使用した自動転送
- 重複投稿の防止（since_id管理）
- ログ出力による動作状況の可視化

## 監視対象

以下のクエリで投稿を監視します：

```
(#浅井恋乃未) (from:sakurazaka46 OR from:sakura_joqr OR from:anan_mag OR from:Lemino_official)
```

- `#浅井恋乃未` ハッシュタグが含まれる投稿
- 以下のアカウントからの投稿：
  - `@sakurazaka46` (櫻坂46公式)
  - `@sakura_joqr` (JOQR)
  - `@anan_mag` (anan編集部)
  - `@Lemino_official` (Lemino公式)

## 必要環境

- Python 3.12以上
- X API Bearer Token
- Discord Webhook URL

## インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd asai-x-bot
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

## 設定

1. 環境変数ファイルを作成
```bash
cp example.env .env
```

2. `.env`ファイルを編集し、必要な値を設定
```env
X_BEARER_TOKEN=your_x_bearer_token_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
QUERY=(#浅井恋乃未) (from:sakurazaka46 OR from:sakura_joqr OR from:anan_mag OR from:Lemino_official)
```

### 環境変数の説明

- `X_BEARER_TOKEN`: X APIのBearer Token（[X Developer Portal](https://developer.twitter.com/)で取得）
- `DISCORD_WEBHOOK_URL`: DiscordチャンネルのWebhook URL
- `QUERY`: 監視する検索クエリ（必要に応じてカスタマイズ可能）

## 使用方法

### 基本的な実行

```bash
python src/asai-rader.py
```

### 定期実行（cron使用例）

```bash
# 5分ごとに実行
*/5 * * * * cd /path/to/asai-x-bot && python src/asai-rader.py
```

### バックグラウンド実行

```bash
nohup python src/asai-rader.py > bot.log 2>&1 &
```

## ファイル構成

```
asai-x-bot/
├── README.md              # このファイル
├── requirements.txt       # Python依存関係
├── example.env           # 環境変数テンプレート
├── since_id.txt          # 最後に処理した投稿ID（自動生成）
└── src/
    ├── __init__.py
    └── asai-rader.py     # メインスクリプト
```

## 動作の仕組み

1. **初期化**: 環境変数を読み込み、X APIとDiscord Webhookの設定を確認
2. **状態管理**: `since_id.txt`から前回処理した投稿IDを読み込み
3. **投稿検索**: X APIを使用して新しい投稿を検索
4. **重複チェック**: 既に処理済みの投稿はスキップ
5. **Discord転送**: 新しい投稿をDiscord Webhookで転送
6. **状態更新**: 処理した投稿IDを保存
