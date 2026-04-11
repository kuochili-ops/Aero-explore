import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# --- 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

# 安全讀取金鑰
if "RAPIDAPI_KEY" not in st.secrets:
    st.error("請在 Streamlit Secrets 中設定 RAPIDAPI_KEY")
    st.stop()

RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"]
HOST = "skyscanner-flights-travel-api.p.rapidapi.com"
headers = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": HOST}

# --- 1. 智慧地點搜尋函式 ---
def search_location(query):
    """
    輸入城市名或代碼，自動回傳 Skyscanner 內部的 entityId
    """
    url = f"https://{HOST}/v1/flights/search-location"
    params = {"q": query, "locale": "zh-TW"}
    try:
        res = requests.get(url, headers=headers, params=params).json()
        if res.get('status') and res.get('data'):
            return res['data']
    except:
        pass
    return []

# --- 2. 機票搜尋函式 ---
def fetch_flight(from_id, to_id, date_obj):
    url = f"https://{HOST}/v1/flights/search-onedate"
    params = {
        "fromEntityId": from_id,
        "toEntityId": to_id,
        "departDate": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "locale": "zh-TW",
        "market": "TW"
    }
    # 這裡必須保持正確縮排，且前後無雜質
    time.sleep(1.5) 
    return requests.get(url, headers=headers, params=params).json()

# --- 3. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")

with st.sidebar:
    st.header("🔍 地點智慧比對")
    dest_query = st.text_input("輸入目的地 (例如: Prague 或 PRG)", value="Prague")
    
    loc_options = search_location(dest_query)
    if loc_options:
        selection = st.selectbox(
            "請選擇正確的機場地點",
            options=loc_options,
            format_func=lambda x: f"{x['presentation']['title']} ({x.get('iataCode', '無代碼')})"
        )
        dest_id = selection['entityId']
        st.success(f"已鎖定 ID: {dest_id}")
    else:
        dest_id = f"{dest_query}-sky"
        st.warning("找不到比對，將使用預設格式")

    s2_date = st.date_input("飛歐洲日期", value=datetime(2026, 6, 10))
    outstations_raw = st.multiselect("選擇外站", ["HKG", "KUL", "BKK", "SIN"], default=["HKG", "KUL"])

# --- 4. 執行邏輯 ---
if st.button("🚀 執行全自動交叉比價"):
    for station in outstations_raw:
        st.subheader(f"📍 從 {station} 出發的方案")
        
        with st.spinner(f"正在分析 {station}..."):
            station_results = search_location(station)
            origin_id = station_results[0]['entityId'] if station_results else f"{station}-sky"
            
            # 目前以台北為基準搜尋 S2 航段
            data = fetch_flight("TPE-sky", dest_id, s2_date)
            
            if data.get('status') == True:
                items = data.get('itineraries', {}).get('buckets', [{}])[0].get('items', [])
                if items:
                    for flight in items[:3]:
                        price = flight['price']['formatted']
                        airline = flight['legs'][0]['carriers']['marketing'][0]['name']
                        st.success(f"💰 {price} | {airline}")
                else:
                    st.warning("⚠️ 該日期暫無報價。")
            else:
                error_msg = data.get('message', '請稍候再試')
                st.error(f"❌ API 錯誤：{error_msg}")

st.divider()
st.caption("𓃥 White 6 Studio - 智慧比對功能已修正")
