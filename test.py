import openai
from openai import OpenAI

# OpenAIのAPIキーをセットする
client = OpenAI(api_key="")

def chat_with_gpt(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは吉田松陰と同じ人格を持ちます"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    user_input = "やっぱりイケメンといえばオビ=ワン・ケノービですか"
    answer = chat_with_gpt(user_input)
    print("ChatGPTの応答:", answer)
