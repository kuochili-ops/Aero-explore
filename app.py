import streamlit as st
import requests
import time
from datetime import datetime

# --- 配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

# 安全讀取金鑰 (請在 Secrets 加入這些 Key)
RAPID_API_KEY = st.secrets.get("RAPIDAPI_KEY")
AMADEUS_KEY = st.secrets.get("AMADEUS_KEY") # 備援方案
AMADEUS_SECRET = st.secrets.get("AMADEUS_SECRET")

HOST = "skyscanner-flights-travel-api.p.rapidapi.com"
headers = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": HOST}

# --- 1. 智慧地點提示 (優化頻率) ---
def get_location_suggestions(query):
    if len(query) < 2: return []
    url = f"https://{HOST}/v1/flights/search-location"
    params = {"q": query, "locale": "zh-TW"}
    try:
        # 僅在特定動作觸發，減少 Auto-request
        res = requests.get(url, headers=headers, params=params).json()
        return res.get('data', [])
    except:
        return []

# --- 2. 核心搜尋與頻率控制 ---
def fetch_flight_safe(from_id, to_id, date_obj):
    url = f"https://{HOST}/v1/flights/search-onedate"
    params = {
        "fromEntityId": from_id, "toEntityId": to_id,
        "departDate": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD", "locale": "zh-TW", "market": "TW"
    }
    # 強制等待 2 秒避開頻率限制
    time.sleep(2.0) 
    return requests.get(url, headers=headers, params=params).json()

# --- 3. 介面介面 ---
st.title("𓃥 White 6 Aero Explorer")

with st.sidebar:
    st.header("🔍 地點智慧提示")
    # 使用者手動輸入後，按「搜尋城市」才觸發 API
    city_input = st.text_input("輸入城市關鍵字 (如: Prag)", value="Prague")
    
    if st.button("🔎 比對機場代碼"):
        with st.spinner("比對中..."):
            suggestions = get_location_suggestions(city_input)
            st.session_state['loc_options'] = suggestions

    # 如果有比對結果，顯示選單
    if 'loc_options' in st.session_state and st.session_state['loc_options']:
        selection = st.selectbox(
            "請確認目的地機場：",
            options=st.session_state['loc_options'],
            format_func=lambda x: f"{x['presentation']['title']} ({x.get('iataCode', '無代碼')})"
        )
        st.session_state['dest_id'] = selection['entityId']
        st.success(f"已鎖定: {selection['presentation']['title']}")
    else:
        st.session_state['dest_id'] = "PRG-sky"

    s2_date = st.date_input("飛歐洲日期", value=datetime(2026, 6, 10))
    outstations = st.multiselect("外站比價", ["HKG", "KUL", "BKK", "SIN"], default=["HKG"])

# --- 4. 執行比價 ---
if st.button("🚀 啟動全自動交叉比價"):
    if 'dest_id' not in st.session_state:
        st.error("請先點擊『比對機場代碼』確認目的地。")
    else:
        for station in outstations:
            st.subheader(f"📍 從 {station} 出發")
            with st.spinner(f"正在搜尋 {station} 的最佳組合..."):
                data = fetch_flight_safe("TPE-sky", st.session_state['dest_id'], s2_date)
                
                if data.get('status') == True:
                    items = data.get('itineraries', {}).get('buckets', [{}])[0].get('items', [])
                    if items:
                        for flight in items[:2]:
                            st.success(f"💰 {flight['price']['formatted']} | {flight['legs'][0]['carriers']['marketing'][0]['name']}")
                    else:
                        st.warning("此段無報價。")
                elif data.get('message') == "Too many requests":
                    st.error("🛑 頻率受限！請等待 1 分鐘後再試。建議申請 Amadeus API 作為備援。")
                else:
                    st.error(f"錯誤：{data.get('message', 'API 暫時無法回應')}")
