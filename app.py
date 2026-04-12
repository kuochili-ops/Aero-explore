import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球完整機場資料庫 (含各國城市) ---
# 此處建議實際開發時串接完整 IATA 庫，目前先擴充關鍵節點
COUNTRIES = {
    "歐洲": ["捷克 (PRG)", "奧地利 (VIE)", "德國 (MUC/FRA)", "英國 (LHR)", "法國 (CDG)", "瑞士 (ZRH)"],
    "亞洲": ["日本 (NRT/HND/KIX)", "韓國 (ICN/PUS)", "中國 (PVG/PKX/TAO)", "泰國 (BKK/CNX)", "越南 (SGN/HAN)"],
    "美加": ["美國 (LAX/SFO/JFK/SEA)", "加拿大 (YVR/YYZ)"]
}

# --- 2. 側邊欄：導航設定 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    st.header("📍 1. 目的地 (S2/S3)")
    region = st.selectbox("選擇區域", list(COUNTRIES.keys()))
    target = st.selectbox("選擇城市", COUNTRIES[region])
    dest_iata = target.split("(")[1].split(")")[0]

    st.header("🛫 2. 啟動外站 (S1/S4)")
    # 新增外站彈性選擇
    hubs = {"KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", "PVG": "上海", "NRT": "東京"}
    selected_hub = st.selectbox("選擇外站", list(hubs.keys()), format_func=lambda x: f"{hubs[x]} ({x})")

    st.header("📅 3. 行程規劃")
    s2_date = st.date_input("S2 出發日", value=datetime.today().date() + timedelta(days=90))
    s3_user_date = st.date_input("S3 回台日", value=s2_date + timedelta(days=14))
    
    allow_oj = st.toggle("S3 不同點進出 (Open Jaw)", value=True)

    if st.button("🚀 執行全方位掃描建議"):
        st.session_state.searched = True

# --- 3. 主頁面：解決「長榮無法提供組合」的列表 ---
if st.session_state.get('searched'):
    st.header(f"📊 {target} 四段票訂票建議清單")
    
    # 模擬系統比價後得出的 S1 與 S4 (避開加價艙等)
    # S1 與 S4 的日期將根據 selected_hub 自動搜尋該週最低價
    s1_suggested = s2_date - timedelta(days=45) 
    s4_suggested = s1_suggested + timedelta(days=330)

    # --- 重要：訂票指引卡片 ---
    st.warning(f"⚠️ **官網搜尋重要提醒**：請務必從 **{hubs[selected_hub]} ({selected_hub})** 作為起點搜尋。")
    
    # --- 列表：顯示各段詳情 ---
    st.subheader("📅 推薦行程組合 (供官網多城市輸入)")
    
    # 構建包含各段航司、艙等、日期的明細
    itineraries = []
    airlines = ["長榮航空 (BR)", "中華航空 (CI)", "星宇航空 (JX)"]
    
    for air in airlines:
        # 基本組合
        itineraries.append({
            "航空公司": air,
            "S1 (外站➔台北)": f"{selected_hub} ➔ TPE ({s1_suggested})",
            "S2 (台北➔長程)": f"TPE ➔ {dest_iata} ({s2_date})",
            "S3 (長程➔台北)": f"{dest_iata} ➔ TPE ({s3_user_date})",
            "S4 (台北➔外站)": f"TPE ➔ {selected_hub} ({s4_suggested})",
            "建議艙等": "Economy (V/W 艙)" if "長榮" in air else "Economy (L 艙)"
        })

    df = pd.DataFrame(itineraries)
    st.table(df) # 使用 Table 確保格式清晰

    st.markdown(f"""
    ### 🛠 長榮官網訂位步驟說明：
    若您在官網搜尋失敗，通常是因為**順序**或**中停時間**問題。請依序輸入以下四段：
    1. **第一段**：出發 **{selected_hub}** / 到達 **TPE** (日期：{s1_suggested})
    2. **第二段**：出發 **TPE** / 到達 **{dest_iata}** (日期：{s2_date})
    3. **第三段**：出發 **{dest_iata}** / 到達 **TPE** (日期：{s3_user_date})
    4. **第四段**：出發 **TPE** / 到達 **{selected_hub}** (日期：{s4_suggested})
    
    **💡 專業撇步：**
    * 如果系統仍報錯，請嘗試將 S1 或 S4 的日期**往前後移動 1-2 天**，避開該航段機位全滿的日期。
    * 確保 S1 到 S4 的總跨度在 **365 天** 內。
    """)
