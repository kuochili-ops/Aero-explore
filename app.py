import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [資料庫] 全球航點 (含日本與加拿大) ---
WORLD_DATABASE = {
    "歐洲": {
        "中東歐": ["布拉格 (PRG)", "維也納 (VIE)", "布達佩斯 (BUD)", "華沙 (WAW)", "伊斯坦堡 (IST)"],
        "北歐": ["赫爾辛基 (HEL)", "斯德哥爾摩 (ARN)", "哥本哈根 (CPH)", "雷克雅維克 (KEF)"],
        "西歐/南歐": ["倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "慕尼黑 (MUC)", "羅馬 (FCO)", "馬德里 (MAD)"]
    },
    "美洲": {
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)", "蒙特婁 (YUL)", "卡加利 (YYC)"],
        "美國": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "西雅圖 (SEA)"],
        "中南美": ["墨西哥城 (MEX)", "聖保羅 (GRU)", "利馬 (LIM)"]
    },
    "亞洲/日本": {
        "日本全航點": ["東京 (NRT/HND)", "大阪 (KIX)", "名古屋 (NGO)", "福岡 (FUK)", "札幌 (CTS)"],
        "東南亞/亞洲樞紐": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "上海 (PVG)", "香港 (HKG)"]
    }
}

if 'searched' not in st.session_state:
    st.session_state.searched = False

# --- 2. 側邊欄：搜尋設定 ---
with st.sidebar:
    st.title("𓃥 旅程設定中心")
    
    st.header("📍 1. 目的地設定")
    continent = st.selectbox("選擇大洲", list(WORLD_DATABASE.keys()))
    sub_region = st.selectbox("選擇區域", list(WORLD_DATABASE[continent].keys()))
    target = st.selectbox("選擇前往城市 (S2/S3)", WORLD_DATABASE[continent][sub_region])
    dest_iata = target.split("(")[1].split(")")[0]

    st.header("💺 2. 艙等配置")
    cabin_config = st.radio(
        "選擇航段艙等",
        ["全行程經濟艙 (V/W 艙)", "S2+S3 核心段商務艙 (D/Z 艙)"],
        help="選擇 S2+S3 商務艙後，台灣出發的長程段將配置商務艙位，S1/S4 則維持經濟艙。"
    )

    st.header("📅 3. 核心大旅行日期")
    s2_core = st.date_input("S2 出發核心日", value=datetime(2026, 10, 15))
    s3_core = st.date_input("S3 回台核心日", value=s2_core + timedelta(days=12))
    
    if st.button("🚀 執行全球戰略比價", use_container_width=True):
        st.session_state.searched = True

# --- 3. 主畫面邏輯 ---

# A. 初始教學畫面
if not st.session_state.searched:
    st.title("✈️ White 6 Aero Explorer")
    st.subheader("四段票戰略規劃與操作指南")
    
    st.warning("👈 **請先在左側完成目的地與「艙等配置」設定後執行搜尋。**")
    
    st.markdown("""
    ---
    ### 💡 什麼是「S2+S3 核心段商務艙」？
    這是最受商務旅客歡迎的配置方式。將預算花在刀口上：
    * **去回程（S2/S3）**：通常是長達 10-15 小時的跨洲航線，選擇商務艙可使用平躺睡床，徹底解決時差問題。
    * **啟動與結尾（S1/S4）**：屬於 3-5 小時內的短程接駁，維持經濟艙以壓低整張票的總價。

    ### 四段結構配置：
    1. **S1 (外站➔台)**：經濟艙 (艙位決定價格起點)。
    2. **S2 (台➔國外)**：**[商務艙]** 假期開始，享受貴賓室與平躺飛行。
    3. **S3 (國外➔台)**：**[商務艙]** 假期結束，舒適回台無縫接軌生活。
    4. **S4 (台➔外站)**：經濟艙。
    """)
    
# B. 搜尋結果畫面
else:
    st.title(f"📊 {target} 行程分析報告 ({'長程商務' if '商務' in cabin_config else '全經濟'})")
    
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    # 比價數據
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)", "NRT (東京)"]
    res = []
    is_biz = "商務" in cabin_config
    
    for air in ["長榮 (BR)", "華航 (CI)"]:
        for hub in hubs:
            h_iata = hub.split("(")[1].split(")")[0]
            for tw_iata in ["TPE", "KHH"]:
                # 模擬加價邏輯
                base_price = 33500 if "歐洲" in continent else 38000
                if is_biz: base_price += 45000 # 長程商務加價較高
                
                res.append({
                    "航空公司": air, "外站樞紐": hub, "台灣機場": tw_iata,
                    "S1/S4 艙等": "經濟 (V/W)",
                    "S2/S3 艙等": "商務 (D/Z)" if is_biz else "經濟 (V/W)",
                    "S1路徑": f"{h_iata}➔{tw_iata}",
                    "S2路徑": f"{tw_iata}➔{dest_iata}",
                    "預估總價": base_price
                })

    df = pd.DataFrame(res).sort_values("預估總價")
    st.subheader("🔍 最佳路徑與航空公司比價清單")
    st.dataframe(df, use_container_width=True)

    # 官網實戰指引
    st.divider()
    st.header("🛠 官網「多城市」精準輸入指南")
    top = df.iloc[0]
    st.error(f"請在 **{top['航空公司']}** 官網搜尋時，分別為各段選擇正確艙等：")
    
    row1_a, row1_b = st.columns(2)
    row1_a.metric("S1 (經濟艙)", top['S1路徑'], str(s1_suggested))
    row1_b.metric("S2 (商務艙)" if is_biz else "S2 (經濟艙)", f"{top['台灣機場']}➔{dest_iata}", str(s2_core))
    
    row2_a, row2_b = st.columns(2)
    row2_a.metric("S3 (商務艙)" if is_biz else "S3 (經濟艙)", f"{dest_iata}➔{top['台灣機場']}", str(s3_core))
    row2_b.metric("S4 (經濟艙)", f"{top['台灣機場']}➔{top['外站樞紐'].split('(')[1][:3]}", str(s4_suggested))

    st.info("💡 **注意**：S2/S3 改選商務艙後，總價會從 3 萬多跳至 7-8 萬。這依然比直接買單純來回商務艙（通常要 12 萬+）便宜非常多！")
    
    if st.button("⬅️ 返回操作解說"):
        st.session_state.searched = False
