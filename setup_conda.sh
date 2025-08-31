#!/bin/bash

# ASAI X Bot - Conda環境セットアップスクリプト

echo "🚀 ASAI X Bot conda環境をセットアップしています..."

# conda環境の存在確認
if conda env list | grep -q "^asai "; then
    echo "✅ conda環境 'asai' は既に存在します"
else
    echo "📦 conda環境 'asai' を作成しています..."
    conda create -n asai python=3.12 -y
    if [ $? -eq 0 ]; then
        echo "✅ conda環境 'asai' を作成しました"
    else
        echo "❌ conda環境の作成に失敗しました"
        exit 1
    fi
fi

# conda環境を有効化
echo "🔄 conda環境 'asai' を有効化しています..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate asai

# 依存関係をインストール
echo "📥 依存関係をインストールしています..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
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
