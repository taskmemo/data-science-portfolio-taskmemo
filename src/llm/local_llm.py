import dspy
import requests
import os

OLLAMA_API = os.getenv("OLLAMA_API_BASE", "http://localhost:11434") #サーバーのエンドポイントは異なる可能性がある。
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi3:mini") # モデルは未設定

lm = dspy.LM(f"ollama/{MODEL_NAME}", api_base=OLLAMA_API)
dspy.configure(lm=lm)


def generate_recommendations(cafes, top_n: int = 5):
    """LLMを用いておすすめカフェコメントを生成"""
    cafes_text = "\n".join([
        f"{i+1}. {c['name']}（評価: {c.get('rating', '?')} / {c.get('user_ratings_total', 0)}件） - {c['address']}"
        for i, c in enumerate(cafes[:top_n])
    ])

    prompt = f"""
    以下は近くのカフェ情報です。地元の案内人として、雰囲気や立地を踏まえたおすすめコメントを日本語で簡潔に5行以内で作成してください。

    {cafes_text}
    """

    response = lm(prompt)
    return response.output_text.strip()

# dspyによる実装ができていないので、修正する。