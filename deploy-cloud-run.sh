#!/bin/bash

# ASAI X Bot Cloud Run デプロイメントスクリプト（完全版）

set -e

# 色付きの出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルプメッセージ
show_help() {
    echo -e "${GREEN}ASAI X Bot Cloud Run デプロイメントスクリプト${NC}"
    echo ""
    echo "使用方法:"
    echo "  $0 [オプション]"
    echo ""
    echo "オプション:"
    echo "  -n, --name SERVICE_NAME    カスタムサービス名を指定 (デフォルト: asai-x-bot)"
    echo "  -q, --query QUERY          カスタム検索クエリを指定"
    echo "  -h, --help                 このヘルプメッセージを表示"
    echo ""
    echo "環境変数:"
    echo "  PROJECT_ID                 GCPプロジェクトID (必須)"
    echo "  REGION                     デプロイリージョン (デフォルト: asia-northeast1)"
    echo ""
    echo "例:"
    echo "  # デフォルトのクエリでデプロイ"
    echo "  $0"
    echo ""
    echo "  # カスタムクエリで別サービスとしてデプロイ"
    echo "  $0 --name asai-x-bot-custom --query '(#浅井恋乃未) (from:custom_account)'"
    echo ""
    echo "  # 環境変数を使用"
    echo "  export PROJECT_ID=my-project"
    echo "  $0 --name asai-x-bot-news --query '(#浅井恋乃未) (news OR ニュース)'"
    exit 0
}

# デフォルト値
SERVICE_NAME="asai-x-bot"
CUSTOM_QUERY=""
DEFAULT_QUERY="(#浅井恋乃未) (from:sakurazaka46 OR from:sakura_joqr OR from:anan_mag OR from:Lemino_official)"

# 引数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        -q|--query)
            CUSTOM_QUERY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}エラー: 不明なオプション: $1${NC}"
            echo "ヘルプを表示するには '$0 --help' を実行してください"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=== ASAI X Bot Cloud Run デプロイメント ===${NC}"

# 必要な変数の確認
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}エラー: PROJECT_ID環境変数が設定されていません${NC}"
    echo "export PROJECT_ID=your-gcp-project-id"
    exit 1
fi

if [ -z "$REGION" ]; then
    REGION="asia-northeast1"
    echo -e "${YELLOW}REGION が設定されていないため、デフォルトの asia-northeast1 を使用します${NC}"
fi

# クエリの決定
if [ -n "$CUSTOM_QUERY" ]; then
    QUERY="$CUSTOM_QUERY"
    echo -e "${BLUE}カスタムクエリを使用します${NC}"
else
    QUERY="$DEFAULT_QUERY"
    echo -e "${BLUE}デフォルトクエリを使用します${NC}"
fi

IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${GREEN}プロジェクト ID: $PROJECT_ID${NC}"
echo -e "${GREEN}リージョン: $REGION${NC}"
echo -e "${GREEN}サービス名: $SERVICE_NAME${NC}"
echo -e "${GREEN}検索クエリ: $QUERY${NC}"

# 1. gcloud の設定確認
echo -e "\n${YELLOW}1. gcloud 設定の確認...${NC}"
gcloud config set project "$PROJECT_ID"

# 1.5. gcloud 認証の確認
echo -e "\n${YELLOW}1.5. gcloud 認証の確認...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}エラー: gcloud にログインしていません${NC}"
    echo "gcloud auth login を実行してください"
    exit 1
fi
echo -e "${GREEN}gcloud 認証済み: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')${NC}"

# 2. 必要なAPIの有効化
echo -e "\n${YELLOW}2. 必要なAPIの有効化...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable secretmanager.googleapis.com

# 3. Dockerイメージのビルド（アーキテクチャ指定）
echo -e "\n${YELLOW}3. Dockerイメージのビルド...${NC}"
echo -e "${YELLOW}   Cloud Run用にlinux/amd64プラットフォームでビルドします${NC}"
docker build --platform linux/amd64 -t "$IMAGE_NAME" .

# 3.5. Docker認証の設定
echo -e "\n${YELLOW}3.5. Docker認証の設定...${NC}"
gcloud auth configure-docker gcr.io

# 4. Dockerイメージのプッシュ
echo -e "\n${YELLOW}4. Dockerイメージのプッシュ...${NC}"
docker push "$IMAGE_NAME"

# 5. シークレットの作成（存在しない場合のみ）
echo -e "\n${YELLOW}5. シークレットの確認/作成...${NC}"

# サービス名ベースのシークレット名を生成
X_BEARER_SECRET="${SERVICE_NAME}-x-bearer-token"
DISCORD_WEBHOOK_SECRET="${SERVICE_NAME}-discord-webhook"
SINCE_ID_SECRET="${SERVICE_NAME}-since-id"

# X_BEARER_TOKEN シークレット
if ! gcloud secrets describe "$X_BEARER_SECRET" >/dev/null 2>&1; then
    echo -e "${YELLOW}X_BEARER_TOKEN シークレットを作成してください:${NC}"
    echo "実際のトークンを入力してください:"
    read -rs x_token
    echo "$x_token" | gcloud secrets create "$X_BEARER_SECRET" --data-file=-
    echo -e "${GREEN}X_BEARER_TOKEN シークレットを作成しました${NC}"
else
    echo -e "${GREEN}X_BEARER_TOKEN シークレットは既に存在します${NC}"
fi

# DISCORD_WEBHOOK_URL シークレット
if ! gcloud secrets describe "$DISCORD_WEBHOOK_SECRET" >/dev/null 2>&1; then
    echo -e "${YELLOW}DISCORD_WEBHOOK_URL シークレットを作成してください:${NC}"
    echo "Discord Webhook URLを入力してください:"
    read -r discord_url
    echo "$discord_url" | gcloud secrets create "$DISCORD_WEBHOOK_SECRET" --data-file=-
    echo -e "${GREEN}DISCORD_WEBHOOK_URL シークレットを作成しました${NC}"
else
    echo -e "${GREEN}DISCORD_WEBHOOK_URL シークレットは既に存在します${NC}"
fi

# SINCE_ID シークレット（初期値は空文字）
if ! gcloud secrets describe "$SINCE_ID_SECRET" >/dev/null 2>&1; then
    echo -e "${YELLOW}SINCE_ID シークレットを作成中...${NC}"
    echo "" | gcloud secrets create "$SINCE_ID_SECRET" --data-file=-
    echo -e "${GREEN}SINCE_ID シークレットを作成しました（初期値は空）${NC}"
else
    echo -e "${GREEN}SINCE_ID シークレットは既に存在します${NC}"
fi

# 5.5. Cloud Runサービスアカウントの権限設定（プロジェクト番号を使用）
echo -e "\n${YELLOW}5.5. Cloud Runサービスアカウントの権限設定...${NC}"
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
echo -e "${YELLOW}プロジェクト番号: $PROJECT_NUMBER${NC}"

# Cloud RunのデフォルトサービスアカウントにSecret Manager Secret Accessor権限を付与
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
echo -e "${GREEN}Cloud Runサービスアカウントに権限を付与しました${NC}"

# 6. Cloud Run サービスのデプロイ
echo -e "\n${YELLOW}6. Cloud Runサービスのデプロイ...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --no-allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 900 \
    --concurrency 1 \
    --max-instances 1 \
    --set-env-vars "QUERY=$QUERY" \
    --set-env-vars "SINCE_ID_FILE=/tmp/data/since_id.txt" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-secrets "X_BEARER_TOKEN=$X_BEARER_SECRET:latest" \
    --set-secrets "DISCORD_WEBHOOK_URL=$DISCORD_WEBHOOK_SECRET:latest"

echo -e "${GREEN}Cloud Runサービスのデプロイが完了しました${NC}"

# 7. Cloud Run URLの取得
echo -e "\n${YELLOW}7. Cloud Run URLの取得...${NC}"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")
echo -e "${GREEN}Cloud Run URL: $SERVICE_URL${NC}"

# 8. Scheduler用Service Accountの作成とIAM設定
echo -e "\n${YELLOW}8. Scheduler用Service Accountの設定...${NC}"
SA_NAME="${SERVICE_NAME}-scheduler"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Service Accountが存在しない場合は作成
if ! gcloud iam service-accounts describe "$SA_EMAIL" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$SA_NAME" \
        --display-name="$SERVICE_NAME Scheduler Service Account"
    echo -e "${GREEN}Scheduler用Service Accountを作成しました${NC}"
else
    echo -e "${GREEN}Scheduler用Service Accountは既に存在します${NC}"
fi

# Cloud Run Invoker権限を付与
gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.invoker" \
    --region="$REGION"
echo -e "${GREEN}Scheduler用Service AccountにCloud Run Invoker権限を付与しました${NC}"

# 9. Cloud Schedulerジョブの作成
echo -e "\n${YELLOW}9. Cloud Schedulerジョブの作成...${NC}"
JOB_NAME="${SERVICE_NAME}-schedule"

# 既存のジョブを削除（存在する場合）
if gcloud scheduler jobs describe "$JOB_NAME" --location="$REGION" >/dev/null 2>&1; then
    echo -e "${YELLOW}既存のSchedulerジョブを削除しています...${NC}"
    gcloud scheduler jobs delete "$JOB_NAME" --location="$REGION" --quiet
fi

# 新しいジョブを作成
gcloud scheduler jobs create http "$JOB_NAME" \
    --location="$REGION" \
    --schedule="0 9 * * *" \
    --time-zone="Asia/Tokyo" \
    --uri="$SERVICE_URL" \
    --http-method=POST \
    --oidc-service-account-email="$SA_EMAIL" \
    --description="$SERVICE_NAME - 1日1回の定期実行"

echo -e "${GREEN}Cloud Schedulerジョブを作成しました${NC}"

# 完了メッセージ
echo -e "\n${GREEN}=== デプロイメント完了! ===${NC}"
echo -e "${GREEN}Cloud Run URL: $SERVICE_URL${NC}"
echo -e "${GREEN}Cloud Scheduler ジョブ: $JOB_NAME${NC}"
echo -e "${GREEN}実行頻度: 1日1回（午前9時）${NC}"
echo -e "${GREEN}次回実行: 翌日午前9時${NC}"

echo -e "\n${YELLOW}=== 設定確認 ===${NC}"
echo -e "${YELLOW}デプロイされたサービス:${NC}"
echo "  - Docker Image: $IMAGE_NAME (linux/amd64)"
echo "  - Cloud Run Service: $SERVICE_NAME"
echo "  - Region: $REGION"
echo "  - Query: $QUERY"
echo "  - Service Account: $PROJECT_NUMBER-compute@developer.gserviceaccount.com"
echo "  - Scheduler Service Account: $SA_EMAIL"

echo -e "\n${YELLOW}使用しているシークレット:${NC}"
echo "  - X Bearer Token: $X_BEARER_SECRET"
echo "  - Discord Webhook: $DISCORD_WEBHOOK_SECRET"
echo "  - Since ID: $SINCE_ID_SECRET"

echo -e "\n${YELLOW}=== トラブルシューティング ===${NC}"
echo -e "${YELLOW}ログの確認:${NC}"
echo "gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME' --limit=50 --format='table(timestamp,textPayload)'"

echo -e "\n${YELLOW}Schedulerジョブの手動実行:${NC}"
echo "gcloud scheduler jobs run $JOB_NAME --location=$REGION"

echo -e "\n${YELLOW}Cloud Runサービスの詳細:${NC}"
echo "gcloud run services describe $SERVICE_NAME --region=$REGION"

echo -e "\n${GREEN}デプロイメントが正常に完了しました！${NC}"
