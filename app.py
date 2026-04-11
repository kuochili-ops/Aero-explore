import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# --- 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"]
HOST = "skyscanner-flights-travel-api.p.rapidapi.com"
headers = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": HOST}

# --- 1. 智慧地點搜尋函式 ---
def search_location(query):
    """
    [span_3](start_span)輸入城市名或代碼，自動回傳 Skyscanner 內部的 entityId[span_3](end_span)
    """
    url = f"https://{HOST}/v1/flights/search-location"
    params = {"q": query, "locale": "zh-TW"}
    try:
        res = requests.get(url, headers=headers, params=params).json()
        if res.get('status') and res.get('data'):
            # 回傳格式：{ 'name': '香港', 'entityId': '27544008', 'iataCode': 'HKG' }
            return res['data']
    except:
        pass
    return []

# --- 2. 機票搜尋函式 (包含頻率控制) ---
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
    [span_4](start_span)time.sleep(1.5) # 避開 Too many requests 錯誤[span_4](end_span)
    return requests.get(url, headers=headers, params=params).json()

# --- 3. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")

with st.sidebar:
    st.header("🔍 地點智慧比對")
    # [span_5](start_span)使用者輸入關鍵字[span_5](end_span)
    dest_query = st.text_input("輸入目的地 (例如: Prague 或 PRG)", value="Prague")
    
    # [span_6](start_span)自動比對地點並顯示下拉選單[span_6](end_span)
    loc_options = search_location(dest_query)
    if loc_options:
        # [span_7](start_span)讓使用者從比對結果中選擇正確的機場[span_7](end_span)
        selection = st.selectbox(
            "請選擇正確的機場地點",
            options=loc_options,
            format_func=lambda x: f"{x['presentation']['title']} ({x.get('iataCode', '無代碼')})"
        )
        dest_id = selection['entityId']
        st.success(f"已鎖定 ID: {dest_id}")
    else:
        dest_id = f"{dest_query}-sky"
        st.warning("找不到精確比對，將嘗試使用預設代碼。")

    s2_date = st.date_input("飛歐洲日期", value=datetime(2026, 6, 10))
    outstations_raw = st.multiselect("選擇外站 (可多選)", ["HKG", "KUL", "BKK", "SIN"], default=["HKG", "KUL"])

# --- 4. 執行邏輯 ---
if st.button("🚀 執行全自動交叉比價"):
    for station in outstations_raw:
        st.subheader(f"📍 從 {station} 出發的方案")
        
        with st.spinner(f"正在分析 {station} → {selection['presentation']['title']}..."):
            # [span_8](start_span)[span_9](start_span)獲取外站的 ID[span_8](end_span)[span_9](end_span)
            station_results = search_location(station)
            origin_id = station_results[0]['entityId'] if station_results else f"{station}-sky"
            
            # [span_10](start_span)執行搜尋[span_10](end_span)
            data = fetch_flight("TPE-sky", dest_id, s2_date) # 預設以台北為基準 S2 航段
            
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
                st.error(f"❌ API 限制或錯誤：{data.get('message', '請稍候再試')}")

st.divider()
st.caption("𓃥 White 6 Studio - 自動比對 IATA 功能已啟動")
