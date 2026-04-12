import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 搜尋函式 ---
def search_flights(dep, arr, date_obj):
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

# --- 3. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("正規四段票全自動掃描 (涵蓋中國、日本、東南亞)")

col1, col2 = st.columns(2)
with col1:
    dest_q = st.text_input("🎯 輸入長程目的地 (如: Prague)", value="Prague")
with col2:
    today = datetime.today().date()
    s2_date = st.date_input("📅 預計 S2 出發日期", value=today + timedelta(days=61), min_value=today + timedelta(days=61))

# --- 4. 核心邏輯：全自動掃描 ---
if st.button("🚀 執行全外站自動掃描並排序"):
    # 自動遍歷所有外站區域
    scan_list = {
        "中國": ["PVG", "PEK", "CAN", "SZX", "XMN"], # 上海、北京、廣州、深圳、廈門
        "日本/韓國": ["NRT", "KIX", "ICN"],
        "東南亞": ["KUL", "BKK", "SIN", "HKG"]
    }
    
    tpe_hub = "TPE"
    all_data = []
    
    # 日期計算
    s1_d, s3_d, s4_d = s2_date-timedelta(days=60), s2_date+timedelta(days=10), s2_date+timedelta(days=120)

    # 執行掃描
    stations = [item for sublist in scan_list.values() for item in sublist]
    bar = st.progress(0)
    
    for i, stn in enumerate(stations):
        with st.spinner(f"正在分析外站：{stn}..."):
            # 搜尋 S2 段價格
            results = search_flights(tpe_hub, dest_q, s2_date)
            
            if results:
                f = results[0]
                all_data.append({
                    "價格 (TWD)": f.get('price', 0),
                    "啟動外站": stn,
                    "航空公司": f['flights'][0]['airline'],
                    "S1 (啟動)": s1_d,
                    "S2 (長程)": s2_date,
                    "S3 (回程)": s3_d,
                    "S4 (結尾)": s4_d,
                    "地區": [k for k, v in scan_list.items() if stn in v][0]
                })
        bar.progress((i + 1) / len(stations))

    # --- 5. 結果呈現與排序 ---
    if all_data:
        df = pd.DataFrame(all_data)
        st.success("✅ 掃描完成！請點擊下表欄位標題進行排序。")
        
        # 顯示可排序表格
        st.dataframe(
            df.sort_values(by="價格 (TWD)"), 
            use_container_width=True,
            column_config={
                "價格 (TWD)": st.column_config.NumberColumn(format="TWD %d"),
            }
        )

        st.subheader("📝 四段票航空公司開票要件 (中國外站版)")
        st.info(f"""
        **【實戰要件註記】**
        - **證件要件**：若外站設在中國大陸 (如上海 PVG)，S1 與 S4 段需準備有效之**台胞證**。
        - **航向規則**：機票必須由「外站」發出，經台灣中停後飛往長程目的地。
        - **行李要件**：回程 (S3) 返抵 {tpe_hub} 時，務必向地勤確認行李「不直掛」至外站。
        - **開票檢查**：S1 啟動日 ({s1_d}) 絕對不可早於今日。
        """)
    else:
        st.error("搜尋未果，請嘗試調整日期或確認目的地名稱。")

st.divider()
st.caption("𓃥 White 6 Studio | 全球外站掃描系統 | 支持中國一線城市 Hub 比價")
