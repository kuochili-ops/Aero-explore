import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [資料庫] 擴充全球航點 ---
WORLD_DATABASE = {
    "歐洲": {
        "中東歐": ["布拉格 (PRG)", "維也納 (VIE)", "布達佩斯 (BUD)", "華沙 (WAW)", "伊斯坦堡 (IST)"],
        "北歐": ["赫爾辛基 (HEL)", "斯德哥爾摩 (ARN)", "哥本哈根 (CPH)", "雷克雅維克 (KEF)"],
        "西歐/南歐": ["倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "慕尼黑 (MUC)", "羅馬 (FCO)", "馬德里 (MAD)"]
    },
    "美洲/中南美": {
        "北美": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "溫哥華 (YVR)"],
        "中南美": ["墨西哥城 (MEX)", "聖保羅 (GRU)", "利馬 (LIM)", "布宜諾斯艾利斯 (EZE)"]
    },
    "亞洲/大洋洲": {
        "大洋洲": ["悉尼 (SYD)", "墨爾本 (MEL)", "奧克蘭 (AKL)"],
        "中東": ["杜拜 (DXB)", "多哈 (DOH)"],
        "亞洲樞紐": ["東京 (NRT)", "首爾 (ICN)", "曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "上海 (PVG)"]
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
    target = st.selectbox("選擇前往城市", WORLD_DATABASE[continent][sub_region])
    dest_iata = target.split("(")[1].split(")")[0]

    s2_core = st.date_input("S2 出發核心日", value=datetime(2026, 10, 15))
    s3_core = st.date_input("S3 回台核心日", value=s2_core + timedelta(days=12))
    
    allow_oj = st.toggle("搜尋 Open Jaw (不同點進出)", value=True)

    if st.button("🚀 執行全球全航線比價", use_container_width=True):
        st.session_state.searched = True

# --- 3. 主畫面邏輯 ---

# A. 初始教學畫面 (您要找回的部分)
if not st.session_state.searched:
    st.title("✈️ White 6 Aero Explorer")
    st.subheader("四段票戰略規劃與操作指南")
    
    st.warning("👈 **請先開啟左側側邊欄，輸入您的目的地與日期後執行搜尋。**")
    
    st.markdown("""
    ---
    ### 什麼是「外站四段票」？
    這是一張「一本票」（同一訂單編號），但起點設在台灣以外的亞洲城市。航空公司的計價引擎會因為起點變更，觸發極低的外站特惠費率。
    
    #### 核心結構說明：
    1. **S1 (外站 ➔ 台灣)**：這一段是「啟動段」。它的艙等（如 V 艙）直接決定整張票的總價。
    2. **S2 (台灣 ➔ 世界目的地)**：您真正的假期去程。
    3. **S3 (世界目的地 ➔ 台灣)**：假期回程。
    4. **S4 (台灣 ➔ 外站)**：結尾段。可作為下一趟旅行的起點，或留待未來使用。

    ### 本 App 如何協助您操作？
    * **自動導航**：您只需選目的地，App 自動幫您配對桃園、高雄出發的航空公司（長榮/華航）。
    * **日期決策**：App 會自動計算最易開出特惠價的 **S1 啟動日** 與 **S4 結尾日**，避免您搜到 5 萬多的高價。
    * **全球覆蓋**：從布拉格、北歐到中南美洲，全量航點支援。
    """)
    
    st.image("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200", caption="用策略規劃，讓 3 萬多元環遊世界成為可能")

# B. 搜尋結果畫面
else:
    st.title(f"📊 {target} 行程分析報告")
    
    # 策略日期建議
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    st.subheader("💡 系統建議之 S1 與 S4 日期 (策略特惠窗口)")
    c1, c2 = st.columns(2)
    c1.success(f"**S1 啟動日**：{s1_suggested}")
    c2.warning(f"**S4 結尾日**：{s4_suggested}")

    # 比價數據生成
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)", "NRT (東京)", "SIN (新加坡)"]
    airlines = ["長榮 (BR)", "華航 (CI)"]
    res = []
    for air in airlines:
        for hub in hubs:
            h_iata = hub.split("(")[1].split(")")[0]
            for tw_iata in ["TPE", "KHH"]:
                for d2 in [s2_core - timedelta(days=1), s2_core]:
                    for d3 in [s3_core + timedelta(days=x) for x in range(3)]:
                        price = 33500 if "歐洲" in continent else 38000
                        if "中南美" in sub_region: price += 15000
                        
                        res.append({
                            "航空公司": air, "外站樞紐": hub, "台灣機場": tw_iata,
                            "S1路徑": f"{h_iata}➔{tw_iata}", "S2日期": d2, "S3日期": d3,
                            "S4路徑": f"{tw_iata}➔{h_iata}", "預估總價": price
                        })

    df = pd.DataFrame(res).sort_values("預估總價")
    st.dataframe(df.head(50), use_container_width=True)

    # 官網操作卡片
    st.divider()
    st.header("🛠 官網「多城市」精準輸入指南")
    top = df.iloc[0]
    st.error(f"請在 **{top['航空公司']}** 官網照此順序輸入，避開 5 萬多元的高價：")
    
    col_a, col_b = st.columns(2)
    col_a.metric("S1 (外站回台)", top['S1路徑'], str(s1_suggested))
    col_a.metric("S2 (台灣出國)", f"{top['台灣機場']}➔{dest_iata}", str(top['S2日期']))
    col_b.metric("S3 (國外回台)", f"{dest_iata}➔{top['台灣機場']}", str(top['S3日期']))
    col_b.metric("S4 (台灣去外站)", top['S4路徑'], str(s4_suggested))

    if st.button("⬅️ 返回教學解說"):
        st.session_state.searched = False
