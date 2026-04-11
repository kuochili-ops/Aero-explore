import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 頁面基本配置 ---
st.set_page_config(
    page_title="White 6 Aero Explorer",
    page_icon="𓃥",
    layout="wide"
)

# 套用「白六」暗色主題與美化卡片
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .flight-card { 
        background-color: #1e2129; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 5px solid #ff4b4b;
        margin-bottom: 15px;
    }
    .price-tag { color: #00ff00; font-size: 1.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 金鑰設定 ---
# 建議將金鑰放入 st.secrets["SERP_API_KEY"]
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 3. 核心搜尋函式 (Google Flights 引擎) ---
def get_best_flights(dep_id, arr_id, date_obj):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep_id,
        "arrival_id": arr_id,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "hl": "zh-tw",
        "api_key": SERP_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get("best_flights", [])
    except Exception as e:
        st.error(f"搜尋發生錯誤: {e}")
        return []

# --- 4. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")
st.info("已成功連結 SerpApi (Google Flights 引擎) ─ 目前最穩定之數據源")

with st.sidebar:
    st.header("📅 行程參數")
    main_dest = st.text_input("目的地機場 (IATA)", value="PRG")
    s2_date = st.date_input("第二段出發日 (TPE -> 歐洲)", value=datetime(2026, 6, 10))
    
    st.divider()
    st.header("📍 外站比價清單")
    outstations = st.multiselect(
        "選擇要分析的外站", 
        ["HKG", "KUL", "BKK", "SIN", "NRT"], 
        default=["HKG", "KUL", "BKK"]
    )

# --- 5. 四段票日期推算展示 ---
s1_date = s2_date - timedelta(days=60)
s3_date = s2_date + timedelta(days=10)
s4_date = s2_date + timedelta(days=120)

cols = st.columns(4)
cols[0].metric("S1 (外站->TPE)", s1_date.strftime("%m/%d"))
cols[1].metric("S2 (TPE->歐洲)", s2_date.strftime("%m/%d"))
cols[2].metric("S3 (歐洲->TPE)", s3_date.strftime("%m/%d"))
cols[3].metric("S4 (TPE->外站)", s4_date.strftime("%m/%d"))

# --- 6. 執行比價邏輯 ---
if st.button("🚀 執行四段票交叉比價"):
    if not outstations:
        st.warning("請至少選擇一個外站進行比價。")
    else:
        for station in outstations:
            st.markdown(f"### 📍 搜尋自 **{station}** 出發的航線組合")
            
            with st.spinner(f"正在抓取 Google Flights 數據 ({station})..."):
                # 我們搜尋 S2 (台北飛歐洲) 的價格作為核心基準
                best_flights = get_best_flights("TPE", main_dest, s2_date)
                
                if best_flights:
                    for flight in best_flights[:2]: # 僅顯示前兩名最優方案
                        # 解析 SerpApi 回傳格式
                        price = flight.get('price', '未提供')
                        airline = flight['flights'][0]['airline']
                        duration = flight.get('total_duration', '未知')
                        
                        st.markdown(f"""
                        <div class="flight-card">
                            <span class="price-tag">TWD {price:,}</span><br>
                            <b>航空公司：</b>{airline} <br>
                            <b>總飞行時間：</b>{duration} 分鐘 <br>
                            <small>基準航段：TPE ✈️ {main_dest} | 日期：{s2_date}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning(f"目前從 {station} 找不到符合條件的航班，建議微調日期。")

st.divider()
st.caption("𓃥 White 6 Studio - 2026 旅遊自動化工具 | 數據源: Google Flights via SerpApi")
