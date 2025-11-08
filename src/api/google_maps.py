import os
import requests
import yaml
import json
from dotenv import load_dotenv
from typing import Optional, Tuple, List, Dict
import sys
from requests.exceptions import RequestException
import hashlib

from src.utils.cache_manager import CacheManager


# ======================================
# ✅ set up configuration
# ======================================

def load_config(path='config/config.yaml') -> dict:
    """Load configuration from YAML file and .env"""
    load_dotenv()
    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    # .env優先
    api_key_env = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key_env:
        config["google_maps"]["api_key"] = api_key_env

    return config


config = load_config()

API_KEY = config["google_maps"].get("api_key")
BASE_URL = config["google_maps"].get("base_url", "https://maps.googleapis.com/maps/api")
RADIUS = config["google_maps"].get("default_radius", 1000)

if not API_KEY:
    print("❌ Google Maps APIキーが設定されていません。 `.env` または config.yaml を確認してください。")
    sys.exit(1)


cache = CacheManager()


# ======================================
# 🗺️ Geocoding API（地名 → 緯度経度）
# ======================================

def geocode_place(place_name: str) -> Optional[Tuple[float, float]]:
    """Use Google Geocoding API to get coordinates from place name"""
    url = f"{BASE_URL}/geocode/json"
    params = {"address": place_name, "key": API_KEY}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except RequestException as e:
        print(f"❌ Geocoding APIリクエスト失敗: {e}")
        return None

    data = resp.json()
    status = data.get("status")

    if status == "OK" and data.get("results"):
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        print(f"⚠️ Geocoding API失敗: status={status}, error={data.get('error_message')}")
        return None


def get_geocode_with_cache(address, ttl_hours=24):
    """
    キャッシュがあればそれを返す。なければ geocode_place を呼んで結果をキャッシュして返す。
    geocode_place が None を返した場合は None を返す。
    """
    cached = cache.get_api_cache(address)
    if cached:
        return cached

    coords = geocode_place(address)
    if coords:
        lat, lng = coords
        data = {
            "status": "OK",
            "results": [
                {
                    "formatted_address": address,
                    "geometry": {"location": {"lat": lat, "lng": lng}}
                }
            ]
        }
        cache.set_api_cache(address, data, ttl_hours=ttl_hours)
        return data

    print(f"⚠️ Geocoding結果が見つかりません: {address}")
    return None


# ======================================
# ☕ Places API（近隣カフェ検索）
# ======================================

def search_nearby_cafes(lat: float, lng: float, user_query: str, radius: int = None, limit: int = 10) -> List[Dict]:
    """Use Google Places API to search for nearby cafes"""
    radius = radius if radius else RADIUS

    profile_cfg = config["google_maps"].get("search_prodfiles", [])
    
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": profile_cfg["place_type"] if profile_cfg else "cafe",
        "keyword": profile_cfg["keyword"] if profile_cfg else user_query,
        "language": config["google_maps"].get("language", "ja"),
        "key": API_KEY
    }

    url = f"{BASE_URL}/place/nearbysearch/json"

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except RequestException as e:
        print(f"❌ Nearby Search APIリクエスト失敗: {e}")
        return []

    data = resp.json()
    status = data.get("status")

    if status != "OK":
        print(f"⚠️ APIエラー: {status} - {data.get('error_message', '詳細なし')}")
        return []

    results = data.get("results", [])[:limit]
    print(f"✅ 検出件数: {len(results)} 件")

    cafes = []
    for place in results:
        cafes.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "lat": place.get("geometry", {}).get("location", {}).get("lat"),
            "lng": place.get("geometry", {}).get("location", {}).get("lng"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "maps_link": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}"
        })

    return cafes
