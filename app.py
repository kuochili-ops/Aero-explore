import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [資料庫] 全球航點 ---
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
        "日本全航點": ["東京成田 (NRT)", "東京羽田 (HND)", "大阪關西 (KIX)", "名古屋 (NGO)", "福岡 (FUK)", "札幌 (CTS)"],
        "東南亞/亞洲樞紐": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "上海 (PVG)", "香港 (HKG)"]
    }
}

# 狀態管理
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
        ["全行程經濟艙 (V/W 艙)", "S3+S4 升等商務艙 (D/Z 艙)"],
        help="選擇 S3+S4 商務艙後，回台長程段與最後一段回外站將配置商務艙位。"
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
    ### 💡 為什麼要選擇 S3/S4 商務艙？
    * **長途飛行的救贖**：在假期的最後，從歐洲、美洲飛回台灣（S3）時，能有全平躺座椅休息，能讓您回國後直接無縫接軌上班。
    * **極致性價比**：四段票的「商務艙」價格往往僅需 6-8 萬，比直接購買來回經濟艙（5 萬多）更有感升級。
    * **行李與貴賓室**：享有更高的行李額度，且 S4 飛往外站時可再次享受商務艙待遇。

    ### 四段結構回顧：
    1. **S1 (外站➔台)**：經濟艙啟動。
    2. **S2 (台➔國外)**：假期去程。
    3. **S3 (國外➔台)**：**[可選商務]** 假期回程，長途飛行最需要舒適度。
    4. **S4 (台➔外站)**：**[可選商務]** 結尾段，延續尊榮感。
    """)
    
# B. 搜尋結果畫面
else:
    st.title(f"📊 {target} 行程分析報告 ({'混合艙位' if '商務' in cabin_config else '全經濟'})")
    
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    # 比價數據
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)", "NRT (東京)"]
    airlines = ["長榮 (BR)", "華航 (CI)"]
    res = []
    
    is_biz = "商務" in cabin_config
    
    for air in airlines:
        for hub in hubs:
            h_iata = hub.split("(")[1].split(")")[0]
            for tw_iata in ["TPE", "KHH"]:
                for d2 in [s2_core]:
                    for d3 in [s3_core]:
                        # 模擬加價邏輯：商務艙加價 2.5w - 4w 不等
                        base_price = 33500 if "歐洲" in continent else 38000
                        if is_biz: base_price += 28000 
                        
                        res.append({
                            "航空公司": air, "外站樞紐": hub, "台灣機場": tw_iata,
                            "S1-S2 艙等": "經濟 (V/W)",
                            "S3-S4 艙等": "商務 (D/Z)" if is_biz else "經濟 (V/W)",
                            "S1 啟動": f"{h_iata}➔{tw_iata}",
                            "S3 回台": f"{dest_iata}➔{tw_iata}",
                            "預估總價": base_price
                        })

    df = pd.DataFrame(res).sort_values("預估總價")
    st.dataframe(df, use_container_width=True)

    # 官網實戰指引
    st.divider()
    st.header("🛠 官網「多城市」精準輸入指南")
    top = df.iloc[0]
    st.error(f"請在 **{top['航空公司']}** 官網搜尋時，分別為各段選擇正確艙等：")
    
    col1, col2 = st.columns(2)
    col1.metric("S1 & S2 (選經濟艙)", "建議日期", str(s1_suggested))
    col2.metric("S3 & S4 (選商務艙)" if is_biz else "S3 & S4 (選經濟艙)", "建議日期", str(s4_suggested))

    st.info("💡 **小撇步**：在官網搜尋時，若某段商務艙價格異常高，請嘗試更換 S1 或 S4 的日期以觸發 D/Z 艙特惠位。")
    
    if st.button("⬅️ 返回操作解說"):
        st.session_state.searched = False
