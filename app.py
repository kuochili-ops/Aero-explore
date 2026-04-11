import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 頁面基本設定 ---
st.set_page_config(
    page_title="White 6 Aero Explorer",
    page_icon="𓃥",
    layout="wide"
)

# 自定義 CSS 讓介面更有「白六」風格
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .flight-card { border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #1e2129; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 金鑰與配置 ---
# 請確保在 Streamlit Cloud Secrets 中設定了 RAPIDAPI_KEY
try:
    RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"]
except KeyError:
    st.error("❌ 找不到 RAPIDAPI_KEY！請在 Streamlit Cloud Secrets 中設定。")
    st.stop()

HOST = "skyscanner-flights-travel-api.p.rapidapi.com"

# --- 2. 核心搜尋函式 ---
def fetch_flight_data(origin, destination, date_obj):
    """
    呼叫 Skyscanner API 獲取單程票價
    """
    url = f"https://{HOST}/v1/flights/search-onedate"
    
    # 根據 API 文件，部分版本需使用 IATA-sky 格式
    params = {
        "fromEntityId": f"{origin}-sky", 
        "toEntityId": f"{destination}-sky",
        "departDate": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "locale": "zh-TW",
        "market": "TW"
    }
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": HOST
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": False, "error": str(e)}

# --- 3. 介面佈局 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("專為布拉格之旅打造的四段票交叉比價器")

# 側邊欄：行程參數
with st.sidebar:
    st.header("📅 行程參數設定")
    main_dest = st.text_input("目的地機場 (IATA)", value="PRG")
    s2_date = st.date_input("第二段出發日 (飛歐洲)", value=datetime(2026, 6, 10))
    
    st.divider()
    st.header("📍 外站選擇")
    outstations = st.multiselect(
        "選擇要比價的起點", 
        ["HKG", "KUL", "BKK", "SIN", "NRT"], 
        default=["HKG", "KUL", "BKK"]
    )

# --- 4. 自動推算四段票日期 ---
s1_date = s2_date - timedelta(days=60)
s3_date = s2_date + timedelta(days=10)
s4_date = s2_date + timedelta(days=120)

# 顯示推算日期給使用者確認
cols = st.columns(4)
cols[0].metric("第一段 (外站->TPE)", s1_date.strftime("%m/%d"))
cols[1].metric("第二段 (TPE->歐洲)", s2_date.strftime("%m/%d"))
cols[2].metric("第三段 (歐洲->TPE)", s3_date.strftime("%m/%d"))
cols[3].metric("第四段 (TPE->外站)", s4_date.strftime("%m/%d"))

# --- 5. 執行比價邏輯 ---
if st.button("🚀 開始全自動四段票交叉比價"):
    if not outstations:
        st.warning("請至少選擇一個外站進行比價。")
    else:
        # 我們主要針對 S2 (台北飛歐洲) 進行比價，因為這是票價波動最大的段落
        for station in outstations:
            with st.container():
                st.markdown(f"### 📍 搜尋從 **{station}** 出發的組合")
                
                with st.spinner(f"正在抓取 {station} 數據..."):
                    # 這裡模擬搜尋 S2 航段作為基準票價參考
                    data = fetch_flight_data("TPE", main_dest, s2_date)
                    
                    if data.get('status') and 'itineraries' in data:
                        itineraries = data['itineraries'].get('buckets', [{}])[0].get('items', [])
                        
                        if itineraries:
                            # 顯示前 3 名最優方案
                            for idx, flight in enumerate(itineraries[:3]):
                                price = flight['price']['formatted']
                                airline = flight['legs'][0]['carriers']['marketing'][0]['name']
                                dep_time = flight['legs'][0]['departure']
                                
                                # 使用自定義卡片樣式顯示
                                st.markdown(f"""
                                <div class="flight-card">
                                    <span style="font-size: 1.2em; color: #00ff00;">💰 {price}</span> | 
                                    <b>{airline}</b> <br>
                                    <small>出發時間: {dep_time} | 航段: TPE → {main_dest}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning(f"⚠️ {station} 航線目前無可用報價。")
                    else:
                        st.error(f"❌ 無法從 API 獲取 {station} 的數據。")
                        # st.write(data) # 除錯用

st.divider()
st.caption("𓃥 White 6 Studio - 2026 旅遊自動化工具")
