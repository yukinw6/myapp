# ベースイメージ選択 (Python3.9など)
FROM python:3.9-slim

# 作業ディレクトリ
WORKDIR /app

# 依存ライブラリを先にコピー＆インストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . /app/

# .env ファイルもコンテナにコピーする（COPY . の前でもOK）
COPY .env /app/

# 環境変数 (後述のDB接続用)
# ENV OPENAI_API_KEY=<...>  # 環境によっては .env 使う方法もOK

# Flaskを起動するコマンド (gunicorn推奨)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]