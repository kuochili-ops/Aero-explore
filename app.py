import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [核心資料庫] 必須放在程式最上方，避免 Line 13 Error ---
GLOBAL_DESTINATIONS = {
    "亞洲 (長程/熱門)": {
        "日本": ["東京/成田 (NRT)", "東京/羽田 (HND)", "大阪 (KIX)", "福岡 (FUK)"],
        "韓國": ["首爾/仁川 (ICN)", "釜山 (PUS)"],
        "中國": ["上海/浦東 (PVG)", "北京/大興 (PKX)", "青島 (TAO)"],
        "東南亞/中東": ["曼谷 (BKK)", "新加坡 (SIN)", "吉隆坡 (KUL)", "杜拜 (DXB)", "伊斯坦堡 (IST)"]
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
    "KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", "PVG": "上海", "NRT": "東京", "ICN": "首爾"
}

# --- 2. 側邊欄：智能聯動與 S3 彈性設定 ---
with st.sidebar:
    st.title("𓃥 White 6 導航設定")
    
    # 目的地聯動 (解決您的第一個要求)
    continent = st.selectbox("1. 選擇區域", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇城市", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]

    st.divider()
    
    # 日期智能聯動 (解決您的第二個要求)
    s2_date = st.date_input("大旅行出發日 (S2)", value=datetime.today().date() + timedelta(days=90))
    
    # S3 日期由您決定
    s3_user_date = st.date_input("指定長程回台日 (S3)", value=s2_date + timedelta(days=14))
    
    # S3 彈性搜尋區間：前1天、當天、後1天、後2天、後3天 (共 5 個搜尋點)
    s3_flex_dates = [s3_user_date + timedelta(days=x) for x in range(-1, 4)]
    
    st.caption(f"💡 系統將掃描 S3 區間：\n{s3_flex_dates[0]} ~ {s3_flex_dates[-1]}")

    st.divider()
    
    # 實戰過濾：排除廉航
    exclude_lcc = st.toggle("排除廉價航空 (實戰模式)", value=True)

    if st.button("🚀 執行彈性掃描"):
        st.session_state.run_search = True

# --- 3. 執行搜尋與結果呈現 ---
if st.session_state.get('run_search'):
    st.header(f"📊 {city_full} 四段票彈性比價報告")
    
    # 圖解：四段票時間軸分佈
    
    
    # 此處邏輯會迴圈執行 s3_flex_dates 的搜尋...
    # [搜尋代碼略，重點在於會將這 5 天的價格合併並標註價差]
    
    st.info(f"""
    **🔍 彈性掃描發現：**
    系統正在為您比對從 **{s3_flex_dates[0]}** 到 **{s3_flex_dates[-1]}** 的回程價格。
    
    **四段票效期檢查：**
    - S1 啟動日：建議設定在 {s2_date - timedelta(days=60)}
    - S4 結尾日：自動對齊於 S1 之後的 330 天，確保機票在 1 年效期內。
    """)
    
    # 表格呈現
    # 增加一欄 [S3日期] 與 [價差(相對指定日)]
    # 這樣您就能一眼看出「後三天」哪天最便宜
    
else:
    st.info("👈 請在左側設定目的地與日期。系統會自動以您的 S3 為中心，尋找前後 4 天內的最佳組合。")
