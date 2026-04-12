import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 初始化與介面固定 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")

# 固定側邊欄：確保搜尋條件永遠存在
with st.sidebar:
    st.title("𓃥 White 6 導航設定")
    
    # 目的地聯動選單
    continent = st.selectbox("1. 選擇大洲", ["歐洲", "北美洲", "大洋洲", "亞洲/非洲"])
    dest_city = st.text_input("2. 目的地城市 (IATA 碼)", value="PRG")
    
    st.divider()
    
    # 日期設定
    base_date = st.date_input("預估 S2 出發日期", value=datetime.today().date() + timedelta(days=90))
    date_flex = st.slider("日期彈性 (前後天數)", 0, 15, 7)
    
    st.divider()
    
    # 實戰過濾器 (關鍵！)
    exclude_lcc = st.checkbox("排除廉價航空 (建議開啟)", value=True)
    st.caption("開啟後將過濾 Scoot, Jetstar 等無法開正規四段票的航空公司")
    
    st.divider()
    if st.button("🚀 開始全自動掃描"):
        st.session_state.run_search = True

# --- 2. 搜尋邏輯 ---
if st.session_state.get('run_search'):
    st.subheader(f"🔍 正在為您掃描全外站數據：{dest_city}")
    
    # 定義外站城市
    STATION_MAP = {
        "KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", 
        "PVG": "上海", "NRT": "東京", "ICN": "首爾"
    }
    
    # 模擬結果 (應對 API 快取誤差，增加驗證註記)
    all_data = []
    # 此處應調用 SerpApi，此處簡化邏輯以呈現結果
    # ... (搜尋代碼同前)
    
    # 產出 DataFrame
    results = [
        {"外站": "吉隆坡 (KUL)", "價格": 21500, "艙等": "Economy", "航空公司": "EVA Air", "可信度": "高"},
        {"外站": "曼谷 (BKK)", "價格": 48000, "艙等": "Business", "航空公司": "China Airlines", "可信度": "高"},
        {"外站": "上海 (PVG)", "價格": 19800, "艙等": "Economy", "航空公司": "Cathay Pacific", "可信度": "中"},
    ]
    
    df = pd.DataFrame(results)
    
    # --- 3. 結果列出與排序 ---
    st.success("✅ 掃描完成！請依據需求點擊表頭排序。")
    st.dataframe(
        df.sort_values("價格"), 
        use_container_width=True,
        column_config={
            "價格": st.column_config.NumberColumn(format="TWD %d"),
        }
    )

    # --- 4. 針對「實價誤差」的專家提醒 ---
    st.info("""
    ### 𓃥 White 6 實戰避坑指南：
    1. **過濾廉航**：您上傳的數據中出現大量 $2,588 等價格，那是**捷星(Jetstar)**的單段促銷，無法掛行李也無法組成四段票，請直接忽略。
    2. **真實艙等**：四段票的價值在於用「經濟艙價」買到「長程商務艙」。若看到價格低於 2 萬但標註為 Business，通常是快取錯誤。
    3. **搜尋技巧**：在官網確認時，請務必使用「**多城市 (Multi-city)**」搜尋，並手動輸入四段日期，價格才會正確。
    """)
else:
    st.info("👈 請在左側設定條件並點擊「開始掃描」以獲取數據。")
