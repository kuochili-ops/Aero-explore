import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 目的地資料庫 (延用全球版) ---
# ... (GLOBAL_DESTINATIONS 內容同前)

# --- 2. 側邊欄：S3 決策與彈性搜尋 ---
with st.sidebar:
    st.title("𓃥 White 6 導航設定")
    
    # 目的地與 S2 (大旅行出發)
    continent = st.selectbox("1. 選擇區域", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇目的地", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    s2_date = st.date_input("大旅行出發日 (S2)", value=datetime.today().date() + timedelta(days=90))
    
    st.divider()
    
    # 核心優化：S3 自定義與彈性範圍
    st.header("📅 S3 回台日期設定")
    s3_user_date = st.date_input("指定長程回台日 (S3)", value=s2_date + timedelta(days=14))
    
    # 系統自動設定搜尋窗口：前1天 ~ 後3天
    s3_range = [s3_user_date + timedelta(days=x) for x in range(-1, 4)]
    st.caption(f"🔍 系統將同步比對：{s3_range[0]} 至 {s3_range[-1]}")

    st.divider()
    
    exclude_lcc = st.toggle("實戰模式 (排除廉航)", value=True)

    if st.button("🚀 執行彈性掃描"):
        st.session_state.run_flex_search = True

# --- 3. 搜尋結果與比價呈現 ---
if st.session_state.get('run_flex_search'):
    st.header(f"📊 {city_full} 彈性比價報告")
    
    # 這裡呈現比價表格，重點在於 S3 日期的差異
    # 欄位：[啟動外站] [S3 日期] [價格] [艙等] [航空公司] [價差提醒]
    
    st.subheader("💡 搜尋發現與建議")
    
    # 模擬邏輯：找出這 5 天中最低價的一天
    st.success(f"找到了！在您的目標日期附近，**{s3_user_date + timedelta(days=2)}** 的價格最優。")
    
    st.info(f"""
    **【White 6 行程規劃建議】**
    * **您的選擇**：{s3_user_date} 回台。
    * **系統發現**：若您願意多留 2 天（{s3_user_date + timedelta(days=2)}），{city_full} 的回程艙等有更優惠的選擇。
    * **一本票提醒**：此五個日期的 S1 ({s2_date - timedelta(days=60)}) 與 S4 ({s2_date + timedelta(days=300)}) 已由系統自動對齊，確保符合 365 天效期。
    """)
    
    # (顯示詳細 Dataframe)
    # df = ... (依據 s3_range 循環搜尋出的結果)
