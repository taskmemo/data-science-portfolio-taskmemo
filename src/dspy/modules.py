from typing import List, Dict, Optional, Any
from dspy import Module
from src.dspy.sigunatures import CafeInfo, CafeSearch
from src.api.google_maps import geocode_place, search_nearby_cafes
from src.llm.local_llm import generate_recommendations # まだ実装していない

class CafeFinderModule(Module):
    """ Module to find nearby cafes given a place name """
    
    def find_cafes(self, place_name: str, radius: int = 1000, limit: int = 20) -> CafeSearch:
        """ Find nearby cafes given a place name """
        loc = geocode_place(place_name)
        if not loc:
            raise ValueError(f"Could not geocode the {place_name}")
        lat, lng = loc
        cafes_data = search_nearby_cafes(lat, lng, radius=radius, limit=limit)
        cafes = [CafeInfo(**cafe) for cafe in cafes_data]
        
        recommendations = generate_recommendations(cafes)

        return CafeSearch(
            latitude=lat,
            longitude=lng,
            radius=radius,
            cafes=cafes,
            total_results=len(cafes),
            recommendations=recommendations
        )
class CafeRecommendationModule(Module):
    """ Module to recommend cafes from a list of CafeInfo with local LLM """
    
    def recommend_cafes(self, cafes: List[CafeInfo], top_n: int = 5) -> List[CafeInfo]:
        """ Recommend top N cafes from the list """
        recommendations = generate_recommendations(cafes, top_n=top_n)
        return recommendations