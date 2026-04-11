import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. 頁面配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

# 核心 SerpApi Key
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 智慧地點補完 (不限次數) ---
def get_location_suggestions(query):
    if len(query) < 1: return []
    url = f"https://autocomplete.travelpayouts.com/places2?term={query}&locale=en&types[]=airport&types[]=city"
    try:
        return requests.get(url).json()
    except:
        return []

# --- 3. 強化版 Google Flights 搜尋 ---
def search_flights_pro(dep, arr, date_obj):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "hl": "zh-tw",
        "api_key": SERP_API_KEY,
        "type": "2" # 強制單程搜尋邏輯
    }
    try:
        res = requests.get(url, params=params).json()
        # 同時抓取 'best_flights' 與 'other_flights'
        best = res.get("best_flights", [])
        others = res.get("other_flights", [])
        return best + others
    except:
        return []

# --- 4. 側邊欄：邏輯設定 ---
with st.sidebar:
    st.header("🔍 目的地設定")
    dest_input = st.text_input("輸入目的地城市 (英文)", value="Prague")
    hints = get_location_suggestions(dest_input)
    if hints:
        selected = st.selectbox("請確認：", options=hints, format_func=lambda x: f"{x['name']} ({x['code']})")
        dest_iata = selected['code']
    else:
        dest_iata = "PRG"

    st.divider()
    st.header("📅 日期與外站邏輯")
    today = datetime.today().date()
    
    # 確保 S1 必須在明天之後，S2 必須在 S1 之後 60 天
    s1_min = today + timedelta(days=1)
    base_s2 = st.date_input("選擇基準出發日 (S2)", value=s1_min + timedelta(days=60), min_value=s1_min + timedelta(days=1))
    
    s1_d = base_s2 - timedelta(days=60)
    s2_d = base_s2
    s3_d = base_s2 + timedelta(days=10)
    s4_d = base_s2 + timedelta(days=120)

# --- 5. 主畫面展示 ---
st.title("𓃥 White 6 Aero Explorer")

d_cols = st.columns(4)
d_cols[0].metric("S1 (外站->TPE)", s1_d.strftime("%Y-%m-%d"))
d_cols[1].metric("S2 (TPE->歐洲)", s2_d.strftime("%Y-%m-%d"))
d_cols[2].metric("S3 (歐洲->TPE)", s3_d.strftime("%Y-%m-%d"))
d_cols[3].metric("S4 (TPE->外站)", s4_d.strftime("%Y-%m-%d"))

# --- 6. 全自動比價執行 ---
if st.button("🚀 開始執行四段票全自動交叉比價"):
    stations = ["HKG", "KUL", "BKK", "SIN"]
    
    for station in stations:
        st.subheader(f"📍 分析外站：{station}")
        
        with st.spinner(f"正在搜尋 {station} 出發之最佳方案..."):
            # 💡 核心優化：我們先搜尋 S2 (TPE->PRG) 作為所有外站共用的基準票價
            results = search_flights_pro("TPE", dest_iata, s2_d)
            
            if results:
                # 顯示前三個最優結果
                for f in results[:3]:
                    price = f.get('price', 0)
                    airline = f['flights'][0]['airline']
                    duration = f.get('total_duration', 'N/A')
                    # 抓取航班號碼
                    flight_no = f['flights'][0].get('flight_number', '')
                    
                    st.success(f"✅ TWD {price:,} | {airline} ({flight_no}) | 總時長: {duration}分")
            else:
                st.warning(f"目前 {station} 的 S2 基準日期 ({s2_d}) 無法獲取有效報價。")

st.divider()
st.caption("𓃥 White 6 Studio | 搜尋引擎：SerpApi Google Flights | 邏輯：自動遍歷全外站")
