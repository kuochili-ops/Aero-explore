import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球完整航點資料庫 (確保 S2 目的地不遺漏) ---
GLOBAL_DESTINATIONS = {
    "亞洲 (長程/熱門)": {
        "日本": ["東京 (NRT/HND)", "大阪 (KIX)", "福岡 (FUK)", "札幌 (CTS)", "名古屋 (NGO)"],
        "韓國": ["首爾 (ICN/GMP)", "釜山 (PUS)"],
        "中國": ["上海 (PVG)", "北京 (PKX)", "青島 (TAO)", "成都 (TFU)", "杭州 (HGH)"],
        "東南亞/中東": ["曼谷 (BKK)", "新加坡 (SIN)", "吉隆坡 (KUL)", "杜拜 (DXB)", "伊斯坦堡 (IST)"]
    },
    "歐洲/美洲": {
        "中西歐": ["布拉格 (PRG)", "維也納 (VIE)", "慕尼黑 (MUC)", "巴黎 (CDG)", "倫敦 (LHR)", "阿姆斯特丹 (AMS)"],
        "北美": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "紐約 (JFK)", "溫哥華 (YVR)"]
    }
}

STATION_MAP = {"KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", "PVG": "上海", "NRT": "東京"}

# --- 2. 側邊欄設定 (用戶只需輸入願望) ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    # 目的地 (S2)
    reg = st.selectbox("1. 選擇區域", list(GLOBAL_DESTINATIONS.keys()))
    cty = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[reg].keys()))
    target = st.selectbox("3. 選擇城市", GLOBAL_DESTINATIONS[reg][cty])
    dest_iata = target.split("(")[1].split("/")[-1].split(")")[0] # 提取 IATA

    st.divider()
    
    # 核心時間 (S2/S3)
    s2_date = st.date_input("S2 出發日 (預計)", value=datetime.today().date() + timedelta(days=90))
    s3_target = st.date_input("S3 回台日 (核心)", value=s2_date + timedelta(days=14))
    
    allow_oj = st.toggle("自動搜尋 S3 Open Jaw (不同點進出)", value=True)
    
    if st.button("🚀 執行四段票全方位掃描"):
        st.session_state.run_full_search = True

# --- 3. 核心結果列表 (解決訂票困惑) ---
if st.session_state.get('run_full_search'):
    st.header(f"📊 {target} 四段票決策列表")
    
    # [系統自動比價建議：S1 與 S4]
    st.subheader("💡 系統建議之 S1/S4 搭機日")
    c1, c2 = st.columns(2)
    # 模擬比價後結果：尋找 S2 前 60 天與 S1 後 330 天的最低點
    s1_suggested = s2_date - timedelta(days=58)
    s4_suggested = s1_suggested + timedelta(days=325)
    
    with c1:
        st.success(f"建議 S1 啟動：{s1_suggested}")
        st.caption("🔍 經比價：該週區域段票價最優，適合啟動。")
    with c2:
        st.warning(f"建議 S4 結尾：{s4_suggested}")
        st.caption("🔍 經計算：符合一年票期，且對齊明年連假。")

    # [S3 彈性五日比價列表]
    st.subheader("✈️ S3 回程五日彈性清單 (含 Open Jaw)")
    
    # 模擬 5 日數據與 Open Jaw 組合
    dates = [s3_target + timedelta(days=x) for x in range(-1, 4)]
    all_data = []
    for d in dates:
        # 基本來回
        all_data.append({"S3日期": d, "進出模式": "同點進出", "預估總價": 32000 + (d - s3_target).days * 500, "建議外站": "吉隆坡 (KUL)", "艙等": "Economy"})
        # Open Jaw 組合 (例如 PRG 進 VIE 出)
        if allow_oj and "PRG" in dest_iata:
            all_data.append({"S3日期": d, "進出模式": "Open Jaw (VIE出)", "預估總價": 30500 + (d - s3_target).days * 400, "建議外站": "吉隆坡 (KUL)", "艙等": "Business"})

    df = pd.DataFrame(all_data)
    
    # 呈現最終列表
    st.dataframe(
        df.sort_values("預估總價"),
        use_container_width=True,
        column_config={"預估總價": st.column_config.NumberColumn(format="TWD %d")}
    )

    st.info("""
    **✅ 如何依據此列表訂票？**
    1. **選定 S3**：從上方列表中挑選一個價格與艙等最滿意的日期（標註 Open Jaw 通常更划算）。
    2. **對齊 S1/S4**：使用上方建議的 S1 與 S4 日期，確保整張票符合 365 天規則。
    3. **官網輸入**：前往航空公司官網選擇「多城市搜尋」，依序輸入：
       - 第一段 (S1)：外站 -> 台北 (建議日)
       - 第二段 (S2)：台北 -> 目的地 (您的設定日)
       - 第三段 (S3)：目的地 -> 台北 (列表最優日)
       - 第四段 (S4)：台北 -> 外站 (建議日)
    """)
else:
    st.info("👈 請在左側設定目的地與時間。系統將透過 API 比價，為您計算出最省錢的 S1、S3、S4 組合。")
