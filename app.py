import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球 IATA 城市資料庫 (亞洲大幅擴充) ---
GLOBAL_DESTINATIONS = {
    "亞洲 (長程/熱門)": {
        "日本": ["東京/成田 (NRT)", "東京/羽田 (HND)", "大阪 (KIX)", "福岡 (FUK)", "仙台 (SDJ)"],
        "韓國": ["首爾/仁川 (ICN)", "釜山 (PUS)"],
        "中國": ["上海/浦東 (PVG)", "北京/大興 (PKX)", "青島 (TAO)", "成都 (TFU)"],
        "東南亞/中東": ["曼谷 (BKK)", "清邁 (CNX)", "新加坡 (SIN)", "吉隆坡 (KUL)", "杜拜 (DXB)", "伊斯坦堡 (IST)"]
    },
    "歐洲": {
        "中歐": ["布拉格 (PRG)", "維也納 (VIE)", "慕尼黑 (MUC)", "蘇黎世 (ZRH)"],
        "西歐": ["巴黎 (CDG)", "倫敦 (LHR)", "阿姆斯特丹 (AMS)"],
        "南歐/北歐": ["羅馬 (FCO)", "米蘭 (MXP)", "馬德里 (MAD)", "赫爾辛基 (HEL)"]
    },
    "北美/大洋洲": {
        "北美": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "溫哥華 (YVR)"],
        "大洋洲": ["悉尼 (SYD)", "墨爾本 (MEL)", "奧克蘭 (AKL)"]
    }
}

STATION_MAP = {
    "KUL": "吉隆坡 (馬來西亞)", "BKK": "曼谷 (泰國)", "HKG": "香港", 
    "PVG": "上海 (中國)", "NRT": "東京 (日本)", "ICN": "首爾 (韓國)"
}

# --- 2. 側邊欄：智能聯動設定 ---
with st.sidebar:
    st.title("𓃥 White 6 導航設定")
    
    st.header("📍 目的地 (三級聯動)")
    continent = st.selectbox("1. 選擇區域", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇城市", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]

    st.divider()
    
    st.header("📅 智能日期聯動")
    # 用戶只需設定 S2 (核心旅行日)
    s2_date = st.date_input("大旅行出發日 (S2)", value=datetime.today().date() + timedelta(days=90))
    
    # 自動推算建議日期 (基於您的 2026 指南與票務邏輯)
    s1_suggest = s2_date - timedelta(days=60)
    s3_suggest = s2_date + timedelta(days=14)
    s4_suggest = s1_suggest + timedelta(days=330)
    
    st.caption(f"💡 系統建議日期：\n- S1 啟動：{s1_suggest} (提前2個月)\n- S3 回台：{s3_suggest} (玩15天)\n- S4 結尾：{s4_suggest} (明年連假)")

    st.divider()
    
    st.header("⚙️ 實戰過濾器")
    exclude_lcc = st.toggle("排除廉價航空 (實戰模式)", value=True)
    st.caption("自動過濾 Jetstar, Scoot 等無法開立一本票的數據")

    if st.button("🚀 啟動全方位掃描"):
        st.session_state.run_search = True

# --- 3. 核心邏輯與結果呈現 ---
if st.session_state.get('run_search'):
    st.header(f"📊 {city_full} 全球外站掃描報告")
    
    # 這裡加入一個圖解，讓用戶理解四段票的時間軸
    
    
    # 模擬與搜尋數據處理 (略，同前)...
    
    st.subheader("📝 2026 外站四段票開票要件 (已依建議日期優化)")
    st.info(f"""
    1. **S1 啟動要件**：請購買一張單程票前往 {STATION_MAP['KUL']} (範例)，並於 {s1_suggest} 搭乘 S1 返台。
    2. **S3/S4 中停策略**：您的 S3 ({s3_suggest}) 回台後，與 S4 ({s4_suggest}) 之間有超過 24 小時。
       - **傳統航空**：需確認機票包含「第二次停留」加價。
       - **行李提醒**：S3 到達台灣時，務必確保行李「不直掛外站」。
    3. **艙等價值**：請查看下方列表之 **S2/S3 實得艙等**，若商務艙價格合理，請優先考慮。
    """)
    
    # (顯示 DataFrame 表格內容...)
    
else:
    st.info("👈 請在左側設定您的『長程出發日 (S2)』，系統將自動為您佈局最合理的四段票時間點。")

st.divider()
st.caption("𓃥 White 6 Studio | 2026 航空自動化導航 | 智能日期聯動版")
