from typing import List, Dict, Optional, Any
from dspy import Module
from src.dspy.signatures import CafeInfo, CafeSearch, CafeRecommendation
from src.api.google_maps import geocode_place, search_nearby_cafes, get_geocode_with_cache, get_place_details
from src.llm.local_llm import run_local_model

class CafeFinderModule(Module):
    """ Module to find nearby cafes given a place name """
    
    def find_cafes(self, place_name: str, radius: int = 1000, limit: int = 20) -> CafeSearch:
        """ Find nearby cafes given a place name """
        # Geocode the place name to get lat/lng
        loc = get_geocode_with_cache(place_name)
        if not loc:
            raise ValueError(f"Could not geocode the {place_name}")
        lat, lng = loc["results"][0]["geometry"]["location"]["lat"], loc["results"][0]["geometry"]["location"]["lng"]
        cafes_data = search_nearby_cafes(lat, lng, radius=radius, limit=limit) # get nearby cafes
        
        cafes = []
        for cafe in cafes_data:
            details = get_place_details(cafe["place_id"])
            if details:
                cafe.update({
                    "website": details.get("website"),
                    "opening_hours": details.get("opening_hours"),
                    "reviews": details.get("reviews"),
                    "rating": details.get("rating"),
                    "user_ratings_total": details.get("user_ratings_total"),
                })
            else:
                print(f"⚠️ 詳細情報の取得に失敗しました: {cafe['name']}")

            cafes.append(CafeInfo(**cafe))

        return CafeSearch(
            place_name=place_name,
            radius=radius,
            latitude=lat,
            longitude=lng,
            cafes=cafes,
            total_results=len(cafes)
        )

class CafeRecommendationModule(Module):
    """ Generate natural-language recommendations from cafe info """

    def generate_recommendation(self, cafes: List[CafeInfo], user_query: str) -> CafeRecommendation:
        """ Generate top 5 cafe recommendations based on user query """
        # カフェリストをLLM入力用に整形（name, rating に加え主要フィールドを含める）
        def fmt_field(obj, attr, fallback="N/A"):
            """ Helper to format field values """
            val = getattr(obj, attr, None)
            if val is None:
                return fallback
            if isinstance(val, list):
                return ", ".join(map(str, val)) if val else fallback
            if isinstance(val, dict):
                return str(val)
            return str(val)

        cafes_text = "\n\n".join([
            (
                f"Name: {fmt_field(cafe, 'name')}\n"
                f"Rating: {fmt_field(cafe, 'rating')}\n"
                f"Reviews: {fmt_field(cafe, 'user_ratings_total')}\n"
                f"Price level: {fmt_field(cafe, 'price_level')}\n"
                f"Types: {fmt_field(cafe, 'types')}\n"
                f"Open now: {fmt_field(getattr(cafe, 'opening_hours', {}), 'get', 'N/A') if False else fmt_field(cafe, 'opening_hours')}\n"
                f"Address / Vicinity: {fmt_field(cafe, 'vicinity')}\n"
            )
            for cafe in cafes
        ])

        prompt = (
            f"以下のカフェ一覧から、ユーザーの希望に最も合う上位5つを選び、"
            f"各カフェにつき簡潔な推薦理由（該当する特徴と評価を含める）を述べてください。\n\n"
            f"ユーザーの希望: {user_query}\n\n"
            f"カフェ一覧:\n{cafes_text}\n\n"
            f"出力形式: 箇条書きで上位5つ（Name: xxx — 理由）。"
        )

        res = run_local_model(prompt)

        return CafeRecommendation(
            cafes=[c.model_dump() for c in cafes],
            user_query=user_query,
            recommendation=res
        )
