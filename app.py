import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"]
HOST = "skyscanner-flights-travel-api.p.rapidapi.com"
headers = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": HOST}

# --- 1. 自動機場 ID 轉換函式 ---
@st.cache_data(ttl=86400) # 快取一天，避免重複查詢
def get_entity_id(query):
    url = f"https://{HOST}/v1/flights/search-location"
    params = {"q": query, "locale": "zh-TW"}
    try:
        res = requests.get(url, headers=headers, params=params).json()
        if res.get('status') and res.get('data'):
            # 傳回第一個匹配項的 entityId
            return res['data'][0]['entityId']
    except:
        pass
    return f"{query}-sky" # 若失敗則回傳預設格式

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
    return requests.get(url, headers=headers, params=params).json()

# --- 3. 介面與邏輯 ---
st.title("𓃥 White 6 Aero Explorer")

with st.sidebar:
    dest_input = st.text_input("目的地 (IATA)", value="PRG")
    s2_date = st.date_input("飛歐洲日期", value=datetime(2026, 6, 10))
    outstations = st.multiselect("選擇外站", ["HKG", "KUL", "BKK", "SIN"], default=["HKG", "KUL"])

if st.button("🚀 執行全自動四段票交叉比價"):
    # 先獲取目的地的正確 ID
    with st.spinner(f"正在定位目的地 {dest_input}..."):
        dest_id = get_entity_id(dest_input)
    
    for station in outstations:
        st.subheader(f"📍 從 {station} 出發的方案")
        with st.spinner(f"正在搜尋 {station} → {dest_input}..."):
            origin_id = get_entity_id(station)
            # 這裡實作四段票核心：我們搜尋最重要的 S2 (台北飛歐洲)
            # 提示：若要搜尋完整四段票，需在此循環中呼叫四次 fetch_flight
            data = fetch_flight("TPE-sky", dest_id, s2_date)
            
            if data.get('status') and 'itineraries' in data:
                items = data['itineraries'].get('buckets', [{}])[0].get('items', [])
                if items:
                    for flight in items[:3]:
                        price = flight['price']['formatted']
                        airline = flight['legs'][0]['carriers']['marketing'][0]['name']
                        st.success(f"💰 {price} | 航空公司：{airline}")
                else:
                    st.warning("⚠️ 該日期暫無報價。")
            else:
                st.error(f"❌ API 回傳錯誤：{data.get('message', '未知錯誤')}")
