import requests
import yaml
import os
import json 
from dotenv import load_dotenv

# Load configuration from YAML file
def load_config(path='config/config.yaml'):
    load_dotenv()  # .envファイルから環境変数をロード

    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    api_key_env = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key_env:
        config["google_maps"]["api_key"] = api_key_env
    # あとでローカルLLMのエンドポイントも一緒に取得するように変更する。

    return config


config = load_config()

# Google Maps Places API configuration
API_KEY = config["google_maps"]["api_key"] # .envに入っているのに取得できるか？
BASE_URL = config["google_maps"]["base_url"]
RADIUS = 1000  # デフォルトの検索半径（メートル）



def search_nearby_cafes(lat: float, lon: float, radius: int = None, limit: int = 10):
    """ Google Maps Places APIを使用して、
        指定された緯度経度の近くにあるカフェを最大5つ検索する"""
    params = {
        "location": f"{lat},{lon}",
        "radius": radius if radius else RADIUS,
        "type": config["google_maps"]["place_type"],
        "language": config["google_maps"]["language"],
        "key": API_KEY
    }
    
    url = f"{BASE_URL}/nearbysearch/json?key={API_KEY}&location={lat},{lon}&radius={params['radius']}&type={params['type']}&language={params['language']}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    print("🔍 Google Maps API response:")
    print(data)  # ← ここで中身を見る

    results = data.get("results", [])[:limit]
    print(f"✅ 検出件数: {len(results)} 件")

    cafes = []
    for place in results:
        cafes.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "location": place.get("geometry", {}).get("location"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "map_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}"
        })
    return cafes

if __name__ == "__main__":
    # テスト用の緯度経度
    latitude = 35.606475
    longitude = 139.667239
    cafes = search_nearby_cafes(latitude, longitude)
    print(json.dumps(cafes, indent=2, ensure_ascii=False))