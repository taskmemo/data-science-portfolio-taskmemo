"""
このスクリプトは、DSPyで定義したSignatureやModuleを実行し、
OllamaのローカルLLMにリクエストして応答を取得する。
"""

import requests
import os
import hashlib
from src.dspy.sigunatures import CafeRecommendation
from src.api.google_maps import load_config
from src.utils.cache_manager import CacheManager

# load configuration for dspy
config = load_config()
OLLAMA_API = config["llm"].get("endpoint", "http://localhost:11434/api/generate")
OLLAMA_MODEL = config["llm"].get("model", "gemma3:12b")

cache = CacheManager()

def run_local_model(prompt: str, model: str = None, temperature: float = 0.7, max_tokens: int = 512) -> str:
    """ローカルLLM（Ollama）にプロンプトを投げて応答を取得する"""
    model = model or OLLAMA_MODEL

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    try:
        response = requests.post(
            OLLAMA_API,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

        # ✅ Ollamaのレスポンス形式に対応
        return data.get("response", "").strip()
    
    except requests.RequestException as e:
        print(f"❌ ローカルLLMリクエスト失敗: {e}")
        return "LLMリクエストに失敗しました。Ollamaが起動しているか確認してください。"
    except Exception as e:
        print(f"❌ ローカルLLM応答解析失敗: {e}")
        return "LLM応答の解析に失敗しました。"

def generate_text(prompt, model_name="local-llm", ttl_hours=24):
    """
    prompt と model_name からハッシュを作り、llm_cache を参照して結果を返す。
    キャッシュがなければ簡易生成（決定論的）を行い、保存して返す。
    """
    key_src = f"{model_name}|{prompt}"
    prompt_hash = hashlib.sha256(key_src.encode()).hexdigest()

    cached = cache.get_llm_cache(model_name, prompt_hash)
    if cached:
        return cached

    # 簡易決定論的生成（ここを実環境ではローカルLLM呼び出しに置き換える）
    summary_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]
    response_text = f"[{model_name}] simulated_response_{summary_hash}: {prompt[:200]}"

    cache.set_llm_cache(model_name, prompt_hash, response_text, ttl_hours=ttl_hours)
    return response_text
