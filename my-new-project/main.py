from flask import Flask, request, render_template, session
from openai import OpenAI
import markdown
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 環境変数からAPIキー取得
api_key = os.getenv("OPENAI_API_KEY")

# Flaskアプリの初期化
app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション暗号化用の秘密鍵（固定化してもOK）

# OpenAIクライアントの初期化 ← ここがポイント！
client = OpenAI(api_key=api_key)
# print(f"API KEY = {api_key}")


@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []

    response_text = None
    response_html = None

    if request.method == "POST":
        genre = request.form.get("genre", "").strip()
        user_input = request.form.get("user_input", "")
        # 両方を組み合わせてプロンプトに渡す
        full_prompt = f"ジャンル: {genre}\n要望: {user_input}"
        if genre or user_input:
            # 会話の履歴を整形してOpenAIに投げる
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI that recommends movies and books. Provide suggestions based on user preferences.",
                }
            ]
            # 既存の履歴をmessagesに追加
            for h in session["history"]:
                messages.append({"role": "user", "content": h["user"]})
                messages.append({"role": "assistant", "content": h["assistant"]})

            # 今回のユーザー入力
            messages.append({"role": "user", "content": full_prompt})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            response_text = response.choices[0].message.content.strip()
            response_html = markdown.markdown(response_text)  # ← ここで変換

            # 会話履歴に追加（Markdown対応）
            session["history"].append({"user": full_prompt, "assistant": response_html})
            session.modified = True

    return render_template(
        "index.html", response_text=response_html, history=session["history"]
    )


if __name__ == "__main__":
    app.run(debug=True)
