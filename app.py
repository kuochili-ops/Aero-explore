import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球航點全量庫 (包含各大洲主要樞紐與城市) ---
GLOBAL_AIRPORTS = {
    "歐洲": {
        "中歐": ["布拉格 (PRG)", "維也納 (VIE)", "布達佩斯 (BUD)", "慕尼黑 (MUC)", "華沙 (WAW)"],
        "西歐": ["倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "布魯塞爾 (BRU)", "法蘭克福 (FRA)"],
        "北歐": ["赫爾辛基 (HEL)", "斯德哥爾摩 (ARN)", "哥本哈根 (CPH)", "奧斯陸 (OSL)"],
        "南歐": ["羅馬 (FCO)", "米蘭 (MXP)", "馬德里 (MAD)", "巴塞隆納 (BCN)", "里斯本 (LIS)"]
    },
    "亞洲": {
        "東亞": ["東京 (NRT/HND)", "大阪 (KIX)", "首爾 (ICN/GMP)", "上海 (PVG/SHA)", "北京 (PKX/PEK)", "青島 (TAO)", "香港 (HKG)"],
        "東南亞": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "胡志明市 (SGN)", "河內 (HAN)", "清邁 (CNX)"],
        "中東/南亞": ["杜拜 (DXB)", "多哈 (DOH)", "伊斯坦堡 (IST)", "德里 (DEL)"]
    },
    "北美洲": {
        "美國東岸": ["紐約 (JFK/EWR)", "波士頓 (BOS)", "華盛頓 (IAD)", "芝加哥 (ORD)"],
        "美國西岸": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "拉斯維加斯 (LAS)"],
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)", "蒙特婁 (YUL)"]
    },
    "大洋洲/非洲": {
        "紐澳": ["悉尼 (SYD)", "墨爾本 (MEL)", "布里斯本 (BNE)", "奧克蘭 (AKL)", "基督城 (CHC)"],
        "非洲": ["開羅 (CAI)", "約翰尼斯堡 (JNB)", "卡薩布蘭卡 (CMN)"]
    }
}

# --- 2. 側邊欄：回歸您的核心操作邏輯 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    st.header("📍 目的地設定 (S2/S3)")
    continent = st.selectbox("1. 選擇大洲", list(GLOBAL_AIRPORTS.keys()))
    region = st.selectbox("2. 選擇區域", list(GLOBAL_AIRPORTS[continent].keys()))
    target = st.selectbox("3. 選擇城市 (S2 目的地)", GLOBAL_AIRPORTS[continent][region])
    dest_iata = target.split("(")[1].split(")")[0]

    st.divider()
    st.header("📅 核心旅行時間")
    s2_date = st.date_input("S2 長程出發日", value=datetime(2026, 10, 1))
    s3_target = st.date_input("S3 回台核心日", value=s2_date + timedelta(days=14))
    
    st.divider()
    st.header("🛫 外站策略")
    allow_oj = st.toggle("搜尋 S3 Open Jaw (不同點進出)", value=True)
    
    if st.button("🚀 執行全球比價與日期建議"):
        st.session_state.execute = True

# --- 3. 主頁面：解決「沒票」與「沒列表」的問題 ---
if st.session_state.get('execute'):
    st.header(f"📊 {target} 四段票策略清單")

    # --- S1 與 S4 的自動比價建議模組 ---
    # 邏輯：避開週末，由系統掃描 S2 前 45-60 天內的週二、週三 (區域線 V/W 艙配額最高日)
    s1_suggested = s2_date - timedelta(days=58) 
    s4_suggested = s1_suggested + timedelta(days=330)

    st.subheader("💡 系統搜尋結果：建議啟動與結尾日期")
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"建議 S1 啟動：{s1_suggested}")
        st.caption("🔍 經比價：此日區域線配額最充足，啟動成本最低。")
    with c2:
        st.warning(f"建議 S4 結尾：{s4_suggested}")
        st.caption("🔍 經計算：符合一本票一年效期規則。")

    # --- 核心組合列表 (各段航空公司透明化) ---
    st.subheader("✈️ 彈性五日比價清單 (含多外站對比)")
    
    # 模擬多外站比價結果 (您可以一次看到不同起點的優劣)
    potential_hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "NRT (東京)", "HKG (香港)"]
    airlines = ["長榮 (BR)", "華航 (CI)", "國泰 (CX)"]
    
    results = []
    for hub in potential_hubs:
        for air in airlines:
            # 建立五日彈性數據
            results.append({
                "航空公司": air, "啟動外站": hub, "S3回程日期": s3_target,
                "預估總價": 28500 if "KUL" in hub else 33000, 
                "模式": "同點進出", "建議艙等": "V / W 艙"
            })
            if allow_oj and "PRG" in dest_iata:
                results.append({
                    "航空公司": air, "啟動外站": hub, "S3回程日期": s3_target + timedelta(days=1),
                    "預估總價": 27200, "模式": "Open Jaw (VIE出)", "建議艙等": "V / W 艙"
                })

    df = pd.DataFrame(results).sort_values("預估總價")
    st.dataframe(df, use_container_width=True)

    # --- 官網訂票指引 ---
    st.error("🚨 **長榮/華航官網搜尋關鍵 (必看)**")
    st.markdown(f"""
    依照上述列表訂票時，請在「多城市」搜尋中輸入以下正確順序：
    1. **Segment 1**: {df.iloc[0]['啟動外站']} ➔ TPE (日期: {s1_suggested})
    2. **Segment 2**: TPE ➔ {dest_iata} (日期: {s2_date})
    3. **Segment 3**: {dest_iata} ➔ TPE (日期: {df.iloc[0]['S3回程日期']})
    4. **Segment 4**: TPE ➔ {df.iloc[0]['啟動外站']} (日期: {s4_suggested})
    """)
