# ☕️ Cafe Finder Bot
**DSPy × ローカルLLM × Google Maps API を用いた、近くのカフェ検索アプリ**

---

## 🚀 概要（Overview）

本プロジェクトは、  
「現在地から近くのカフェを簡単に検索し、会話形式でおすすめを教えてくれる」  
AIアシスタントを構築する個人開発プロジェクトです。

- **Google Maps API** で店舗データを取得  
- **DSPy** で推論プロセスを最適化  
- **ローカルLLM**（例: Mistral / Phi-3 / ELYZA）を利用して自然な対話を生成  
- **Streamlit** によるWeb UIで実装  

本システムは、以前開発した  
[🌴 種子島グルメチャットBot (Zenn記事)](https://zenn.dev/taskmemo/articles/7a781ac4fb5ea4)  
の発展版として位置づけています。

---

## 🧩 システム構成図（Architecture）

```mermaid
graph TD
    A[ユーザー] -->|入力: 現在地 or 地名| B[Streamlit UI]
    B --> C[Google Maps API]
    C -->|店舗データ| D[Retriever Layer]
    D -->|カフェ情報JSON| E[DSPy Signature]
    E -->|推論プロンプト| F[ローカルLLM]
    F -->|生成テキスト| G[Streamlit表示]
````

---

## ⚙️ 使用技術（Tech Stack）

| 分類         | 技術名                                         | 用途               |
| ---------- | ------------------------------------------- | ---------------- |
| 言語         | Python 3.11                                 | メイン開発言語          |
| Webフレームワーク | Streamlit                                   | フロントエンドUI        |
| LLM最適化     | DSPy                                        | モジュール構築・プロンプト最適化 |
| LLM実行環境    | Ollama / LM Studio                          | ローカルLLM API化     |
| LLMモデル例    | Mistral-Instruct-7B / Phi-3-mini / ELYZA-7B | 応答生成             |
| API        | Google Maps Places API                      | カフェ検索・詳細取得       |
| データ保存      | SQLite / JSON / Cache                       | キャッシュと履歴管理       |

---

## 🧠 機能概要（Features）

| 機能名             | 概要                              |
| --------------- | ------------------------------- |
| 🔍 **カフェ検索**    | 現在地・半径指定で近隣のカフェ情報を取得            |
| 🗺️ **地図リンク生成** | 各店舗に Google Maps のナビリンクを付与      |
| 💬 **LLM推薦文生成** | ローカルLLMが自然文でおすすめコメントを生成         |
| ⚡ **キャッシュ最適化**  | 同条件でのAPI再利用により高速化               |
| 🎛️ **条件フィルタ**  | 「静かな店」「Wi-Fiあり」などの条件を指定可能（発展予定） |

---

## 📁 ディレクトリ構成（Project Structure）

```
project_root/
├── src/
│   ├── app/
│   │   └── streamlit_app.py           # Streamlitアプリ本体
│   ├── api/
│   │   └── google_maps.py             # Google Maps APIラッパー
│   ├── dspy/
│   │   ├── signatures.py              # DSPy Signature定義
│   │   └── modules.py                 # 推論モジュール
│   ├── llm/
│   │   └── local_llm_client.py        # ローカルLLM呼び出し
│   └── utils/
│       └── cache_manager.py           # キャッシュ制御
├── config/
│   └── config.yaml                    # APIキー・モデル設定
├── data/
│   └── cache.sqlite                   # キャッシュDB
├── requirements.txt
├── README.md
└── .env.example                       # APIキー設定例
```

---

## 🔧 設定（Setup）

### 1️⃣ 環境構築

```bash
uv venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ `.env` 設定例

プロジェクトルートに .env を置き、Google Maps API キーなどを管理します（推奨）。例:

```
# .env (プロジェクトルート)
GOOGLE_MAPS_API_KEY=xxxxxxx
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=mistral
```

Python 側での読み込み例（python-dotenv を使用）:

```python
# README に示す読み込み例
from dotenv import load_dotenv
import os

load_dotenv()  # .env を読み込む
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 実装方針
# - アプリはまず環境変数(GOOGLE_MAPS_API_KEY)を参照する。
# - 見つからない場合のみ config/config.yaml の google_maps.api_key を参照する（ただし config に API キーをハードコードするのは非推奨）。
```

インストール例:

```bash
pip install python-dotenv
```

### 3️⃣ Streamlit起動

```bash
streamlit run src/app/streamlit_app.py
```

---

## 🧮 DSPy 設計概要

### Signature定義

```python
from dspy import Signature

class CafeSearch(Signature):
    """指定された位置情報からおすすめカフェを検索する。"""
    latitude: float
    longitude: float
    radius_meters: int = 1000
    -> recommendations: list[dict]
```

### モジュール構成

```python
from dspy import Module

class CafeFinderModule(Module):
    def run(self, inp: CafeSearch):
        cafes = search_nearby_cafes(inp.latitude, inp.longitude, inp.radius_meters)
        return {"recommendations": cafes}
```

### 応答生成（LLM）

```python
prompt = f"""
次のカフェ情報を基に、ユーザーにフレンドリーにおすすめ文を生成してください。
{cafes}
"""
response = local_llm.generate(prompt)
```

---

## 🌍 将来的な拡張（Future Work）

| 分類             | アイデア                           |
| -------------- | ------------------------------ |
| 🧭 **RAG化**    | Google Maps＋口コミ情報をベクトル化して類似検索  |
| 🎙️ **音声入力**   | Whisper / SpeechRecognition 連携 |
| 📍 **位置自動取得**  | HTML5 Geolocation API 対応       |
| 🪄 **パーソナライズ** | ユーザー嗜好データを保存し推薦最適化             |
| 💡 **教育×地域分析** | カフェ密度・口コミデータを用いた地域分析モデルに展開     |

---

## 📚 参考

* [Google Maps Platform - Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
* [DSPy Documentation](https://github.com/stanfordnlp/dspy)
* [Ollama Models List](https://ollama.ai/library)
* [種子島グルメチャットBot - Zenn記事](https://zenn.dev/taskmemo/articles/7a781ac4fb5ea4)

---

## 🧑‍💻 Author

**Tasuku Kurasawa**

* Data Scientist / AI Engineer
* Interests: 教育 × データ × AI
* GitHub: [@taskmemo](https://github.com/taskmemo)

---