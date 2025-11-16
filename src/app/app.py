import os
from dotenv import load_dotenv
import json
import streamlit as st
import streamlit.components.v1 as components
from src.dspy.signatures import CafeInfo
from src.dspy.modules import CafeFinderModule, CafeRecommendationModule
from src.utils.cache_manager import CacheManager

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
cache = CacheManager()
cafe_finder = CafeFinderModule()
cafe_recommender = CafeRecommendationModule()

# ======================================
# Helper functions 
# ======================================

def generate_google_map_html(cafes, api_key, center_lat, center_lng, zoom=15):
    """ generate HTML for embedding Google Map with cafe Markers """
    cafes_json = json.dumps(cafes, ensure_ascii=False)
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <meta charset="utf-8" />
        <style>
          #map {{ height:100%; width:100%; }}
          html,body {{ height:100%; margin:0; padding:0; }}
        </style>
      </head>
      <body>
        <div id="map" style="height:100%;"></div>
        <script>
          const cafes = {cafes_json};
          function initMap() {{
            const center = {{lat: {center_lat}, lng: {center_lng}}};
            const map = new google.maps.Map(document.getElementById('map'), {{ zoom: {zoom}, center }});
            const bounds = new google.maps.LatLngBounds();
            cafes.forEach(c => {{
              if(!c.lat || !c.lng) return;
              const pos = {{lat: c.lat, lng: c.lng}};
              const marker = new google.maps.Marker({{ position: pos, map: map, title: c.name }});
              bounds.extend(pos);
              const content = `
                <div style="font-family:Arial,sans-serif;line-height:1.2;max-width:240px">
                  <strong>${{c.name}}</strong><br/>
                  <div>📍 ${{c.address}}</div>
                  <div>⭐ ${{c.rating || '—'}} (${{c.user_ratings_total || 0}})</div>
                  <div><a href="${{c.maps_link}}" target="_blank">Google Mapsで開く</a></div>
                </div>
              `;
              const infowindow = new google.maps.InfoWindow({{ content }});
              marker.addListener('click', () => infowindow.open(map, marker));
            }});
            if(!bounds.isEmpty) map.fitBounds(bounds);
          }}
        </script>
        <script async defer src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap"></script>
      </body>
    </html>
    """
    return html

def to_cafeinfo(c):
    """" Convert input to CafeInfo instance """
    if isinstance(c, CafeInfo):
        return c
    if isinstance(c, dict):
        return CafeInfo(**c)
    raise ValueError("Invalid cafe data")


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
        # 🔹　キャッシュキー生成（一旦キャッシュ機能は使わないようにする）
        # ======================================
        #cache_key = f"{place_name}_{radius}".lower().strip()
        #cached_data = cache.get_api_cache(cache_key)
        #if cached_data:
            #st.success("💾 キャッシュからデータを取得しました！")
            #cafes = cached_data
        #else:

        # カフェ検索
        with st.spinner("位置情報とカフェ情報を取得中..."):
            results = cafe_finder.find_cafes(place_name, radius=radius, limit=5, user_query=user_query)
            cafes = results.cafes
            lat, lng = results.latitude, results.longitude

        if lat is None:
            st.error("❌ 位置情報の取得に失敗しました。地名を確認してください。")
            st.stop()
        if not cafes:
            st.warning("⚠️ 近くにカフェが見つかりませんでした。")
            return 
          
          # 🔹 キャッシュを保存
          #cache.set_api_cache(cache_key, results.model_dump(), ttl_hours=24)

        st.success(f"✅ {len(cafes)} 件のカフェを発見しました！")
        # ======================================
        # Wi-fi and Review Summary Enrichment（口コミ要約とWi-Fi情報の拡充）
        # ======================================
        enriched_cafes = []
        with st.spinner("口コミ要約とWi-Fi情報の拡充中..."):
            for cafe in cafes:
                cafe_obj = to_cafeinfo(cafe) # CafeInfoインスタンスに統一
                enriched = cafe_finder.enrich_cafe_info(cafe_obj)
                enriched_cafes.append(enriched.model_dump()) # 辞書型で保存
        # ======================================
        # Cafe Recommendation（カフェ推薦文の生成）
        # ======================================
        cafe_recommender = CafeRecommendationModule()
        with st.spinner("カフェの推薦を生成中..."):
            recommendation_result = cafe_recommender.generate_recommendation(
                cafes=[CafeInfo(**cafe) for cafe in enriched_cafes],
                user_query=user_query
            )
        st.success("✅ カフェの推薦が完了しました！")

        # ======================================
        # Cafe Recommendation Display（カフェ推薦文の表示）
        # ======================================
        st.write(recommendation_result.recommendation) # 表示しなくても良いか？
        st.write("### 発見したカフェ一覧")
        for c in enriched_cafes:
            st.markdown(
            f"""
            - **☕️ {c['name']}**
            - 📍 {c['address']}
            - ⭐️ 評価: {c['rating']} ({c['user_ratings_total']})件のレビュー
            - 🔗 [Google Mapsで開く]({c['maps_link']})
            - 📶 Wi-Fi: {'あり' if c.get('has_wifi') else 'なし'}
            - 📝 口コミ要約: {c.get('review_summary', 'なし')}
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
                       "address": c["address"],
                       "rating": c.get("rating"),
                       "user_ratings_total": c.get("user_ratings_total"),
                       "maps_link": c.get("maps_link")
                      } for c in enriched_cafes if c.get("lat") and c.get("lng")]
        if map_points:
            # 中心を最初のポイントに設定
            center = map_points[0]
            # Google Maps 用に必要なフィールドだけ抽出
            cafes_for_map = [
                {
                    "name": p["name"],
                    "address": p["address"],
                    "lat": p["lat"],
                    "lng": p["lon"],
                    "rating": p.get("rating"),
                    "user_ratings_total": p.get("user_ratings_total"),
                    "maps_link": p.get("maps_link", "")
                }
                for p in map_points
            ]
            map_html = generate_google_map_html(
                cafes=cafes_for_map,
                api_key=GOOGLE_MAPS_API_KEY,
                center_lat=center["lat"],
                center_lng=center["lon"],
                zoom=15
            )
            components.html(map_html, height=500)
        
    st.divider()
    st.caption("📍 Powered by Google Maps API | Developed by Tasuku Kurasawa")

if __name__ == "__main__":
    main()