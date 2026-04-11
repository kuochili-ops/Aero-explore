import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 搜尋函式 ---
def search_google_flights(dep, arr, date_obj):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "api_key": SERP_API_KEY,
        "type": "2"  # 單程搜尋
    }
    try:
        res = requests.get(url, params=params).json()
        return res.get("best_flights", []) + res.get("other_flights", [])
    except:
        return []

# --- 介面設計 ---
st.title("𓃥 White 6 Aero Explorer: 四段票範圍搜尋")

with st.sidebar:
    st.header("🔍 目的地與日期範圍")
    dest_iata = st.text_input("目的地機場代碼", value="PRG")
    
    # 設定 S2 的期望範圍
    today = datetime.today().date()
    start_s2 = st.date_input("S2 期望開始日期", value=today + timedelta(days=61))
    end_s2 = st.date_input("S2 期望結束日期", value=start_s2 + timedelta(days=3))
    
    st.info(f"S1 將自動設定在 S2 之前 60 天 (需晚於今日)")
    stations = ["HKG", "KUL", "BKK", "SIN"]

# --- 執行比對 ---
if st.button("🚀 執行全自動日期範圍比價"):
    # 計算日期清單
    date_range = [start_s2 + timedelta(days=x) for x in range((end_s2 - start_s2).days + 1)]
    
    results_list = []
    
    progress_bar = st.progress(0)
    for i, s2_date in enumerate(date_range):
        # 航空公司規則校驗：S1 必須在今日之後
        s1_date = s2_date - timedelta(days=60)
        if s1_date <= today:
            st.warning(f"跳過日期 {s2_date}: 其 S1 ({s1_date}) 早於今日。")
            continue
            
        for station in stations:
            with st.spinner(f"搜尋 {s2_date} | 外站: {station}..."):
                # 搜尋核心 S2 航段
                flights = search_google_flights("TPE", dest_iata, s2_date)
                
                if flights:
                    f = flights[0] # 取最優一筆
                    results_list.append({
                        "S2日期": s2_date,
                        "外站": station,
                        "航空公司": f['flights'][0]['airline'],
                        "S2價格": f.get('price', 0),
                        "S1預計日期": s1_date,
                        "S4預計日期": s2_date + timedelta(days=120)
                    })
        progress_bar.progress((i + 1) / len(date_range))

    # --- 結果呈現 ---
    if results_list:
        df = pd.DataFrame(results_list)
        
        st.subheader("📊 交叉比對分析表")
        # 依照日期與價格排序
        df_sorted = df.sort_values(by=["S2價格", "S2日期"])
        st.dataframe(df_sorted.style.highlight_min(axis=0, subset=['S2價格'], color='lightgreen'))
        
        st.subheader("💡 航空公司四段票規則建議")
        best_deal = df_sorted.iloc[0]
        st.success(f"""
            **最優推薦組合：**
            * **外站推薦**：從 **{best_deal['外站']}** 啟動 S1
            * **關鍵 S2 日期**：**{best_deal['S2日期']}**
            * **S2 報價**：TWD {best_deal['S2價格']:,}
            * **航空公司**：{best_deal['航空公司']}
            * **S1 必須在 {best_deal['S1預計日期']} 前完成開票。**
        """)
    else:
        st.error("此範圍內暫無有效數據，請擴大日期範圍或更換目的地。")

st.divider()
st.caption("𓃥 White 6 Studio | 2026 旅遊自動化 | 符合航空公司四段票時間邏輯")
