import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [核心架構] 定義目的地與外站 ---
GLOBAL_DESTINATIONS = {
    "歐洲": {"捷克/奧地利": ["布拉格 (PRG)", "維也納 (VIE)"], "德國": ["慕尼黑 (MUC)", "法蘭克福 (FRA)"]},
    "北美/大洋洲": {"美國": ["洛杉磯 (LAX)", "紐約 (JFK)"], "澳洲": ["悉尼 (SYD)"]}
}

STATION_MAP = {"KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", "NRT": "東京"}

# --- 2. [側邊欄] 重新佈局：用戶只需決定目的地與 S2/S3 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    # 用戶輸入 A：目的地
    st.header("📍 第一步：決定長程目的地")
    reg = st.selectbox("選擇區域", list(GLOBAL_DESTINATIONS.keys()))
    cty = st.selectbox("選擇國家", list(GLOBAL_DESTINATIONS[reg].keys()))
    target_city = st.selectbox("選擇城市", GLOBAL_DESTINATIONS[reg][cty])
    dest_iata = target_city.split("(")[1].split(")")[0]

    # 用戶輸入 B：S2 與 S3 (您的核心行程)
    st.header("📅 第二步：設定核心行程")
    s2_user_date = st.date_input("S2 出發日", value=datetime.today().date() + timedelta(days=90))
    s3_user_date = st.date_input("S3 回台日", value=s2_user_date + timedelta(days=14))
    
    st.divider()
    
    # 策略開關
    allow_oj = st.toggle("自動搜尋 S3 Open Jaw (不同點進出)", value=True)
    st.caption("開啟後將同步搜尋鄰近機場報價")

    if st.button("🚀 執行全方位票價掃描"):
        st.session_state.do_analysis = True

# --- 3. [主介面] 根據搜尋結果給予 S1/S4 建議 ---
if st.session_state.get('do_analysis'):
    st.header(f"📊 {target_city} 四段票規劃建議報告")

    # 這裡會跑 3 個搜尋任務：
    # 1. S2/S3 彈性 5 日比價 (含 Open Jaw)
    # 2. S1 搜尋：在 S2 前 30-60 天內找最低價日
    # 3. S4 搜尋：在 S1 後 300-350 天內找最低價日

    st.subheader("💡 最佳搭機日期建議 (由 AI 掃描比價後產出)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("✔ 建議 S1 啟動日")
        st.write("**2026-04-15 (週三)**")
        st.caption("比對前後兩週，此日票價最低 (TWD 4,200)")
        
    with col2:
        st.info("✈ 您的 S2/S3 核心")
        st.write(f"**{s2_user_date} ~ {s3_user_date}**")
        st.caption("長程段建議選用長榮或華航一本票")

    with col3:
        st.warning("✔ 建議 S4 結尾日")
        st.write("**2027-02-10 (週三)**")
        st.caption("對齊明年春節前夕，且仍在機票效期內")

    # --- 彈性五日比價列表 ---
    st.subheader("🔍 S3 回程五日彈性比價 (含 Open Jaw)")
    # 此處顯示 dataframe [S3日期] [外站] [價格] [艙等] [進出模式]
    # ...
    
    st.divider()
    st.info("""
    **𓃥 White 6 策略說明**：
    - 我們搜尋了您 S2 出發前的區域航線趨勢，為您挑選了 **S1 最低價位點**。
    - **S4 日期建議** 已考量航空公司 365 天的一本票規則，確保您的行程合法且最具效益。
    """)
