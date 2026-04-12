import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [全量庫] 全球大城市選單 (S2/S3 目標) ---
WORLD_MAP = {
    "歐洲": ["布拉格 (PRG)", "維也納 (VIE)", "倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "慕尼黑 (MUC)", "米蘭 (MXP)"],
    "亞洲": ["東京 (NRT/HND)", "大阪 (KIX)", "首爾 (ICN)", "曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "上海 (PVG)"],
    "北美/大洋洲": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "溫哥華 (YVR)", "悉尼 (SYD)", "奧克蘭 (AKL)"]
}

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.title("𓃥 White 6 旅程規劃師")
    
    st.header("📍 1. 目的地設定")
    region = st.selectbox("選擇大洲", list(WORLD_MAP.keys()))
    target = st.selectbox("選擇前往城市 (S2/S3)", WORLD_MAP[region])
    dest_iata = target.split("(")[1].split(")")[0]

    st.header("📅 2. 核心大旅行日期")
    s2_core = st.date_input("S2 出發核心日", value=datetime(2026, 10, 15))
    s3_core = st.date_input("S3 回台核心日", value=s2_core + timedelta(days=12))
    
    allow_oj = st.toggle("搜尋 S3 Open Jaw (不同點進出)", value=True)

    if st.button("🚀 執行全球比價與全航段分析"):
        st.session_state.run_pro = True

# --- 3. 主頁面：顯示四段全細節清單 ---
if st.session_state.get('run_pro'):
    st.header(f"📊 {target} 四段票精準行程清單")

    # S1/S4 系統建議日
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    st.info(f"💡 **系統策略建議**：\n- **S1 啟動日**：{s1_suggested} (最易開出 V 艙)\n- **S4 結尾日**：{s4_suggested} (最大化年票效期)")

    # 模擬數據：並列外站、台灣機場、與 S2/S3 彈性組合
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)", "NRT (東京)"]
    tw_hubs = ["TPE (桃園)", "KHH (高雄)"] # 只列出有長程接駁實力的機場
    
    data = []
    # S2 前1/當天, S3 當天/後3天
    for hub in hubs:
        hub_iata = hub.split("(")[1].split(")")[0]
        for tw in tw_hubs:
            tw_iata = tw.split("(")[1].split(")")[0]
            for d2 in [s2_core - timedelta(days=1), s2_core]:
                for d3 in [s3_core + timedelta(days=x) for x in range(4)]:
                    # 基本來回
                    data.append({
                        "外站樞紐": hub, "台灣機場": tw,
                        "S1段": f"{hub_iata} ➔ {tw_iata}",
                        "S2段": f"{tw_iata} ➔ {dest_iata}", "S2日期": d2,
                        "S3段": f"{dest_iata} ➔ {tw_iata}", "S3日期": d3,
                        "S4段": f"{tw_iata} ➔ {hub_iata}",
                        "預估總價": 32800 if "KUL" in hub else 35500,
                        "模式": "同點進出"
                    })
                    # Open Jaw
                    if allow_oj and "PRG" in dest_iata:
                        data.append({
                            "外站樞紐": hub, "台灣機場": tw,
                            "S1段": f"{hub_iata} ➔ {tw_iata}",
                            "S2段": f"{tw_iata} ➔ {dest_iata}", "S2日期": d2,
                            "S3段": f"VIE ➔ {tw_iata}", "S3日期": d3,
                            "S4段": f"{tw_iata} ➔ {hub_iata}",
                            "預估總價": 30500 if "KUL" in hub else 33200,
                            "模式": "Open Jaw (VIE出)"
                        })

    df = pd.DataFrame(data).sort_values("預估總價")
    st.dataframe(df, use_container_width=True)

    # --- 關鍵訂票對照 ---
    st.error("🚨 **官網訂票輸入指引 (請務必完全依照此順序)**")
    top = df.iloc[0]
    st.markdown(f"""
    **請在官網「多城市」搜尋輸入以下四段：**
    1. **第一段 (S1)**：`{top['S1段']}` | 日期：**{s1_suggested}**
    2. **第二段 (S2)**：`{top['S2段']}` | 日期：**{top['S2日期']}**
    3. **第三段 (S3)**：`{top['S3段']}` | 日期：**{top['S3日期']}**
    4. **第四段 (S4)**：`{top['S4段']}` | 日期：**{s4_suggested}**
    
    *💡 註：若目的地為布拉格，S2 出發通常需在 TPE 轉機。若 S1/S2 銜接不順，請將 S1 日期前後移動一天。*
    """)
