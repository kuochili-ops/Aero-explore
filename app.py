import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 頁面配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 核心搜尋與提示功能 ---

def get_location_suggestions(query):
    if len(query) < 1: return []
    url = f"https://autocomplete.travelpayouts.com/places2?term={query}&locale=en&types[]=airport&types[]=city"
    try:
        return requests.get(url).json()
    except: return []

def search_google_flights(dep, arr, date_obj):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "api_key": SERP_API_KEY,
        "type": "2" 
    }
    try:
        res = requests.get(url, params=params).json()
        return (res.get("best_flights", []) + res.get("other_flights", []))[:1]
    except: return []

# --- 3. 側邊欄：Open-Jaw 與四段規則設定 ---

with st.sidebar:
    st.header("📍 台灣 Hub 與外站")
    tpe_hub = st.selectbox("台灣機場", ["TPE", "TSA", "KHH", "RMQ"], index=0)
    
    station_q = st.text_input("輸入啟動外站 (如: KUL)", value="KUL")
    s_hints = get_location_suggestions(station_q)
    station_iata = st.selectbox("確認外站：", options=s_hints, format_func=lambda x: f"{x['name']} ({x['code']})")['code'] if s_hints else station_q.upper()

    st.divider()
    st.header("✈️ Open-Jaw 航點設定")
    
    # 去程目的地 (S2)
    s2_q = st.text_input("去程目的地 (S2 Arrival)", value="Prague")
    s2_hints = get_location_suggestions(s2_q)
    s2_dest = st.selectbox("確認 S2 目的地：", options=s2_hints, format_func=lambda x: f"{x['name']} ({x['code']})")['code'] if s2_hints else "PRG"
    
    # 回程起點 (S3) - 實作 Open-Jaw
    st.markdown("**[Open-Jaw 選項]**")
    s3_q = st.text_input("回程出發地 (S3 Departure)", value="Vienna")
    s3_hints = get_location_suggestions(s3_q)
    s3_org = st.selectbox("確認 S3 起點：", options=s3_hints, format_func=lambda x: f"{x['name']} ({x['code']})")['code'] if s3_hints else s2_dest

    st.divider()
    st.header("📅 期望日期範圍 (S2)")
    today = datetime.today().date()
    start_s2 = st.date_input("S2 開始日", value=today + timedelta(days=61), min_value=today + timedelta(days=2))
    end_s2 = st.date_input("S2 結束日", value=start_s2 + timedelta(days=3))

# --- 4. 主畫面：Open-Jaw 規則呈現 ---

st.title("𓃥 White 6 Aero Explorer")

is_open_jaw = s2_dest != s3_org
oj_status = "✅ 已啟動 Open-Jaw" if is_open_jaw else "標準來回"
st.subheader(f"正規四段票架構 - {oj_status}")

# 預覽四段結構
s1_d, s2_d, s3_d, s4_d = start_s2-timedelta(days=60), start_s2, start_s2+timedelta(days=10), start_s2+timedelta(days=120)

st.code(f"""
[四段票 Open-Jaw 航程註記]
1st: {station_iata} ➔ {tpe_hub} | {s1_d}
2nd: {tpe_hub} ➔ {s2_dest} | {s2_d} (去程進)
3rd: {s3_org} ➔ {tpe_hub} | {s3_d} (回程出 - Open Jaw: {is_open_jaw})
4th: {tpe_hub} ➔ {station_iata} | {s4_d}
""", language="markdown")

# --- 5. 執行搜尋與比價 ---

if st.button("🚀 執行 Open-Jaw 全自動比價"):
    s2_dates = [start_s2 + timedelta(days=x) for x in range((end_s2 - start_s2).days + 1)]
    final_results = []
    
    for d in s2_dates:
        with st.spinner(f"分析日期 {d}..."):
            # 在 Open-Jaw 模式下，價格通常以去程 S2 價格為主要浮動參考
            res = search_google_flights(tpe_hub, s2_dest, d)
            if res:
                f = res[0]
                final_results.append({
                    "S2 出發日期": d,
                    "航空公司": f['flights'][0]['airline'],
                    "S2 價格 (去程)": f.get('price', 0),
                    "Open-Jaw 航點": f"{s2_dest} 進 / {s3_org} 出",
                    "S1 (外站回台)": d - timedelta(days=60),
                    "S3 (歐洲回台)": d + timedelta(days=10),
                    "S4 (送回外站)": d + timedelta(days=120)
                })

    if final_results:
        df = pd.DataFrame(final_results)
        st.subheader("📊 交叉比對矩陣")
        st.dataframe(
            df.sort_values("S2 價格 (去程)").style.highlight_min(subset=['S2 價格 (去程)'], color='#1b5e20'),
            use_container_width=True
        )
        st.success(f"✅ 比對完成。已將 {s2_dest} 與 {s3_org} 的不同點進出邏輯納入註記。")
    else:
        st.error("此範圍內無數據。")

st.divider()
st.caption("𓃥 White 6 Studio | 支持 Open-Jaw 不同點進出 | 航空公司規則：S1 > 今天")
