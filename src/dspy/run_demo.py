from src.dspy.modules import CafeFinderModule, CafeRecommendationModule

def main():
    """ Run a demo of the Cafe Finder and Recommendation modules """
    
    place_name = "Jiyugaoka, Tokyo"
    user_query = "静かで作業に適したカフェ"

    # Initialize modules
    cafe_finder = CafeFinderModule()
    cafe_recommender = CafeRecommendationModule()

    # Find cafes near the specified place
    try:
        cafe_search_result = cafe_finder.find_cafes(place_name, radius=1000, limit=5)
        print(f"Found {cafe_search_result.total_results} cafes near {place_name}.")
    except Exception as e:
        print(f"Error finding cafes: {e}")
        return

    # Recommend cafes based on user query
    recommendation_result = cafe_recommender.generate_recommendation(
        cafes=cafe_search_result.cafes,
        user_query=user_query
    )

    print("Recommendation:")
    print(recommendation_result.recommendation)

if __name__ == "__main__":
    main()

"""
出力結果の例：

✅ 検出件数: 20 件
Found 20 cafes near Jiyugaoka, Tokyo.
Recommendation:
ユーザーの希望「静かで作業に適したカフェ」に基づき、以下の5つのカフェを推薦します。評価だけでなく、一般的なカフェの傾向も考慮して選んでいます。

1. **ラジオプラント (⭐️4.6):** 評価が最も高く、落ち着いた雰囲気で、集中して作業したいユーザーに最適です。静かで、居心地の良い空間を提供していると評判です。
2. **usubane (⭐️4.3):** 評価が高く、落ち着いた雰囲気で、集中して作業したいユーザーに最適です。
3. **セキルバーグカフェ (⭐️4.2):** 評価が高く、静かで落ち着いた雰囲気で作業できると評判です。
4. **LATTE GRAPHIC 自由が丘店 (⭐️4.1):** 評価が高く、落ち着いた雰囲気で作業に適していると評判です。
5. **CHA NO KO COFFEE ROASTERY (⭐️4.4):** 評価が高く、コーヒーの香りに包まれた静かな空間で作業したいユーザーにおすすめです。

これらのカフェは、評価が高く、レビューでも静かで落ち着いた雰囲気であるという言及が多いことから、ユーザーの希望に合う可能性が高いと考えられます。
"""