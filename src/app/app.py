import os
from dotenv import load_dotenv
import streamlit as st
from src.api.google_maps import search_nearby_cafes, geocode_place

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# set streamlit config
st.set_page_config(page_title='☕️ Cafe Finder Bot', layout='centered')

def main():
    st.title("☕️ Cafe Finder Bot")
    st.caption("地名を入力して、近くのカフェを検索します。")

    # API key check
    if not GOOGLE_MAPS_API_KEY:
        st.error("❌ Google Maps APIキーが設定されていません。 `.env` または config.yaml を確認してください。")
        st.stop()
    
    # search form and radius slider
    place_name = st.text_input("地名 / 住所（例：渋谷駅, 東京駅）")   
    radius = st.slider("検索半径（メートル）", min_value=100, max_value=5000, value=1000, step=100)
    if place_name and radius and st.button("☕️ 近くのカフェを検索"):
        with st.spinner("位置情報を取得中..."):
            loc = geocode_place(place_name)
        if not loc:
            st.error("❌ 位置情報の取得に失敗しました。地名を確認してください。")
            st.stop()
        else:
            lat, lng = loc
            with st.spinner("カフェ情報の検索中..."):
                cafes = search_nearby_cafes(lat, lng, radius=radius, limit=20)
            if not cafes:
                st.warning("⚠️ 近くにカフェが見つかりませんでした。")
                return 
            st.success(f"✅ {len(cafes)} 件のカフェを発見しました！")

        # plot cafes on map
        map_points = [{"lat": c["lat"],
                       "lon": c["lng"],
                       "name": c["name"],
                       "address": c["address"]} for c in cafes if c["lat"] and c["lng"]]
        if map_points:
            st.map(map_points)
            st.write("### カフェ一覧")
        
        st.dataframe(
            [{
                "名前": c["name"],
                "住所": c["address"],
                "評価": c.get("rating", "N/A"),
                "レビュー数": c.get("user_ratings_total", "N/A")
            } for c in cafes],
            use_container_width=True
        )

        # show cafe details with expander
        for c in cafes:
            with st.expander(f"{c['name']} — {c.get('rating') or '?'}⭐"):
                st.write(f"📍 住所: {c.get('address')}")
                st.write(f"⭐ 評価: {c.get('rating')}（{c.get('user_ratings_total') or 0}件）")
                st.markdown(f"[Google Mapsで開く]({c.get('maps_link')})", unsafe_allow_html=True)

    st.divider()
    st.caption("📍 Powered by Google Maps API | Developed by Tasuku Kurasawa")

if __name__ == "__main__":
    main()