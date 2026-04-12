import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. Open Jaw 鄰近城市對照表 (2026 實戰版) ---
OPEN_JAW_PAIRS = {
    "PRG": "VIE", "VIE": "PRG", # 布拉格 - 維也納 (最熱門)
    "CDG": "AMS", "AMS": "CDG", # 巴黎 - 阿姆斯特丹
    "MUC": "FRA", "FRA": "MUC", # 慕尼黑 - 法蘭克福
    "LAX": "SFO", "SFO": "LAX", # 洛杉磯 - 舊金山
}

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    # ... (目的地選擇邏輯同前)
    
    st.divider()
    s2_date = st.date_input("S2 大旅行出發日", value=datetime.today().date() + timedelta(days=90))
    s3_user_date = st.date_input("S3 指定回台日", value=s2_date + timedelta(days=14))
    
    # 新增 S3 Open Jaw 開關
    allow_oj = st.checkbox("自動搜尋 S3 Open Jaw (不同點進出)", value=True)
    
    if st.button("🚀 執行全球策略掃描"):
        st.session_state.run_analysis = True

# --- 3. 核心結果顯示 ---
if st.session_state.get('run_analysis'):
    st.header(f"📊 {target_city} 四段票策略報告")

    # 

    # --- S1 / S4 票價建議模組 ---
    st.subheader("📅 S1 / S4 趨勢建議")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("S1 建議日 (啟動)", f"{s2_date - timedelta(days=58)}", "低價波段")
        st.caption("建議搭乘週二/週三航班，API 顯示此時段外站票配額最充足。")
    with col2:
        st.metric("S4 建議日 (結尾)", f"{s2_date + timedelta(days=320)}", "效期極限")
        st.caption("自動對齊明年連假，可作為下一趟小旅行的起點。")

    # --- 彈性五日比價清單 (含 Open Jaw) ---
    st.subheader("✈️ S3 彈性比價 (含 Open Jaw 選項)")
    # 此處邏輯會自動將原本目的地的鄰近城市加入搜尋
    # 例如：搜尋 PRG-TPE 的同時，也搜尋 VIE-TPE
    
    # ... (DataFrame 呈現，加入 [Open Jaw] 標籤)
    
    st.info("""
    **💡 White 6 開票提醒**：
    1. **S3 Open Jaw**：若選擇不同點進出，請在官網使用「多城市」輸入，系統會自動套用一本票優惠。
    2. **S4 日期**：我們建議將 S4 設定在 S1 之後的 320 天，這能保留最大的改票彈性，若明年想提前出發也沒問題。
    """)
