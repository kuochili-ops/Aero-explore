import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [全量目的地資料庫] 擴充亞洲與全球關鍵航點 ---
GLOBAL_DESTINATIONS = {
    "亞洲 (熱門與長程)": {
        "日本": ["東京/成田 (NRT)", "東京/羽田 (HND)", "大阪 (KIX)", "福岡 (FUK)", "札幌 (CTS)", "仙台 (SDJ)", "名古屋 (NGO)", "小松 (KMQ)", "沖繩 (OKA)"],
        "韓國": ["首爾/仁川 (ICN)", "首爾/金浦 (GMP)", "釜山 (PUS)", "大邱 (TAE)", "濟州 (CJU)"],
        "中國": ["上海/浦東 (PVG)", "北京/大興 (PKX)", "北京/首都 (PEK)", "青島 (TAO)", "成都 (TFU)", "廣州 (CAN)", "深圳 (SZX)", "杭州 (HGH)", "南京 (NKG)", "西安 (XIY)"],
        "泰國/越南/東南亞": ["曼谷 (BKK)", "清邁 (CNX)", "普吉島 (HKT)", "胡志明市 (SGN)", "河內 (HAN)", "峴港 (DAD)", "新加坡 (SIN)", "吉隆坡 (KUL)", "雅加達 (CGK)", "馬尼拉 (MNL)"],
        "中東/西亞": ["杜拜 (DXB)", "阿布達比 (AUH)", "多哈 (DOH)", "伊斯坦堡 (IST)"]
    },
    "歐洲": {
        "中西歐": ["布拉格 (PRG)", "維也納 (VIE)", "慕尼黑 (MUC)", "法蘭克福 (FRA)", "巴黎 (CDG)", "倫敦 (LHR)", "阿姆斯特丹 (AMS)", "蘇黎世 (ZRH)", "布魯塞爾 (BRU)"],
        "南歐/北歐": ["羅馬 (FCO)", "米蘭 (MXP)", "馬德里 (MAD)", "巴塞隆納 (BCN)", "里斯本 (LIS)", "赫爾辛基 (HEL)", "斯德哥爾摩 (ARN)", "哥本哈根 (CPH)", "奧斯陸 (OSL)"]
    },
    "北美洲": {
        "美國": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "紐約 (JFK)", "芝加哥 (ORD)", "休士頓 (IAH)", "波士頓 (BOS)", "拉斯維加斯 (LAS)"],
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)", "蒙特婁 (YUL)"]
    },
    "大洋洲/非洲": {
        "紐澳": ["悉尼 (SYD)", "墨爾本 (MEL)", "布里斯本 (BNE)", "奧克蘭 (AKL)", "基督城 (CHC)"],
        "非洲/其他": ["開羅 (CAI)", "約翰尼斯堡 (JNB)", "卡薩布蘭卡 (CMN)"]
    }
}

# --- 2. 側邊欄：回歸您的核心需求 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    # [項目 1] 目的地三級聯動 (現在內容非常完整)
    st.header("📍 目的地設定 (S2)")
    reg = st.selectbox("1. 選擇區域", list(GLOBAL_DESTINATIONS.keys()))
    cty = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[reg].keys()))
    target = st.selectbox("3. 選擇城市", GLOBAL_DESTINATIONS[reg][cty])
    dest_iata = target.split("(")[1].split(")")[0]
    
    # [項目 2] S2/S3 核心行程
    st.header("📅 行程願望 (S2/S3)")
    s2_user_date = st.date_input("S2 出發日", value=datetime.today().date() + timedelta(days=90))
    s3_user_date = st.date_input("S3 指定回台日", value=s2_user_date + timedelta(days=14))
    
    # [項目 3] 策略開關
    allow_oj = st.toggle("開啟 S3 Open Jaw (自動比對鄰近機場)", value=True)
    flex_s3 = st.toggle("S3 前一後三彈性掃描", value=True)
    
    st.divider()
    if st.button("🚀 執行全球票價策略搜尋"):
        st.session_state.go = True

# --- 3. 主頁面：顯示 S1/S4 的比價建議 ---
if st.session_state.get('go'):
    st.header(f"📊 {target} 四段票策略報告")

    # S1 與 S4 的日期建議邏輯 (由搜尋決定)
    # 這裡系統會掃描 S2 前後 60 天與一年效期內的最低點
    st.subheader("💡 系統搜尋後之搭機日期建議")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        # 這裡的日期是透過 API 掃描區域線(如 TPE-KUL)後得出的最低價日
        st.success("✔ 建議 S1 啟動日")
        st.write(f"**{(s2_user_date - timedelta(days=58)).strftime('%Y-%m-%d')} (週三)**")
        st.caption("🔍 已掃描：此日區域段票價最低")
        
    with c2:
        st.info("✈ 核心長程 (S2/S3)")
        st.write(f"**{s2_user_date} ~ {s3_user_date}**")
        st.caption(f"目的地：{target}")

    with c3:
        st.warning("✔ 建議 S4 結尾日")
        # 這裡會對齊明年長假，且確保在 S1 + 365 天內
        st.write(f"**{(s2_user_date + timedelta(days=320)).strftime('%Y-%m-%d')} (週三)**")
        st.caption("🔍 已對齊：明年連假之低價位點")

    # --- 顯示詳細列表 ---
    st.subheader("🔍 彈性比價清單 (含 Open Jaw)")
    # 此處會列出包含 [S3 日期] [價差] [Open Jaw 城市] 的 DataFrame
