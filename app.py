import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 聯動選單資料 ---
DESTINATIONS = {
    "歐洲": {
        "捷克": ["Prague (PRG)"], "奧地利": ["Vienna (VIE)"],
        "德國": ["Munich (MUC)", "Frankfurt (FRA)"], "法國": ["Paris (CDG)"]
    },
    "亞洲": {
        "日本": ["Tokyo (NRT)", "Osaka (KIX)", "Fukuoka (FUK)"],
        "中國": ["Shanghai (PVG)", "Beijing (PEK)", "Xiamen (XMN)"],
        "東南亞": ["Bangkok (BKK)", "Kuala Lumpur (KUL)", "Singapore (SIN)"]
    }
}

# --- 3. 介面設定 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("2026 外站四段票實戰導航 (依據最新指南校準)")

with st.sidebar:
    st.header("📍 目的地與日期")
    continent = st.selectbox("選擇大洲", list(DESTINATIONS.keys()))
    country = st.selectbox("選擇國家", list(DESTINATIONS[continent].keys()))
    city_full = st.selectbox("選擇城市", DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    base_date = st.date_input("預估 S2 出發日期", value=datetime.today().date() + timedelta(days=61))
    
    st.divider()
    st.header("⚙️ 實戰選項")
    accept_oj = st.checkbox("接受 Open Jaw (鄰近城市比對)", value=True)
    tpe_hub = st.selectbox("台灣機場 (Hub)", ["TPE", "TSA", "KHH", "RMQ"])

# --- 4. 廣域掃描邏輯 ---
if st.button("🚀 啟動全自動掃描 (含 +/- 15天 & 跨國外站)"):
    # 外站清單涵蓋 指南中提到的熱門點
    stations = ["KUL", "BKK", "HKG", "NRT", "PVG", "ICN"]
    # 掃描日期範圍 (前後各15天，採樣跳步以優化效能)
    date_range = [base_date + timedelta(days=x) for x in range(-15, 16, 3)]
    
    search_targets = [dest_iata]
    if accept_oj:
        search_targets.extend([c.split("(")[1].split(")")[0] for c in DESTINATIONS[continent][country] if dest_iata not in c])

    all_data = []
    bar = st.progress(0)
    
    total = len(stations) * len(date_range) * len(search_targets)
    count = 0

    for stn in stations:
        for d in date_range:
            for target in search_targets:
                count += 1
                bar.progress(count / total)
                
                # 模擬搜尋 (實際執行時調用 SerpApi)
                # 這裡呈現結果結構...
                all_data.append({
                    "價格 (TWD)": 18000 + (count % 5000), # 範例模擬
                    "啟動外站": stn,
                    "出發日期 (S2)": d,
                    "航空公司": "STARLUX" if count % 3 == 0 else "EVA Air",
                    "進出模式": "同點" if target == dest_iata else "Open Jaw",
                    "S1 日期": d - timedelta(days=60),
                    "S4 日期": d + timedelta(days=120)
                })

    # --- 5. 結果呈現與排序 ---
    df = pd.DataFrame(all_data)
    st.dataframe(df.sort_values("價格 (TWD)"), use_container_width=True)

    # --- 6. 依據指南生成的「要件註記」 ---
    st.subheader("📝 2026 四段票開票要件註記 (指南建議版)")
    best_stn = df.iloc[0]['啟動外站']
    st.warning(f"""
    **【核心要件：第四段 (S4) 處理策略】**
    1. **行李要件**：在 S3 ({dest_iata} ➔ {tpe_hub}) 報到時，務必告知地勤「行李只掛到台北」，確認標籤為 **TPE**。
    2. **安全處理**： 絕對不要在飛完前三段前自行在官網取消第四段，以免觸發「系統連帶取消」導致 S3 失效。
    3. **No Show 註記**：完成第三段後，若不打算飛 S4，可選擇 **No Show**。這是目前成本最低且不影響前段里程的作法。
    4. **改降要件**：若 S4 ({tpe_hub} ➔ {best_stn}) 確定不飛，可聯絡客服嘗試「改降不同機場」(如改飛 TSA 或 KHH)，或延後日期作為下一趟旅程起點。
    5. **外站限制**：若外站為 **PVG (上海)**，須確保 S1 與 S4 時具備有效台胞證。
    """)

st.divider()
st.caption("𓃥 White 6 Studio | 2026 航空自動化導航 | 參考《旅途中的景深隨想》專業指南校準")
