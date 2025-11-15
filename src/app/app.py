import os
from dotenv import load_dotenv
import json
import streamlit as st
import streamlit.components.v1 as components
from src.api.google_maps import search_nearby_cafes, geocode_place
from src.dspy.signatures import CafeInfo
from src.dspy.modules import CafeFinderModule, CafeRecommendationModule
from src.utils.cache_manager import CacheManager

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
cache = CacheManager()

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
            # Geocode Place（位置情報の取得）
            # ======================================
            with st.spinner("位置情報を取得中..."):
                loc = geocode_place(place_name)
            if not loc:
                st.error("❌ 位置情報の取得に失敗しました。地名を確認してください。")
                st.stop()
            lat, lng = loc
            with st.spinner("カフェ情報の検索中..."):
                cafes = search_nearby_cafes(lat, lng, radius=radius, limit=5, user_query=user_query) #上位5件を取得
            if not cafes:
                st.warning("⚠️ 近くにカフェが見つかりませんでした。")
                return 
            
            # 🔹 キャッシュを保存
            cache.set_api_cache(cache_key, cafes, ttl_hours=24)

        st.success(f"✅ {len(cafes)} 件のカフェを発見しました！")
        # ======================================
        # Wi-fi and Review Summary Enrichment（口コミ要約とWi-Fi情報の拡充）
        # ======================================
        cafe_finder = CafeFinderModule()
        enriched_cafes = []
        with st.spinner("口コミ要約とWi-Fi情報の拡充中..."):
            for cafe in cafes:
                enriched_cafe = cafe_finder.enrich_cafe_info(CafeInfo(**cafe))
                enriched_cafes.append(enriched_cafe.model_dump())

        # ======================================
        # Cafe Recommendation（カフェ推薦文の生成）
        # ======================================
        cafe_recommender = CafeRecommendationModule()
        with st.spinner("カフェの推薦を生成中..."):
            recommendation_result = cafe_recommender.generate_recommendation(
                cafes=[CafeInfo(**cafe) for cafe in cafes],
                user_query=user_query
            )
        st.success("✅ カフェの推薦が完了しました！")

        # ======================================
        # Cafe Recommendation Display（カフェ推薦文の表示）
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
            📝 口コミ要約: {c.get('review_summary', 'なし')}
            📶 Wi-Fi: {'あり' if c.get('has_wifi') else 'なし'}
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
                      } for c in cafes if c.get("lat") and c.get("lng")]
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