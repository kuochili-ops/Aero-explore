import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# --- 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"]
HOST = "skyscanner-flights-travel-api.p.rapidapi.com"
headers = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": HOST}

# --- 1. 機場 ID 轉換 (加入快取避免浪費額度) ---
@st.cache_data(ttl=86400)
def get_entity_id(query):
    url = f"https://{HOST}/v1/flights/search-location"
    params = {"q": query, "locale": "zh-TW"}
    try:
        # 為了保險，這裡也加一點緩衝
        time.sleep(0.5)
        res = requests.get(url, headers=headers, params=params).json()
        if res.get('status') and res.get('data'):
            return res['data'][0]['entityId']
    except:
        pass
    return f"{query}-sky"

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

# --- 3. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")

with st.sidebar:
    st.header("⚙️ 搜尋設定")
    dest_input = st.text_input("目的地 (IATA)", value="PRG")
    s2_date = st.date_input("飛歐洲日期", value=datetime(2026, 6, 10))
    outstations = st.multiselect("選擇外站", ["HKG", "KUL", "BKK", "SIN"], default=["HKG", "KUL"])
    st.info("提示：免費版 API 頻率有限，搜尋多個外站時請稍候。")

# --- 4. 執行邏輯 ---
if st.button("🚀 執行全自動四段票交叉比價"):
    # 第一步：先抓目的地 ID (只抓一次)
    with st.spinner(f"正在定位目的地 {dest_input}..."):
        dest_id = get_entity_id(dest_input)
    
    # 第二步：遍歷外站
    for station in outstations:
        st.subheader(f"📍 從 {station} 出發的方案")
        
        with st.spinner(f"正在搜尋 {station} → {dest_input}..."):
            # 獲取外站 ID
            origin_id = get_entity_id(station)
            
            # 💡 關鍵優化：在搜尋前先睡 1.5 秒，避開 Too Many Requests
            time.sleep(1.5)
            
            data = fetch_flight("TPE-sky", dest_id, s2_date) # 您目前的邏輯是看 S2
            
            if data.get('status') == True:
                items = data.get('itineraries', {}).get('buckets', [{}])[0].get('items', [])
                if items:
                    for flight in items[:3]:
                        price = flight['price']['formatted']
                        airline = flight['legs'][0]['carriers']['marketing'][0]['name']
                        st.success(f"💰 {price} | 航空公司：{airline}")
                else:
                    st.warning("⚠️ 該日期暫無報價，請嘗試更換日期。")
            elif data.get('message') == "Too many requests":
                st.error("🛑 API 頻率過高，請等 10 秒後再試一次。")
            else:
                st.error(f"❌ 發生錯誤：{data.get('message', '未知錯誤')}")

st.divider()
st.caption("𓃥 White 6 Studio - 2026 旅遊自動化工具")
