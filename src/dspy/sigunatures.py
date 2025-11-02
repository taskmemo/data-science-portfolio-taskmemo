from typing import List, Dict, Optional
from dspy import Signature

class CafeInfo(Signature):
    """ cafe information class """
    name: str
    address: str
    lat: Optional[float]
    lng: Optional[float]
    rating: Optional[float]
    user_ratings_total: Optional[int]
    place_id: str
    maps_link: str

class CafeSearch(Signature):
    """ cafe search result class """
    latitude: float
    longitude: float
    radius: int = 1000
    cafes: List[CafeInfo]
    total_results: int = 20
    recommendations: Optional[List[CafeInfo]] = None