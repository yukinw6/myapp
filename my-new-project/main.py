import os
from flask import Flask, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
import markdown
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv(dotenv_path=".env", override=True)  # ← 明示的に

# Flaskアプリの初期化
app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション暗号化用の秘密鍵（固定化してもOK）
app.config["TEMPLATES_AUTO_RELOAD"] = True

# DB設定
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "myapp_db")
DB_USER = os.environ.get("DB_USER", "myapp_user")
DB_PASS = os.environ.get("DB_PASS", "myapp_pass")

# SQLAlchemyのDB接続URL (PostgreSQL)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# 環境変数からAPIキー取得
api_key = os.getenv("OPENAI_API_KEY")


# DBモデル定義
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_text = db.Column(db.Text)
    ai_response = db.Column(db.Text)


# 初期化用（初回だけ叩く）
@app.route("/initdb")
def initdb():
    db.create_all()
    return "DB initialized!"


# 履歴テーブル用のHTML
@app.route("/logs")
def view_logs():
    logs = ChatLog.query.order_by(ChatLog.id.desc()).limit(20).all()
    return render_template("logs.html", logs=logs)


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
                max_tokens=2000,
                temperature=0.7,
            )
            response_text = response.choices[0].message.content.strip()
            response_html = markdown.markdown(response_text)  # ← ここで変換

            # 会話履歴に追加（Markdown対応）
            session["history"].append({"user": full_prompt, "assistant": response_html})
            session.modified = True

            # DBにも保存
            log = ChatLog(user_text=full_prompt, ai_response=response_text)
            db.session.add(log)
            db.session.commit()

    # 直近の履歴（DB）も表示したければ：
    logs = ChatLog.query.order_by(ChatLog.id.desc()).limit(10).all()

    return render_template(
        "index.html", response_text=response_html, history=session["history"]
    )


if __name__ == "__main__":
    app.run(debug=True)
