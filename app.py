import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# 設定頁面
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥")
st.title("𓃥 White 6 Aero Explorer")

# 從 Secrets 讀取金鑰
RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"]
HOST = "skyscanner-flights-travel-api.p.rapidapi.com"

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("行程設定")
    dest = st.text_input("目的地機場", value="PRG")
    s2_date = st.date_input("第二段出發日 (飛歐洲)", value=datetime(2026, 6, 10))
    outstations = st.multiselect("選擇比價外站", ["HKG", "KUL", "BKK", "SIN"], default=["HKG", "KUL"])

# --- 核心搜尋函式 ---
def fetch_flight(origin, destination, date):
    url = f"https://{HOST}/v1/flights/search-onedate"
    params = {
        "fromEntityId": origin,
        "toEntityId": destination,
        "departDate": date.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "locale": "zh-TW"
    }
    headers = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": HOST}
    res = requests.get(url, headers=headers, params=params)
    return res.json()

# --- 執行搜尋 ---
if st.button("開始執行四段票交叉比價"):
    for station in outstations:
        st.subheader(f"📍 從 {station} 出發的方案")
        with st.spinner(f"正在抓取 {station} 數據..."):
            data = fetch_flight("TPE", dest, s2_date) # 這裡以 S2 為範例
            
            if data.get('status') and 'itineraries' in data:
                # 只取前三個最便宜的方案
                results = data['itineraries']['buckets'][0]['items'][:3]
                for flight in results:
                    price = flight['price']['formatted']
                    airline = flight['legs'][0]['carriers']['marketing'][0]['name']
                    st.info(f"💰 價格：{price} | 航空公司：{airline}")
            else:
                st.warning(f"暫時找不到從 {station} 出發的有效航線。")
