import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 頁面基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

# 安全讀取 SerpApi 金鑰
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 智慧地點提示函式 (Travelpayouts 免費引擎) ---
def get_location_suggestions(query):
    if len(query) < 1: return []
    # 這個 API 是公開且免費的，反應速度極快，適合做輸入提示
    url = f"https://autocomplete.travelpayouts.com/places2?term={query}&locale=en&types[]=airport&types[]=city"
    try:
        res = requests.get(url).json()
        return res
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
    st.header("🔍 目的地智慧提示")
    # 目的地輸入與自動提示
    dest_input = st.text_input("輸入目的地關鍵字 (如: Pra...)", value="Prague")
    suggestions = get_location_suggestions(dest_input)
    
    if suggestions:
        selected_loc = st.selectbox(
            "請從選單中確認目的地：",
            options=suggestions,
            format_func=lambda x: f"{x['name']} ({x['code']}) - {x['country_name']}"
        )
        dest_iata = selected_loc['code']
        st.success(f"已鎖定目的地：{dest_iata}")
    else:
        dest_iata = "PRG"
        st.caption("請輸入關鍵字以獲取提示")

    st.divider()
    st.header("📅 基準日期 (S2)")
    # 預設為今天
    base_date = st.date_input("選擇基準出發日 (S2)", value=datetime.today())
    
    # 自動推算四段日期
    s1_d = base_date - timedelta(days=60)
    s2_d = base_date
    s3_d = base_date + timedelta(days=10)
    s4_d = base_date + timedelta(days=120)

    st.header("📍 外站設定")
    outstations = st.multiselect("外站比價範圍", ["HKG", "KUL", "BKK", "SIN"], default=["HKG", "KUL"])

# --- 5. 主畫面：四段票日期預覽 ---
st.markdown("### ✈️ 四段票預計行程")
d_cols = st.columns(4)
d_cols[0].metric("S1 (外站->TPE)", s1_d.strftime("%Y-%m-%d"))
d_cols[1].metric("S2 (TPE->歐洲)", s2_d.strftime("%Y-%m-%d"))
d_cols[2].metric("S3 (歐洲->TPE)", s3_d.strftime("%Y-%m-%d"))
d_cols[3].metric("S4 (TPE->外站)", s4_d.strftime("%Y-%m-%d"))

# --- 6. 執行搜尋 ---
if st.button("🚀 執行全自動四段票交叉比價"):
    for station in outstations:
        st.subheader(f"📍 方案分析：自 {station} 出發")
        
        # 搜尋最核心的 S2 段 (TPE -> 歐洲)
        with st.spinner(f"正在分析 {station} 航組價格..."):
            best_results = search_flights("TPE", dest_iata, s2_d)
            
            if best_results:
                for flight in best_results[:2]:
                    price = flight.get('price', 0)
                    airline = flight['flights'][0]['airline']
                    st.success(f"💰 TWD {price:,} | 航空公司：{airline} (S2 基準報價)")
            else:
                st.warning(f"目前從 {station} 找不到符合日期的有效票價。")

st.divider()
st.caption("𓃥 White 6 Studio | 地點提示與四段日期自動化已啟動")
