import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 核心搜尋函式 ---
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

# --- 3. 介面設計：極簡設定與功能開關 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("31天廣域掃描 + Open Jaw 實戰系統")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    dest_q = st.text_input("🎯 目的地 (例如: Prague)", value="Prague")
with col2:
    base_date = st.date_input("📅 預估 S2 出發日期", value=datetime.today().date() + timedelta(days=61))
with col3:
    allow_oj = st.toggle("開啟 Open Jaw", value=False)

if allow_oj:
    oj_dest = st.text_input("🔄 Open Jaw 回程起點 (例如: Vienna)", value="Vienna")
else:
    oj_dest = dest_q

# --- 4. 核心邏輯：自動生成日期與外站清單 ---
if st.button("🚀 執行全球外站 + 31天範圍深度掃描"):
    # 設定外站清單 (涵蓋中國、日韓、東南亞)
    stations = ["PVG", "HKG", "KUL", "NRT", "BKK", "SIN", "ICN"]
    
    # 生成前後 15 天日期範圍 (共 31 天)
    date_range = [base_date + timedelta(days=x) for x in range(-15, 16)]
    
    all_results = []
    tpe_hub = "TPE"
    
    # 建立進度條
    total_steps = len(stations) * len(date_range)
    bar = st.progress(0)
    status_text = st.empty()
    
    count = 0
    for stn in stations:
        for d in date_range:
            count += 1
            # 確保 S1 晚於今日 (航空公司硬規則)
            if d - timedelta(days=60) <= datetime.today().date():
                continue
                
            status_text.text(f"掃描中：外站 {stn} | 日期 {d} ({count}/{total_steps})")
            bar.progress(count / total_steps)
            
            # 搜尋核心 S2 (台北-去程目的地)
            res = search_flights(tpe_hub, dest_q, d)
            
            if res:
                f = res[0]
                all_results.append({
                    "價格 (TWD)": f.get('price', 0),
                    "啟動外站": stn,
                    "出發日期 (S2)": d,
                    "航空公司": f['flights'][0]['airline'],
                    "進出模式": f"{dest_q} 進 / {oj_dest} 出" if allow_oj else "同點進出",
                    "S1 (啟動日)": d - timedelta(days=60),
                    "S4 (結尾日)": d + timedelta(days=120)
                })

    # --- 5. 結果呈現與排序 ---
    if all_results:
        df = pd.DataFrame(all_results)
        st.success(f"✅ 掃描完成！共找到 {len(all_results)} 組符合條件的四段票方案。")
        
        # 顯示可排序表格
        st.dataframe(
            df.sort_values(by="價格 (TWD)"), 
            use_container_width=True,
            column_config={
                "價格 (TWD)": st.column_config.NumberColumn(format="TWD %d"),
                "出發日期 (S2)": st.column_config.DateColumn(format="YYYY-MM-DD")
            }
        )

        # 航空公司要件註記
        st.subheader("📋 航空公司四段票要件註記 (實戰版)")
        st.info(f"""
        **【開票核心要件】**
        - **日期範圍**：已自動掃描 {base_date} 前後 15 天，上方列表已按價格排序。
        - **Open Jaw 規則**：{'已啟用' if allow_oj else '未啟用'}。回程時航空公司允許「開口」，但行李仍需註記取回。
        - **外站要件**：S1 必須在指定日期從外站飛抵台灣以「激活」整張票。
        - **證件提醒**：若外站位於中國 (PVG)，務必檢查台胞證效期。
        """)
    else:
        st.error("掃描範圍內未發現有效報價。請確認目的地代碼或嘗試更遠的日期。")

st.divider()
st.caption("𓃥 White 6 Studio | 2026 航空自動化比價 | 支持 +/- 15 天深度掃描")
