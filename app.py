import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 頁面配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 核心功能：地點搜尋與飛行搜尋 ---

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
        "type": "2" # 單程搜尋
    }
    try:
        res = requests.get(url, params=params).json()
        # 回傳最優機票
        return (res.get("best_flights", []) + res.get("other_flights", []))[:1]
    except: return []

# --- 3. 介面設計：規則設定 ---

st.title("𓃥 White 6 Aero Explorer")
st.subheader("正規四段票自動化比價系統")

with st.sidebar:
    st.header("📍 航點設定")
    # 台灣出發地選單
    tpe_origin = st.selectbox("台灣出發地", ["TPE", "TSA", "RMQ", "KHH"], index=0)
    
    # 外站設定
    station = st.selectbox("外站啟動點", ["HKG", "KUL", "BKK", "SIN", "NRT"], index=1)
    
    # 目的地提示選單 (S2)
    st.divider()
    dest_q = st.text_input("輸入目的地 (S2)", value="Prague")
    s2_hints = get_location_suggestions(dest_q)
    dest_iata = st.selectbox("確認 S2 目的地：", options=s2_hints, format_func=lambda x: f"{x['name']} ({x['code']})")['code'] if s2_hints else "PRG"
    
    # 鄰近回程城市提示 (S3)
    dest_q_s3 = st.text_input("輸入回程城市 (S3，可選鄰近)", value=dest_q)
    s3_hints = get_location_suggestions(dest_q_s3)
    s3_origin_iata = st.selectbox("確認 S3 起點：", options=s3_hints, format_func=lambda x: f"{x['name']} ({x['code']})")['code'] if s3_hints else dest_iata

    st.divider()
    st.header("📅 日期範圍 (S2)")
    today = datetime.today().date()
    start_s2 = st.date_input("S2 開始日", value=today + timedelta(days=61), min_value=today + timedelta(days=2))
    end_s2 = st.date_input("S2 結束日", value=start_s2 + timedelta(days=3))

# --- 4. 邏輯呈現：航段拆解 ---

s2_dates = [start_s2 + timedelta(days=x) for x in range((end_s2 - start_s2).days + 1)]

st.info(f"🔍 正在規劃：從 **{station}** 啟動，經 **{tpe_origin}** 前往 **{dest_iata}**，並從 **{s3_origin_iata}** 返回。")

# --- 5. 執行搜尋與結果展示 ---

if st.button("🚀 執行四段票全自動交叉搜尋"):
    final_data = []
    
    for s2_d in s2_dates:
        # 自動推算符合航司規則的四段日期
        s1_d = s2_d - timedelta(days=60)
        s3_d = s2_d + timedelta(days=10)
        s4_d = s2_d + timedelta(days=120)
        
        # 規則校驗：S1 必須在今日之後
        if s1_d <= today:
            st.warning(f"跳過日期 {s2_d}: 其 S1 ({s1_d}) 不符合『今日之後』規則。")
            continue

        with st.spinner(f"正在分析日期組合：{s2_d}..."):
            # 搜尋最關鍵的 S2 航段價格
            s2_flights = search_google_flights(tpe_origin, dest_iata, s2_d)
            
            if s2_flights:
                f = s2_flights[0]
                final_data.append({
                    "S2日期": s2_d,
                    "航空公司": f['flights'][0]['airline'],
                    "S2價格 (TPE-Dest)": f.get('price', 0),
                    "S1日期 (外站-TPE)": s1_d,
                    "S3日期 (回程)": s3_d,
                    "S4日期 (回外站)": s4_d,
                    "目的地組合": f"{dest_iata} / {s3_origin_iata}"
                })

    if final_data:
        df = pd.DataFrame(final_data)
        st.subheader("📊 四段票實戰比價矩陣")
        
        # 呈現完整航段日誌
        st.dataframe(
            df.style.highlight_min(subset=['S2價格 (TPE-Dest)'], color='#1b5e20'),
            use_container_width=True
        )
        
        st.success("✅ 搜尋完成。價格以 TPE 出發之關鍵長程段 (S2) 為基準呈現。")
    else:
        st.error("此範圍內暫無數據，請嘗試調整日期。")

st.divider()
st.caption(f"𓃥 White 6 Studio | 四段票定義：S1({station}→{tpe_origin}) > S2({tpe_origin}→{dest_iata}) > S3({s3_origin_iata}→{tpe_origin}) > S4({tpe_origin}→{station})")
