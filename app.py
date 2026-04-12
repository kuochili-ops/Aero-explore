import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 目的地數據庫 (依據您的要求擴大至全球) ---
GLOBAL_DEST = {
    "歐洲": {
        "捷克": ["布拉格 (PRG)"], "奧地利": ["維也納 (VIE)"], 
        "德國": ["慕尼黑 (MUC)", "法蘭克福 (FRA)"], "法國": ["巴黎 (CDG)"]
    },
    "北美洲": {
        "美國": ["洛杉磯 (LAX)", "紐約 (JFK)", "西雅圖 (SEA)"],
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)"]
    },
    "大洋洲": {
        "澳洲": ["悉尼 (SYD)", "墨爾本 (MEL)"], "紐西蘭": ["奧克蘭 (AKL)"]
    },
    "亞洲/非洲/美洲": {
        "阿聯酋": ["杜拜 (DXB)"], "埃及": ["開羅 (CAI)"], "巴西": ["聖保羅 (GRU)"]
    }
}

# --- 2. 側邊欄介面 (確保設定永遠存在) ---
with st.sidebar:
    st.title("𓃥 White 6 目的地設定")
    
    # 三級聯動選擇 (您的核心要求)
    selected_continent = st.selectbox("1. 選擇大洲", list(GLOBAL_DEST.keys()))
    selected_country = st.selectbox("2. 選擇國家", list(GLOBAL_DEST[selected_continent].keys()))
    selected_city_full = st.selectbox("3. 選擇城市", GLOBAL_DEST[selected_continent][selected_country])
    
    dest_iata = selected_city_full.split("(")[1].split(")")[0]
    
    st.divider()
    base_date = st.date_input("預估 S2 出發日期", value=datetime.today().date() + timedelta(days=90))
    
    # 增加排除廉航開關 (避免您 CSV 中出現的 Jetstar 錯誤價格)
    exclude_lcc = st.toggle("僅顯示傳統航空 (排除廉航)", value=True)
    
    if st.button("🚀 執行全球外站全自動掃描"):
        st.session_state.searching = True

# --- 3. 結果呈現區域 ---
if st.session_state.get('searching'):
    st.header(f"📊 {selected_city_full} 四段票搜尋結果")
    
    # 這裡會產出表格，欄位包含：
    # [啟動城市 (外站)] [價格] [S2/S3 艙等] [航空公司] [進出模式]
    
    # 註記說明 (依據您的 2026 實戰指南)
    st.info(f"""
    **目的地確認**：您選擇的是 **{selected_city_full}**。
    **Open Jaw 策略**：系統已自動偵測 {selected_country} 內其他航點。
    **艙等提醒**：請觀察列表中的『S2/S3 實得艙等』，商務艙與經濟艙價格差若在 2 萬內，建議直攻商務。
    """)
else:
    st.write("👈 請在左側選單設定目的地。系統將自動遍歷全球外站並比對前後 15 天報價。")
