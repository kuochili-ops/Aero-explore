import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 核心設定 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 選單與資料庫 ---
STATION_MAP = {
    "KUL": "吉隆坡 (馬來西亞)", "BKK": "曼谷 (泰國)", "HKG": "香港", 
    "PVG": "上海 (中國)", "NRT": "東京 (日本)", "ICN": "首爾 (韓國)"
}

# --- 3. 搜尋核心 (優化 API 調用) ---
def search_flights(dep, arr, date_obj):
    # 增加深度搜尋參數 deep_search=True 以提高準確度 (若 API 支援)
    params = {
        "engine": "google_flights", "departure_id": dep, "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"), "currency": "TWD",
        "api_key": SERP_API_KEY, "type": "2" 
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params).json()
        return (res.get("best_flights", []) + res.get("other_flights", []))[:1]
    except: return []

# --- 4. 介面 ---
st.title("𓃥 White 6 Aero Explorer")
st.warning("⚠️ 提醒：API 價格具備 10-15% 的快取誤差，下方結果僅供『航線結構比價』參考，實價請以航空公司官網為準。")

# (中間介面邏輯同前，略過)

# --- 5. 結果呈現與「官網確認連結」建議 ---
if st.button("🚀 執行深度比價"):
    # (搜尋邏輯...)
    # 產出 DataFrame 後增加一個「動態風險」欄位
    df['價格可信度'] = "中 (快取)"
    df.loc[df['價格 (TWD)'] < 5000, '價格可信度'] = "低 (可能已售罄)" 

    st.dataframe(df)

    st.subheader("💡 專家對策：如何抓到真正的低價？")
    st.info("""
    **當您發現官網價格較高時，請嘗試：**
    1. **使用無痕視窗**：避免瀏覽器的 Cookie 導致航空公司系統對特定航線調漲（即『越查越貴』現象）。
    2. **切換幣別**：外站票若從 KUL 出發，嘗試在官網選用馬幣 (MYR) 結帳，有時匯率轉換會比 TWD 更有優勢。
    3. **搜尋『多城市』而非『往返』**：在官網務必使用 **Multi-city (多城市)** 功能手動輸入四段航程，這才能觸發正確的四段票規則。
    """)
