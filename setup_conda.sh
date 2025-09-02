#!/bin/bash

# ASAI X Bot - Conda環境セットアップスクリプト

echo "🚀 ASAI X Bot conda環境をセットアップしています..."

# Anaconda Terms of Service acceptance (non-interactive)
echo "📄 Anacondaの利用規約(TOS)を受諾しています..."
if conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r; then
    echo "✅ TOSの受諾が完了しました（または既に受諾済み）"
else
    echo "❌ TOSの受諾に失敗しました"
    echo "   手動で以下を実行してください:"
    echo "   conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main"
    echo "   conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r"
    exit 1
fi

# conda環境の存在確認
if conda env list | grep -q "^asai "; then
    echo "✅ conda環境 'asai' は既に存在します"
else
    echo "📦 conda環境 'asai' を作成しています..."
    if conda create -n asai python=3.12 -y; then
        echo "✅ conda環境 'asai' を作成しました"
    else
        echo "❌ conda環境の作成に失敗しました"
        exit 1
    fi
fi

# conda環境を有効化
echo "🔄 conda環境 'asai' を有効化しています..."
# shellcheck source=/dev/null
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate asai

# 依存関係をインストール
echo "📥 依存関係をインストールしています..."
if pip install -r requirements.txt; then
    echo "✅ 依存関係のインストールが完了しました"
else
    echo "❌ 依存関係のインストールに失敗しました"
    exit 1
fi

# .envファイルの確認
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません"
    echo "📝 example.envをコピーして.envファイルを作成してください:"
    echo "   cp example.env .env"
    echo "   その後、.envファイルを編集して実際の値を設定してください"
else
    echo "✅ .envファイルが見つかりました"
fi

echo ""
echo "🎉 セットアップが完了しました！"
echo ""
echo "📋 次のステップ:"
echo "1. Cursorで Python インタープリターを設定:"
echo "   - Cmd+Shift+P → 'Python: Select Interpreter'"
echo "   - $(conda info --base)/envs/asai/bin/python を選択"
echo ""
echo "2. ボットを実行:"
echo "   conda activate asai"
echo "   cd src && python run.py"
echo ""
echo "3. Cursorでデバッグ実行:"
echo "   - F5キーを押して 'Python: ASAI Bot' を選択"
