# My OpenAI Web App

## 概要
このWebアプリはOpenAI APIを使用してChatGPTとの質疑応答を実現します。

## 環境設定

1. **依存関係のインストール**
    ```bash
    pip install -r requirements.txt
    ```

2. **環境変数の設定**
    プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の内容を記述します。
    ```dotenv
    OPENAI_API_KEY=your_openai_api_key_here
    ```

3. **アプリケーションの起動**
    ```bash
    python app.py
    ```

## セキュリティ

- **APIキーは絶対に公開しないでください。**
- `.env` ファイルは `.gitignore` に追加されています。