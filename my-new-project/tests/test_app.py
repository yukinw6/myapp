# tests/test_app.py

import sys
import os
import pytest
from dotenv import load_dotenv
import main  # 'main' モジュールをインポート

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app  # 'app' から 'main' に変更


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"  # テスト用の秘密鍵を設定
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_index_get(client):
    """GETリクエストでトップページが正しく表示されるか確認"""
    response = client.get("/")
    assert response.status_code == 200
    # 必要に応じて具体的な内容を確認
    # assert b'Expected Content' in response.data


def test_index_post(client, monkeypatch):
    """POSTリクエストでOpenAI APIが正しく動作するか確認"""

    # モック関数を定義してOpenAI API呼び出しをシミュレート
    class MockResponse:
        def __init__(self, content):
            self.choices = [MockChoice(content)]

    class MockChoice:
        def __init__(self, content):
            self.message = MockMessage(content)

    class MockMessage:
        def __init__(self, content):
            self.content = content

    def mock_create(*args, **kwargs):
        return MockResponse("Mocked response from OpenAI!")

    # モック先を Flask 側の client に合わせる！
    monkeypatch.setattr(main.client.chat.completions, "create", mock_create)

    # POSTデータを準備
    data = {"user_input": "Test input"}

    response = client.post("/", data=data)
    assert response.status_code == 200

    # ★ ここで HTML 全体をちゃんと表示する
    html = response.data.decode("utf-8")
    print("\n========= レスポンスHTML =========")
    print(html)
    print("========= END =========\n")

    # 元のアサーション
    assert "Mocked response from OpenAI!" in html


def test_no_user_input(client):
    """POSTリクエストでユーザー入力がない場合の動作確認"""
    data = {"user_input": ""}
    response = client.post("/", data=data)
    assert response.status_code == 200
    # 期待される動作に基づいてアサートを追加
    # 例: エラーメッセージが表示されることを確認
