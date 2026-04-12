import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 頁面基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

# 安全讀取 SerpApi 金鑰
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 核心功能函式 ---

def get_location_suggestions(query):
    """輸入提示：鍵入第一個字母即跳出全球機場選單"""
    if len(query) < 1: return []
    url = f"https://autocomplete.travelpayouts.com/places2?term={query}&locale=en&types[]=airport&types[]=city"
    try:
        return requests.get(url).json()
    except:
        return []

def search_google_flights(dep, arr, date_obj):
    """Google Flights 搜尋引擎"""
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "hl": "zh-tw",
        "api_key": SERP_API_KEY,
        "type": "2"  # 強制單程搜尋
    }
    try:
        res = requests.get(url, params=params).json()
        return res.get("best_flights", []) + res.get("other_flights", [])
    except:
        return []

# --- 3. 側邊欄：參數設定 ---

with st.sidebar:
    st.header("🔍 目的地智慧選擇")
    # 鍵入提示功能
    dest_q = st.text_input("鍵入目的地 (如: P...)", value="Prague")
    suggestions = get_location_suggestions(dest_q)
    
    if suggestions:
        selected_dest = st.selectbox(
            "請從選單選擇正確機場：",
            options=suggestions,
            format_func=lambda x: f"{x['name']} ({x['code']}) - {x['country_name']}"
        )
        dest_iata = selected_dest['code']
    else:
        dest_iata = "PRG"
        st.caption("請輸入英文字母以啟動提示選單")

    st.divider()
    st.header("📅 S2 期望出發日期範圍")
    today = datetime.today().date()
    
    # 航空公司規則：S1 (回台段) 必須在今日之後
    # 假設 S1 預設在 S2 之前 60 天，則 S2 的最小值應為今日 + 61 天
    min_s2 = today + timedelta(days=61)
    
    start_s2 = st.date_input("範圍開始日", value=min_s2, min_value=min_s2)
    end_s2 = st.date_input("範圍結束日", value=start_s2 + timedelta(days=3))
    
    st.info(f"💡 系統已自動校驗：S1 日期將晚於今日 ({today})，符合開票規則。")

# --- 4. 主畫面：規則呈現 ---

st.title("𓃥 White 6 Aero Explorer")

# 計算日期矩陣
s2_dates = [start_s2 + timedelta(days=x) for x in range((end_s2 - start_s2).days + 1)]
target_stations = ["HKG", "KUL", "BKK", "SIN"]

st.markdown("### ✈️ 四段票航空公司規則預覽 (以首日為例)")
example_s2 = s2_dates[0]
r_cols = st.columns(4)
r_cols[0].metric("S1 (啟動航段)", (example_s2 - timedelta(days=60)).strftime("%m/%d"), "外站→TPE")
r_cols[1].metric("S2 (期望航段)", example_s2.strftime("%m/%d"), "TPE→歐洲")
r_cols[2].metric("S3 (中停回程)", (example_s2 + timedelta(days=10)).strftime("%m/%d"), "歐洲→TPE")
r_cols[3].metric("S4 (結尾航段)", (example_s2 + timedelta(days=120)).strftime("%m/%d"), "TPE→外站")

# --- 5. 執行比價 ---

if st.button("🚀 執行全自動日期範圍比價"):
    all_results = []
    
    for s2_d in s2_dates:
        for station in target_stations:
            with st.spinner(f"正在分析 {s2_d} | 外站 {station}..."):
                # 核心比價：搜尋 S2 (台北-歐洲) 在不同日期的表現
                flights = search_google_flights("TPE", dest_iata, s2_d)
                
                if flights:
                    f = flights[0] # 取最優
                    all_results.append({
                        "S2 出發日期": s2_d,
                        "出發外站": station,
                        "航空公司": f['flights'][0]['airline'],
                        "S2 單程價格": f.get('price', 0),
                        "S1 預計日": s2_d - timedelta(days=60),
                        "S4 預計日": s2_d + timedelta(days=120)
                    })
    
    if all_results:
        df = pd.DataFrame(all_results)
        
        st.subheader("📊 四段票交叉比對矩陣")
        # 價格格式化與排序
        df_display = df.sort_values(by=["S2 單程價格", "S2 出發日期"])
        st.dataframe(
            df_display.style.highlight_min(subset=['S2 單程價格'], color='#2e7d32'),
            use_container_width=True
        )
        
        st.success("✅ 比對完成！綠色標記為您期望範圍內的最低價組合。")
    else:
        st.error("暫無有效數據，請嘗試更換日期範圍。")

st.divider()
st.caption("𓃥 White 6 Studio | 目的地自動補完引擎 | 航空公司四段票邏輯校準版")
