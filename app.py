import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [資料庫] 全球全量航點 ---
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
    "亞洲/大洋洲": {
        "日本": ["東京 (NRT/HND)", "大阪 (KIX)", "名古屋 (NGO)", "福岡 (FUK)", "札幌 (CTS)"],
        "紐澳": ["悉尼 (SYD)", "墨爾本 (MEL)", "奧克蘭 (AKL)", "基督城 (CHC)"],
        "樞紐": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "上海 (PVG)", "香港 (HKG)"]
    }
}

if 'searched' not in st.session_state:
    st.session_state.searched = False

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.title("𓃥 旅程設定中心")
    
    st.header("📍 1. 目的地設定")
    continent = st.selectbox("選擇大洲", list(WORLD_DATABASE.keys()))
    sub_region = st.selectbox("選擇區域", list(WORLD_DATABASE[continent].keys()))
    target_s2 = st.selectbox("選擇 S2 入境城市", WORLD_DATABASE[continent][sub_region])
    dest_iata_s2 = target_s2.split("(")[1].split(")")[0]

    # Open Jaw 設定
    is_oj = st.toggle("開啟 S3 Open Jaw (不同城市回程)", value=True)
    if is_oj:
        target_s3 = st.selectbox("選擇 S3 出境城市", WORLD_DATABASE[continent][sub_region], index=1 if len(WORLD_DATABASE[continent][sub_region]) > 1 else 0)
        dest_iata_s3 = target_s3.split("(")[1].split(")")[0]
    else:
        dest_iata_s3 = dest_iata_s2

    st.header("💺 2. 艙等配置")
    cabin_config = st.radio(
        "選擇航段艙等",
        ["全行程經濟艙 (V/W 艙)", "S2+S3 核心段商務艙 (D/Z 艙)"]
    )

    st.header("📅 3. 核心旅行日期")
    s2_core = st.date_input("S2 出發核心日", value=datetime(2026, 10, 15))
    s3_core = st.date_input("S3 回台核心日", value=s2_core + timedelta(days=12))
    
    if st.button("🚀 執行全球戰略分析", use_container_width=True):
        st.session_state.searched = True

# --- 3. 主畫面邏輯 ---

if not st.session_state.searched:
    st.title("✈️ White 6 Aero Explorer")
    st.subheader("四段票戰略規劃與 Open Jaw 指南")
    st.warning("👈 **請在左側側邊欄設定您的進出城市與艙等。**")
    
    st.markdown("""
    ---
    ### 💡 什麼是「S2/S3 商務艙 + Open Jaw」？
    這是頂級玩家最愛的規劃：
    * **Open Jaw (異地進出)**：例如「布拉格進、維也納出」。不走回頭路，省下中間跨國交通的回程時間。
    * **核心商務艙**：在最重要的兩段長程線（台灣 ➔ 國外、國外 ➔ 台灣）選擇商務艙。
    * **戰略價值**：利用外站啟動 (S1)，用接近來回經濟艙的預算，換取長程平躺商務艙的體驗。

    ### 四段結構對照：
    1. **S1 (經濟)**：外站 ➔ 台北 (啟動費率)
    2. **S2 (商務)**：台北 ➔ **入境城市 A** (假期開啟)
    3. **S3 (商務)**：**出境城市 B** ➔ 台北 (不走回頭路，舒適返家)
    4. **S4 (經濟)**：台北 ➔ 外站 (結尾段)
    """)
    st.image("https://images.unsplash.com/photo-1544016768-982d1554f0b9?auto=format&fit=crop&w=1200", caption="商務艙與 Open Jaw 讓跨國旅行更有效率且舒適")

else:
    st.title(f"📊 {'Open Jaw' if is_oj else '同點進出'} 行程分析報告")
    st.caption(f"航線：{dest_iata_s2} 進 / {dest_iata_s3} 出 | 艙等：{'長程商務' if '商務' in cabin_config else '全經濟'}")
    
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    # 模擬數據
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)"]
    res = []
    is_biz = "商務" in cabin_config
    
    for air in ["長榮 (BR)", "華航 (CI)"]:
        for hub in hubs:
            h_iata = hub.split("(")[1].split(")")[0]
            price = 33800 if not is_biz else 78500
            if is_oj: price += 1500 # Open Jaw 通常會微幅增加稅金
            
            res.append({
                "航空公司": air, "外站啟動": h_iata, "台灣機場": "TPE",
                "S1 (經濟)": f"{h_iata}➔TPE",
                "S2 (商務)": f"TPE➔{dest_iata_s2}" if is_biz else f"TPE➔{dest_iata_s2}",
                "S3 (商務)": f"{dest_iata_s3}➔TPE" if is_biz else f"{dest_iata_s3}➔TPE",
                "預估總價": price
            })

    df = pd.DataFrame(res).sort_values("預估總價")
    st.subheader("🔍 最佳路徑與航空公司比價清單")
    st.dataframe(df, use_container_width=True)

    # 官網操作卡片
    st.divider()
    st.header("🛠 官網「多城市」精準輸入指南")
    top = df.iloc[0]
    st.error(f"請在 **{top['航空公司']}** 官網搜尋時，分別為各段選擇正確城市與艙等：")
    
    c1, c2 = st.columns(2)
    c1.metric("第一段 (S1 - 經濟)", top['S1 (經濟)'], str(s1_suggested))
    c1.metric("第二段 (S2 - 商務)" if is_biz else "第二段 (S2 - 經濟)", top['S2 (商務)'], str(s2_core))
    c2.metric("第三段 (S3 - 商務)" if is_biz else "第三段 (S3 - 經濟)", top['S3 (商務)'], str(s3_core))
    c2.metric("第四段 (S4 - 經濟)", f"TPE➔{top['外站啟動']}", str(s4_suggested))

    st.info(f"💡 **Open Jaw 提示**：您已選擇從 **{dest_iata_s2}** 入境，並從 **{dest_iata_s3}** 離開。請確保官網輸入的 S3 起點為 {dest_iata_s3}。")
    
    if st.button("⬅️ 返回教學解說"):
        st.session_state.searched = False
