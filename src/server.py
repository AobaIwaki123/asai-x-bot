#!/usr/bin/env python3
"""
Cloud Run用のHTTPサーバー
Cloud SchedulerからのHTTPリクエストを受け取ってボットを実行する
"""

import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from .main import main

logger = logging.getLogger(__name__)


class BotHandler(BaseHTTPRequestHandler):
    """HTTP リクエストハンドラー"""

    def do_GET(self):
        """GET リクエストの処理"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ASAI X Bot is running")

    def do_POST(self):
        """POST リクエストの処理 - ボットを実行"""
        try:
            logger.info("Cloud Schedulerからのリクエストを受信")
            main()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        except Exception as e:
            logger.error(f"ボット実行中にエラーが発生: {e}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_response = f'{{"status": "error", "message": "{str(e)}"}}'
            self.wfile.write(error_response.encode())

    def log_message(self, format, *args):
        """アクセスログを標準ログに統合"""
        logger.info(f"HTTP {format % args}")


def run_server():
    """HTTPサーバーを起動"""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("", port), BotHandler)
    logger.info(f"サーバーをポート {port} で起動")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("サーバーを停止")
        server.server_close()


if __name__ == "__main__":
    run_server()
