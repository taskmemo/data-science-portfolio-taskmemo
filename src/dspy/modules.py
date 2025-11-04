from typing import List, Dict, Optional, Any
from dspy import Module
from src.dspy.sigunatures import CafeInfo, CafeSearch, CafeRecommendation
from src.api.google_maps import geocode_place, search_nearby_cafes
from src.llm.local_llm import run_local_model

class CafeFinderModule(Module):
    """ Module to find nearby cafes given a place name """
    
    def find_cafes(self, place_name: str, radius: int = 1000, limit: int = 20) -> CafeSearch:
        """ Find nearby cafes given a place name """
        loc = geocode_place(place_name) # get latitude and longitude from place name
        if not loc:
            raise ValueError(f"Could not geocode the {place_name}")
        lat, lng = loc
        cafes_data = search_nearby_cafes(lat, lng, radius=radius, limit=limit) # get nearby cafes
        cafes = [CafeInfo(**cafe) for cafe in cafes_data]

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
        # カフェリストをLLM入力用に整形
        cafes_text = "\n".join([
            f"{cafe.name}  (⭐️Rating: {cafe.rating})"
            for cafe in cafes
        ])

        # プロンプト
        prompt = (
            f"以下のカフェリストから、ユーザーの希望に最も合う上位5つのカフェを推薦し、"
            f"各カフェの特徴や評価を考慮して、それぞれの推薦理由を簡潔に説明してください。\n\n"
            f"# ユーザーの希望: {user_query}\n\n"
            f"# カフェリスト:\n{cafes_text}\n\n"
            f"# 推薦結果: "
        )

        # ローカルLLMに投げる
        res = run_local_model(prompt)

        return CafeRecommendation(
            cafes=cafes,
            user_query=user_query,
            recommendation=res
        )
