import os
from dotenv import load_dotenv
import streamlit as st
from src.api.google_maps import search_nearby_cafes, geocode_place
from src.dspy.sigunatures import CafeInfo
from src.dspy.modules import CafeFinderModule, CafeRecommendationModule
from src.utils.cache_manager import CacheManager

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

cache = CacheManager()

# set streamlit config
st.set_page_config(page_title='☕️ Cafe Finder Bot', layout='centered')

def main():
    st.title("☕️ Cafe Finder Bot")
    st.caption("地名を入力して、近くのカフェを検索します。")

    # API key check
    if not GOOGLE_MAPS_API_KEY:
        st.error("❌ Google Maps APIキーが設定されていません。 `.env` または config.yaml を確認してください。")
        st.stop()
    
    # ======================================
    # User Inputs
    # ======================================
    place_name = st.text_input("地名 / 住所（例：渋谷駅, 東京駅）")   
    user_query = st.text_input("カフェに求める条件（例：静か、作業に適した、コーヒーが美味しい）")
    radius = st.slider("検索半径（メートル）", min_value=100, max_value=5000, value=1000, step=100)
    
    if place_name and radius and user_query and st.button("☕️ 近くのカフェを検索"):
        # ======================================
        # 🔹　キャッシュキー生成
        # ======================================
        cache_key = f"{place_name}_{radius}".lower().strip()
        cached_data = cache.get_api_cache(cache_key)
        if cached_data:
            st.success("💾 キャッシュからデータを取得しました！")
            cafes = cached_data
        else:
            # ======================================
            # Geocode Place
            # ======================================
            with st.spinner("位置情報を取得中..."):
                loc = geocode_place(place_name)
            if not loc:
                st.error("❌ 位置情報の取得に失敗しました。地名を確認してください。")
                st.stop()
            lat, lng = loc
            with st.spinner("カフェ情報の検索中..."):
                cafes = search_nearby_cafes(lat, lng, radius=radius, limit=5) #上位5件を取得
            if not cafes:
                st.warning("⚠️ 近くにカフェが見つかりませんでした。")
                return 
            
            # 🔹 キャッシュを保存
            cache.set_api_cache(cache_key, cafes, ttl_hours=24)

        st.success(f"✅ {len(cafes)} 件のカフェを発見しました！")

        # ======================================
        # Cafe Recommendation
        # ======================================
        cafe_recommender = CafeRecommendationModule()
        with st.spinner("カフェの推薦を生成中..."):
            recommendation_result = cafe_recommender.generate_recommendation(
                cafes=[CafeInfo(**cafe) for cafe in cafes],
                user_query=user_query
            )
        st.success("✅ カフェの推薦が完了しました！")

        # ======================================
        # Cafe Recommendation Display
        # ======================================
        st.write(recommendation_result.recommendation)
        st.write("### 発見したカフェ一覧")
        for c in cafes:
            st.markdown(
            f"""
            **☕️ {c['name']}**
            📍 {c['address']}
            ⭐️ 評価: {c['rating']} ({c['user_ratings_total']})件のレビュー
            🔗 [Google Mapsで開く]({c['maps_link']})
            """,
            unsafe_allow_html=True
            )
        st.divider()
                            
        # ======================================
        # Map Display
        # ======================================
        map_points = [{"lat": c["lat"],
                       "lon": c["lng"],
                       "name": c["name"],
                       "address": c["address"]} for c in cafes if c["lat"] and c["lng"]]
        if map_points:
            st.map(map_points)
        
    st.divider()
    st.caption("📍 Powered by Google Maps API | Developed by Tasuku Kurasawa")

if __name__ == "__main__":
    main()