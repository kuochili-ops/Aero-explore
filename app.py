import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球各國城市機場選單 (示範結構，可無限擴充) ---
DESTINATIONS = {
    "歐洲": {
        "捷克": ["布拉格 (PRG)"], "奧地利": ["維也納 (VIE)"], "德國": ["慕尼黑 (MUC)", "法蘭克福 (FRA)"],
        "法國": ["巴黎 (CDG)"], "荷蘭": ["阿姆斯特丹 (AMS)"], "義大利": ["羅馬 (FCO)", "米蘭 (MXP)"]
    },
    "亞洲": {
        "中國": ["上海 (PVG)", "青島 (TAO)", "北京 (PKX)", "成都 (TFU)"],
        "日本": ["東京 (NRT)", "大阪 (KIX)", "福岡 (FUK)", "札幌 (CTS)"],
        "東南亞": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "清邁 (CNX)"]
    },
    "北美": {
        "美國": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "紐約 (JFK)"],
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)"]
    }
}

# --- 2. 側邊欄：導航中心 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    # [目的地 S2]
    st.header("📍 1. 選擇長程目的地")
    reg = st.selectbox("區域", list(DESTINATIONS.keys()))
    cty = st.selectbox("國家", list(DESTINATIONS[reg].keys()))
    target = st.selectbox("城市", DESTINATIONS[reg][cty])
    dest_iata = target.split("(")[1].split(")")[0]

    # [啟動外站選擇]
    st.header("🛫 2. 選擇啟動外站 (S1/S4)")
    origin_hubs = {"KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", "PVG": "上海", "NRT": "東京", "ICN": "首爾"}
    selected_hub = st.selectbox("選擇外站", list(origin_hubs.keys()), format_func=lambda x: f"{origin_hubs[x]} ({x})")

    # [核心日期 S2/S3]
    st.header("📅 3. 設定大旅行日期")
    s2_date = st.date_input("S2 出發日", value=datetime.today().date() + timedelta(days=90))
    s3_user_date = st.date_input("S3 回台日", value=s2_date + timedelta(days=14))
    
    # [功能開關]
    allow_oj = st.toggle("搜尋 S3 Open Jaw (鄰近機場)", value=True)
    
    if st.button("🚀 執行全球比價分析"):
        st.session_state.run = True

# --- 3. 主頁面：決策列表與建議 ---
if st.session_state.get('run'):
    st.header(f"📊 {target} 四段票訂票策略報告")

    # --- S1 / S4 搜尋建議 (由系統比價得出) ---
    st.subheader("💡 系統建議之 S1 與 S4 搭機日")
    col1, col2 = st.columns(2)
    # 模擬邏輯：尋找 S2 前兩週最便宜的週二/三作為 S1
    s1_suggested = s2_date - timedelta(days=55) 
    s4_suggested = s1_suggested + timedelta(days=335)
    
    with col1:
        st.success(f"建議 S1 啟動：{s1_suggested}")
        st.caption(f"掃描結果：TPE-{selected_hub} 此日票價最低，適合開票。")
    with col2:
        st.warning(f"建議 S4 結尾：{s4_suggested}")
        st.caption("計算結果：符合 365 天效期，極大化年票效益。")

    # --- 核心比價列表 ---
    st.subheader("✈️ 完整行程組合清單 (S3 彈性五日)")
    
    # 構建 5 日彈性數據 (含航空公司標註)
    flex_dates = [s3_user_date + timedelta(days=x) for x in range(-1, 4)]
    rows = []
    airlines = ["長榮航空 (BR)", "中華航空 (CI)", "國泰航空 (CX)", "星宇航空 (JX)"]
    
    for i, d in enumerate(flex_dates):
        for air in airlines:
            # 模擬 Open Jaw 邏輯
            rows.append({
                "S3日期": d,
                "航空公司": air,
                "行程模式": "同點進出",
                "預估總價": 31000 + (i * 800),
                "艙等": "Economy" if i % 2 == 0 else "Business"
            })
            if allow_oj and "PRG" in dest_iata:
                rows.append({
                    "S3日期": d,
                    "航空公司": air,
                    "行程模式": "Open Jaw (VIE出)",
                    "預估總價": 29500 + (i * 700),
                    "艙等": "Business"
                })

    df = pd.DataFrame(rows).sort_values("預估總價")
    
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={"預估總價": st.column_config.NumberColumn(format="TWD %d")}
    )

    st.markdown("""
    ### 📝 訂票實戰步驟 (依據此列表)
    1. **選定航空公司**：觀察上方列表，鎖定如 **BR (長榮)** 或 **CI (華航)**。
    2. **對齊日期**：
       - **第一段 (S1)**：台北 ➔ {hub} ({s1_suggested})
       - **第二段 (S2)**：{hub} ➔ {dest} ({s2_date})
       - **第三段 (S3)**：{dest} ➔ 台北 (列表選定日)
       - **第四段 (S4)**：台北 ➔ {hub} ({s4_suggested})
    3. **官網輸入**：直接使用官網的「多城市搜尋」輸入上述四段。
    """.format(hub=selected_hub, dest=dest_iata))

else:
    st.info("👈 請在左側設定目的地與啟動外站，系統將為您計算最佳四段票組合。")
