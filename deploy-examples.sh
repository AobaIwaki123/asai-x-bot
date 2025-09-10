#!/bin/bash

# ASAI X Bot - デプロイ例

# 色付きの出力
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ASAI X Bot デプロイ例 ===${NC}"
echo -e "これらは ${YELLOW}./deploy-cloud-run.sh${NC} の使用例です"
echo ""

echo -e "${BLUE}1. デフォルトのクエリでデプロイ:${NC}"
echo "   export PROJECT_ID=your-project-id"
echo "   ./deploy-cloud-run.sh"
echo ""

echo -e "${BLUE}2. ニュース関連の投稿を監視:${NC}"
echo "   ./deploy-cloud-run.sh \\"
echo "     --name asai-x-bot-news \\"
echo "     --query '(#浅井恋乃未) (news OR ニュース OR 速報)'"
echo ""

echo -e "${BLUE}3. 特定のアカウントを追加で監視:${NC}"
echo "   ./deploy-cloud-run.sh \\"
echo "     --name asai-x-bot-extended \\"
echo "     --query '(#浅井恋乃未) (from:sakurazaka46 OR from:sakura_joqr OR from:anan_mag OR from:Lemino_official OR from:natalie_mu)'"
echo ""

echo -e "${BLUE}4. メディア付き投稿のみ監視:${NC}"
echo "   ./deploy-cloud-run.sh \\"
echo "     --name asai-x-bot-media \\"
echo "     --query '(#浅井恋乃未) has:media'"
echo ""

echo -e "${BLUE}5. 写真付き投稿のみ監視:${NC}"
echo "   ./deploy-cloud-run.sh \\"
echo "     --name asai-x-bot-photos \\"
echo "     --query '(#浅井恋乃未) has:images'"
echo ""

echo -e "${YELLOW}注意事項:${NC}"
echo "- 各デプロイは独立したサービスとして動作します"
echo "- サービスごとに個別のシークレットが作成されます"
echo "- 同じDiscord Webhookを共有することも、別々のチャンネルに送信することも可能です"
echo "- Cloud Schedulerのジョブ名は 'サービス名-schedule' になります"
echo ""

echo -e "${GREEN}詳細なヘルプ:${NC}"
echo "   ./deploy-cloud-run.sh --help"