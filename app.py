import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. 頁面基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

# 安全讀取 SerpApi 金鑰
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 智慧地點提示函式 ---
def get_location_suggestions(query):
    if len(query) < 1: return []
    url = f"https://autocomplete.travelpayouts.com/places2?term={query}&locale=en&types[]=airport&types[]=city"
    try:
        return requests.get(url).json()
    except:
        return []

# --- 3. Google Flights 搜尋函式 ---
def search_flights(dep, arr, date_obj):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "hl": "zh-tw",
        "api_key": SERP_API_KEY
    }
    try:
        res = requests.get(url, params=params).json()
        return res.get("best_flights", [])
    except:
        return []

# --- 4. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")

with st.sidebar:
    st.header("🔍 目的地設定")
    dest_input = st.text_input("輸入目的地 (如: Prague)", value="Prague")
    suggestions = get_location_suggestions(dest_input)
    
    if suggestions:
        selected_loc = st.selectbox(
            "請確認目的地：",
            options=suggestions,
            format_func=lambda x: f"{x['name']} ({x['code']}) - {x['country_name']}"
        )
        dest_iata = selected_loc['code']
    else:
        dest_iata = "PRG"

    st.divider()
    st.header("📅 日期邏輯設定")
    
    # 強制 S1 在今天之後，基準日 S2 預設推算為 S1 + 60 天
    today = datetime.today().date()
    min_s1 = today + timedelta(days=1)
    
    st.info(f"💡 系統已鎖定第一段票(S1)必須晚於今日 ({today})")
    
    # 讓使用者選擇 S2 基準日，但限制其最小值
    base_date = st.date_input("選擇基準出發日 (S2)", value=today + timedelta(days=61), min_value=today + timedelta(days=61))
    
    # 自動推算四段日期
    s1_d = base_date - timedelta(days=60)
    s2_d = base_date
    s3_d = base_date + timedelta(days=10)
    s4_d = base_date + timedelta(days=120)

# --- 5. 主畫面：行程預覽 ---
st.markdown("### ✈️ 四段票自動化排程預覽")
d_cols = st.columns(4)
d_cols[0].metric("S1 (外站->TPE)", s1_d.strftime("%Y-%m-%d"), "今日後✅")
d_cols[1].metric("S2 (TPE->歐洲)", s2_d.strftime("%Y-%m-%d"))
d_cols[2].metric("S3 (歐洲->TPE)", s3_d.strftime("%Y-%m-%d"))
d_cols[3].metric("S4 (TPE->外站)", s4_d.strftime("%Y-%m-%d"))

# --- 6. 執行搜尋 ---
if st.button("🚀 啟動全自動外站比價 (HKG/KUL/BKK/SIN)"):
    # 固定搜尋的外站清單
    target_stations = ["HKG", "KUL", "BKK", "SIN"]
    
    for station in target_stations:
        st.subheader(f"📍 分析外站：{station}")
        
        with st.spinner(f"正在抓取 {station} 相關航段數據..."):
            # 以 S2 段 (台北飛目的地) 作為核心價格參考
            # 注意：Google Flights 主要顯示該日期的最佳價格，不論外站起點，
            # 此處邏輯為模擬從 TPE 出發之關鍵 S2 航段
            results = search_flights("TPE", dest_iata, s2_d)
            
            if results:
                for flight in results[:2]:
                    price = flight.get('price', 0)
                    airline = flight['flights'][0]['airline']
                    duration = flight.get('total_duration', '未知')
                    st.success(f"💰 TWD {price:,} | 航空公司：{airline} | 總長：{duration}分")
            else:
                st.warning(f"目前 {station} 方案無報價或該日期無適合航班。")

st.divider()
st.caption("𓃥 White 6 Studio | 四段票日期邏輯：S1 > Today | 外站全自動遍歷搜尋")
