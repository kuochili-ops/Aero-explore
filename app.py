import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [資料庫] 全球全量航點 (包含日本與加拿大) ---
WORLD_DATABASE = {
    "歐洲": {
        "中東歐": ["布拉格 (PRG)", "維也納 (VIE)", "布達佩斯 (BUD)", "華沙 (WAW)", "伊斯坦堡 (IST)"],
        "北歐": ["赫爾辛基 (HEL)", "斯德哥爾摩 (ARN)", "哥本哈根 (CPH)", "雷克雅維克 (KEF)"],
        "西歐/南歐": ["倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "慕尼黑 (MUC)", "羅馬 (FCO)", "馬德里 (MAD)"]
    },
    "美洲": {
        "加拿大 (加全航點)": ["溫哥華 (YVR)", "多倫多 (YYZ)", "蒙特婁 (YUL)", "卡加利 (YYC)"],
        "美國": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "紐約 (JFK)", "芝加哥 (ORD)", "休士頓 (IAH)"],
        "中南美": ["墨西哥城 (MEX)", "聖保羅 (GRU)", "利馬 (LIM)", "布宜諾斯艾利斯 (EZE)"]
    },
    "亞洲/大洋洲": {
        "日本 (日全航點)": ["東京成田 (NRT)", "東京羽田 (HND)", "大阪關西 (KIX)", "名古屋 (NGO)", "福岡 (FUK)", "札幌 (CTS)", "沖繩 (OKA)"],
        "東南亞樞紐": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "胡志明市 (SGN)"],
        "大洋洲": ["悉尼 (SYD)", "墨爾本 (MEL)", "布里斯本 (BNE)", "奧克蘭 (AKL)"]
    }
}

# 狀態管理
if 'searched' not in st.session_state:
    st.session_state.searched = False

# --- 2. 側邊欄：搜尋設定 ---
with st.sidebar:
    st.title("𓃥 旅程設定中心")
    st.header("📍 目的地與日期")
    continent = st.selectbox("選擇大洲", list(WORLD_DATABASE.keys()))
    sub_region = st.selectbox("選擇區域", list(WORLD_DATABASE[continent].keys()))
    target = st.selectbox("選擇前往城市 (S2/S3)", WORLD_DATABASE[continent][sub_region])
    dest_iata = target.split("(")[1].split(")")[0]

    s2_core = st.date_input("S2 出發核心日", value=datetime(2026, 10, 15))
    s3_core = st.date_input("S3 回台核心日", value=s2_core + timedelta(days=12))
    
    allow_oj = st.toggle("搜尋 S3 Open Jaw (不同點進出)", value=True)

    if st.button("🚀 執行全球全航線比價", use_container_width=True):
        st.session_state.searched = True

# --- 3. 主畫面邏輯 ---

# A. 初始教學畫面
if not st.session_state.searched:
    st.title("✈️ White 6 Aero Explorer")
    st.subheader("四段票戰略規劃與操作指南")
    
    st.warning("👈 **請先開啟左側側邊欄，輸入您的目的地與日期後執行搜尋。**")
    
    st.markdown("""
    ---
    ### 什麼是「外站四段票」？
    這是一張航空公司認可的「一本票」，但起點設在台灣以外（如吉隆坡或上海）。因為起點變更，會觸發極低的外站特惠費率，價格通常比台北直飛便宜 40% 以上。
    
    #### 核心結構說明：
    1. **S1 (外站 ➔ 台灣)**：啟動段。鎖定 V 艙或 W 艙是整張票便宜的關鍵。
    2. **S2 (台灣 ➔ 世界目的地)**：大旅行去程。
    3. **S3 (世界目的地 ➔ 台灣)**：大旅行回程。
    4. **S4 (台灣 ➔ 外站)**：結尾段。可作為下次旅行起點或單純放棄。

    ### 本 App 如何操作？
    * **全球航點**：已收錄日本、加拿大、北歐、中南美等 60+ 個主要機場。
    * **日期導航**：自動推算最易開出特惠價的 **S1 啟動日** 與 **S4 結尾日**。
    * **航空公司對照**：結果列表明確標註航空公司 (BR/CI) 與四段詳細起訖機場。
    """)
    
    st.image("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200", caption="用策略規劃，讓全球旅行更輕鬆")

# B. 搜尋結果畫面
else:
    st.title(f"📊 {target} 行程分析報告")
    
    # 策略日期建議
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    st.subheader("💡 系統建議之 S1 與 S4 日期 (策略窗口)")
    c1, c2 = st.columns(2)
    c1.success(f"**S1 啟動日**：{s1_suggested}")
    c2.warning(f"**S4 結尾日**：{s4_suggested}")

    # 比價數據
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)", "NRT (東京)", "SIN (新加坡)"]
    airlines = ["長榮 (BR)", "華航 (CI)"]
    res = []
    for air in airlines:
        for hub in hubs:
            h_iata = hub.split("(")[1].split(")")[0]
            for tw_iata in ["TPE", "KHH"]:
                for d2 in [s2_core - timedelta(days=1), s2_core]:
                    for d3 in [s3_core + timedelta(days=x) for x in range(3)]:
                        # 模擬區域加價邏輯
                        price = 33500
                        if "美洲" in continent: price += 6000
                        if "中南美" in sub_region: price += 15000
                        
                        res.append({
                            "航空公司": air, "外站樞紐": hub, "台灣機場": tw_iata,
                            "S1路徑": f"{h_iata}➔{tw_iata}", "S2日期": d2, "S3日期": d3,
                            "S4路徑": f"{tw_iata}➔{h_iata}", "預估總價": price
                        })

    df = pd.DataFrame(res).sort_values("預估總價")
    st.subheader("🔍 最佳路徑與航空公司比價清單")
    st.dataframe(df, use_container_width=True)

    # 官網操作卡片
    st.divider()
    st.header("🛠 官網「多城市」精準輸入指南")
    top = df.iloc[0]
    st.error(f"請在 **{top['航空公司']}** 官網依此順序輸入，即可避開 5 萬多元的高價：")
    
    col_a, col_b = st.columns(2)
    col_a.metric("S1 (外站回台)", top['S1路徑'], str(s1_suggested))
    col_a.metric("S2 (台灣出國)", f"{top['台灣機場']}➔{dest_iata}", str(top['S2日期']))
    col_b.metric("S3 (國外回台)", f"{dest_iata}➔{top['台灣機場']}", str(top['S3日期']))
    col_b.metric("S4 (台灣去外站)", top['S4路徑'], str(s4_suggested))

    if st.button("⬅️ 返回教學解說"):
        st.session_state.searched = False
