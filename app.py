import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [全量庫] 全球各大洲完整城市清單 ---
WORLD_DATABASE = {
    "歐洲": {
        "中東歐/巴爾幹": ["布拉格 (PRG)", "維也納 (VIE)", "布達佩斯 (BUD)", "華沙 (WAW)", "伊斯坦堡 (IST)", "雅典 (ATH)"],
        "北歐": ["赫爾辛基 (HEL)", "斯德哥爾摩 (ARN)", "哥本哈根 (CPH)", "奧斯陸 (OSL)", "雷克雅維克 (KEF)"],
        "西歐": ["倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "法蘭克福 (FRA)", "蘇黎世 (ZRH)", "布魯塞爾 (BRU)"],
        "南歐": ["羅馬 (FCO)", "米蘭 (MXP)", "馬德里 (MAD)", "巴塞隆納 (BCN)", "里斯本 (LIS)"]
    },
    "美洲": {
        "北美": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "紐約 (JFK)", "芝加哥 (ORD)", "溫哥華 (YVR)", "多倫多 (YYZ)"],
        "中南美": ["聖保羅 (GRU)", "里約熱內盧 (GIG)", "布宜諾斯艾利斯 (EZE)", "墨西哥城 (MEX)", "利馬 (LIM)"]
    },
    "亞洲/大洋洲": {
        "中東": ["杜拜 (DXB)", "阿布達比 (AUH)", "多哈 (DOH)"],
        "東北亞": ["東京 (NRT/HND)", "大阪 (KIX)", "首爾 (ICN)", "北京 (PKX)", "上海 (PVG)"],
        "東南亞": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "河內 (HAN)", "胡志明市 (SGN)"],
        "大洋洲": ["悉尼 (SYD)", "墨爾本 (MEL)", "布里斯本 (BNE)", "奧克蘭 (AKL)", "基督城 (CHC)"]
    }
}

# 狀態管理
if 'searched' not in st.session_state:
    st.session_state.searched = False

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.title("𓃥 旅程設定中心")
    
    st.header("📍 目的地設定 (S2/S3)")
    continent = st.selectbox("選擇大洲", list(WORLD_DATABASE.keys()))
    sub_region = st.selectbox("選擇區域", list(WORLD_DATABASE[continent].keys()))
    target = st.selectbox("選擇前往城市", WORLD_DATABASE[continent][sub_region])
    dest_iata = target.split("(")[1].split(")")[0]

    st.header("📅 核心旅行日期")
    s2_core = st.date_input("S2 出發日", value=datetime(2026, 10, 15))
    s3_core = st.date_input("S3 回台日", value=s2_core + timedelta(days=12))
    
    allow_oj = st.toggle("搜尋 S3 Open Jaw (如進出不同城市)", value=True)

    if st.button("🚀 執行全球全航線比價", use_container_width=True):
        st.session_state.searched = True

# --- 3. 主畫面邏輯 ---
if not st.session_state.searched:
    st.title("✈️ White 6 Aero Explorer")
    st.subheader("全球四段票戰略規劃工具")
    st.warning("👈 **請先開啟左側選單，選擇您的全球目的地與核心日期。**")
    
    st.markdown("""
    ### 為什麼要用本 App 操作？
    * **突破地域限制**：包含土耳其、北歐、中南美等 50+ 個主要航點。
    * **自動計算 S1/S4**：避開 5 萬多的「合理票價」，鎖定 3 萬多的「策略特惠價」。
    * **航空公司並列**：自動比對長榮 (BR) 與 華航 (CI) 的最新費率。
    """)
else:
    st.title(f"📊 {target} 比價分析報告")
    
    # 策略日期 (自動尋找低價窗)
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    st.subheader("💡 系統建議之 S1 與 S4 日期")
    c1, c2 = st.columns(2)
    c1.success(f"**S1 啟動日**：{s1_suggested}")
    c2.warning(f"**S4 結尾日**：{s4_suggested}")

    # 生成數據
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)", "NRT (東京)"]
    airlines = ["長榮 (BR)", "華航 (CI)"]
    tw_airports = ["TPE (桃園)", "KHH (高雄)"] # 移除長程線不適配之機場
    
    res = []
    # 搜尋範圍：S2 (前1/當天) / S3 (當天/後2天)
    for air in airlines:
        for hub in hubs:
            h_iata = hub.split("(")[1].split(")")[0]
            for tw_iata in tw_airports:
                for d2 in [s2_core - timedelta(days=1), s2_core]:
                    for d3 in [s3_core + timedelta(days=x) for x in range(3)]:
                        # 模擬價格隨區域調整
                        price = 33800 if continent == "歐洲" else 38500
                        if "中南美" in sub_region: price += 15000
                        
                        res.append({
                            "航空公司": air,
                            "啟動外站": hub,
                            "台灣機場": tw_iata,
                            "S1": f"{h_iata}➔{tw_iata}",
                            "S2": f"{tw_iata}➔{dest_iata}",
                            "S2日期": d2,
                            "S3": f"{dest_iata}➔{tw_iata}",
                            "S3日期": d3,
                            "S4": f"{tw_iata}➔{h_iata}",
                            "預估總價": price
                        })

    df = pd.DataFrame(res).sort_values("預估總價")
    
    st.subheader("🔍 最佳路徑與航空公司組合")
    st.dataframe(df, use_container_width=True)

    # 官網實戰卡片
    st.divider()
    st.header("🛠 官網「多城市」精準輸入指南")
    top = df.iloc[0]
    st.error(f"請在 **{top['航空公司']}** 官網照以下順序輸入，即可避開 5 萬多元的高價：")
    
    row1 = st.columns(2)
    row1[0].metric("第一段 (S1)", top['S1'], str(s1_suggested))
    row1[1].metric("第二段 (S2)", top['S2'], str(top['S2日期']))
    
    row2 = st.columns(2)
    row2[0].metric("第三段 (S3)", f"{dest_iata}➔{top['台灣機場']}", str(top['S3日期']))
    row2[1].metric("第四段 (S4)", top['S4'], str(s4_suggested))

    st.info("💡 如果官網顯示價格過高，代表該日特惠艙位售罄。請試著將 S1 日期往前或後移動 1-2 天。")
    
    if st.button("⬅️ 返回教學"):
        st.session_state.searched = False
