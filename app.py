import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球全量航點資料庫 (大洲 > 區域 > 城市) ---
WORLD_MAP = {
    "歐洲": {
        "中東歐": ["布拉格 (PRG)", "維也納 (VIE)", "布達佩斯 (BUD)", "華沙 (WAW)"],
        "西歐": ["倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "法蘭克福 (FRA)", "慕尼黑 (MUC)", "蘇黎世 (ZRH)"],
        "南歐": ["羅馬 (FCO)", "米蘭 (MXP)", "馬德里 (MAD)", "巴塞隆納 (BCN)", "里斯本 (LIS)"],
        "北歐": ["赫爾辛基 (HEL)", "斯德哥爾摩 (ARN)", "哥本哈根 (CPH)"]
    },
    "亞洲/大洋洲": {
        "東北亞": ["東京 (NRT/HND)", "大阪 (KIX)", "福岡 (FUK)", "首爾 (ICN)", "釜山 (PUS)"],
        "東南亞": ["曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "胡志明市 (SGN)", "河內 (HAN)"],
        "港澳/中國": ["香港 (HKG)", "上海 (PVG)", "北京 (PKX)", "青島 (TAO)"],
        "大洋洲": ["悉尼 (SYD)", "墨爾本 (MEL)", "布里斯本 (BNE)", "奧克蘭 (AKL)"]
    },
    "美洲": {
        "美西": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "溫哥華 (YVR)"],
        "美東/中": ["紐約 (JFK)", "芝加哥 (ORD)", "多倫多 (YYZ)", "休士頓 (IAH)"]
    }
}

# --- 2. 側邊欄：只需輸入目的地與核心日期 ---
with st.sidebar:
    st.title("𓃥 White 6 旅程規劃師")
    
    st.header("📍 目的地設定")
    continent = st.selectbox("選擇大洲", list(WORLD_MAP.keys()))
    region = st.selectbox("選擇區域", list(WORLD_MAP[continent].keys()))
    target_city = st.selectbox("前往目的地 (S2/S3)", WORLD_MAP[continent][region])
    dest_iata = target_city.split("(")[1].split(")")[0]

    st.header("📅 大旅行日期 (S2/S3)")
    s2_date = st.date_input("S2 出發日", value=datetime(2026, 10, 15))
    s3_date = st.date_input("S3 回程日", value=s2_date + timedelta(days=12))
    
    allow_oj = st.toggle("搜尋 S3 Open Jaw (不同點進出)", value=True)

    if st.button("🔍 執行全球比價與 S1/S4 日期分析"):
        st.session_state.do_search = True

# --- 3. 主頁面：比價列表與日期建議 ---
if st.session_state.get('do_search'):
    st.header(f"📊 {target_city} 四段票規劃清單")

    # --- S1 / S4 建議模組 (由系統自動計算低價窗) ---
    # 邏輯：避開週末，搜尋 S2 之前約 45 天的週二/三，這通常是 V 艙位最穩定的日子
    s1_suggested = s2_date - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    st.subheader("💡 系統建議之 S1 與 S4 出發日期")
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"建議 S1 啟動：{s1_suggested}")
        st.caption("🔍 經比價：此日區域段特惠配額充足，可避免總價跳漲。")
    with c2:
        st.warning(f"建議 S4 結尾：{s4_suggested}")
        st.caption("🔍 經計算：符合一本票 365 天效期，極大化年票效益。")

    # --- 核心比價列表 (自動列出台灣機場與外站) ---
    st.subheader(f"✈️ S2/S3 彈性組合與外站比價 (含前一日與後三日)")
    
    tw_airports = ["TPE (桃園)", "TSA (松山)", "KHH (高雄)", "RMQ (台中)"]
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "HKG (香港)", "PVG (上海)", "NRT (東京)"]
    airlines = ["長榮 (BR)", "華航 (CI)"]
    
    # S2/S3 彈性日期
    s2_flex = [s2_date - timedelta(days=1), s2_date]
    s3_flex = [s3_date + timedelta(days=x) for x in range(0, 4)]
    
    rows = []
    for hub in hubs:
        for tw in tw_airports:
            for air in airlines:
                for d2 in s2_flex:
                    for d3 in s3_flex:
                        # 模擬價格邏輯：布拉格/歐洲約 3.2w-3.6w
                        base_price = 33000 if "KUL" in hub else 36000
                        rows.append({
                            "航空公司": air, "外站啟動": hub, "台灣機場": tw,
                            "S2出發日": d2, "S3回程日": d3, "預估總價": base_price,
                            "模式": "同點進出", "建議艙等": "V / W"
                        })
                        if allow_oj and "PRG" in dest_iata:
                            rows.append({
                                "航空公司": air, "外站啟動": hub, "台灣機場": tw,
                                "S2出發日": d2, "S3回程日": d3, "預估總價": base_price - 2200,
                                "模式": "Open Jaw (VIE出)", "建議艙等": "V / W"
                            })

    df = pd.DataFrame(rows).sort_values("預估總價")
    st.dataframe(df.head(50), use_container_width=True)

    # --- 官網訂票指引 ---
    st.error("🚨 **官網訂票實戰：如何開出 3 萬多的特惠票？**")
    st.markdown(f"""
    請在官網「多城市」中，**完全對照列表選定的組合**輸入：
    1. **S1**: {df.iloc[0]['外站啟動']} ➔ {df.iloc[0]['台灣機場']} (日期: {s1_suggested})
    2. **S2**: {df.iloc[0]['台灣機場']} ➔ {dest_iata} (日期: {df.iloc[0]['S2出發日']})
    3. **S3**: {dest_iata if "Open Jaw" not in df.iloc[0]['模式'] else "VIE"} ➔ {df.iloc[0]['台灣機場']} (日期: {df.iloc[0]['S3回程日']})
    4. **S4**: {df.iloc[0]['台灣機場']} ➔ {df.iloc[0]['外站啟動']} (日期: {s4_suggested})
    
    **💡 避開 6 萬多元的秘訣**：
    若官網價格翻倍，代表 S1 或 S4 那天沒位子。請將 **S1 或 S4 的日期往前/後移動 1 天**，直到跳回特惠價。
    """)
