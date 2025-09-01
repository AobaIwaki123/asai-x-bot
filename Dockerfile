# Python 3.12 slim image
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ ./src/

# since_id.txtを保存するディレクトリを作成
RUN mkdir -p /tmp/data

# 環境変数設定
ENV PYTHONPATH=/app/src
ENV SINCE_ID_FILE=/tmp/data/since_id.txt

# ポート設定
EXPOSE 8080

# アプリケーションの実行
CMD ["python", "/app/src/server.py"]
