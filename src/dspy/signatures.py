from typing import List, Dict, Optional
import dspy
from src.api.google_maps import load_config



class CafeInfo(dspy.Signature):
    name: str = dspy.OutputField(desc="カフェの名前")
    address: str = dspy.OutputField(desc="カフェの住所")
    lat: Optional[float] = dspy.OutputField(desc="カフェの緯度", default=None)
    lng: Optional[float] = dspy.OutputField(desc="カフェの経度", default=None)
    rating: Optional[float] = dspy.OutputField(desc="カフェの評価（1.0〜5.0）", default=None)
    user_ratings_total: Optional[int] = dspy.OutputField(desc="カフェの評価数", default=None)
    maps_link: str = dspy.OutputField(desc="Google Mapsのカフェリンク", default="")
    reviews: Optional[List[str]] = dspy.OutputField(desc="カフェの口コミ情報", default=None)
    has_wifi: Optional[str] = dspy.OutputField(desc="カフェのWi-Fi有無", default=None)
    review_summary: Optional[str] = dspy.OutputField(desc="カフェの口コミ要約", default=None)

class CafeSearch(dspy.Signature):
    """ cafe search result class """
    # Input fields 
    place_name: str = dspy.InputField(desc = "検索した地名")
    radius: int = dspy.InputField(desc = "検索半径（メートル）")

    # Output fields
    latitude: float = dspy.InputField(desc = "検索地点の緯度")
    longitude: float = dspy.InputField(desc = "検索地点の経度")
    cafes: List[CafeInfo] = dspy.InputField(desc = "検索結果のカフェ情報リスト")
    total_results: int = dspy.InputField(desc = "検索結果の総件数")

class CafeRecommendation(dspy.Signature):
    """ カフェ情報に基づき、ユーザーの希望に沿ったおすすめ文を生成する """
    cafes: List[CafeInfo] = dspy.InputField(
        desc = "Google Maps APIから取得したカフェ情報のリスト"
    )

    user_query: str = dspy.InputField(
        desc = "ユーザーが求めている条件（例：静かなカフェ、作業可能なカフェなど）"
    )

    recommendation: str = dspy.OutputField(
        desc = "与えられたカフェ情報に基づいて、上位5つを推薦し、簡潔に理由を説明した文章",
        default=""
    )
