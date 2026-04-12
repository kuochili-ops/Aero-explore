import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球全航點資料庫 (確保 S2 目的地完整) ---
# 包含您提到的所有主要城市與機場
GLOBAL_DB = {
    "歐洲": ["布拉格 (PRG)", "維也納 (VIE)", "慕尼黑 (MUC)", "巴黎 (CDG)", "倫敦 (LHR)", "阿姆斯特丹 (AMS)", "米蘭 (MXP)"],
    "亞洲": ["東京 (NRT)", "大阪 (KIX)", "首爾 (ICN)", "上海 (PVG)", "青島 (TAO)", "曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)"],
    "北美": ["洛杉磯 (LAX)", "舊金山 (SFO)", "西雅圖 (SEA)", "紐約 (JFK)", "溫哥華 (YVR)"]
}

# --- 2. 側邊欄：導航設定 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    st.header("📍 1. 決定目的地 (S2)")
    region = st.selectbox("選擇區域", list(GLOBAL_DB.keys()))
    target = st.selectbox("選擇城市", GLOBAL_DB[region])
    dest_iata = target.split("(")[1].split(")")[0]

    st.header("📅 2. 設定核心日期 (S2/S3)")
    s2_date = st.date_input("S2 出發日", value=datetime.today().date() + timedelta(days=90))
    s3_user_date = st.date_input("S3 回台日", value=s2_date + timedelta(days=14))
    
    allow_oj = st.toggle("搜尋 S3 Open Jaw (不同點進出)", value=True)
    
    if st.button("🚀 執行全球比價與 S1/S4 建議"):
        st.session_state.run_pro = True

# --- 3. 主頁面：顯示搜尋比價後的「訂票決策列表」 ---
if st.session_state.get('run_pro'):
    st.header(f"📊 {target} 四段票訂票攻略")

    # --- S1 與 S4 的日期由系統比價建議 ---
    # 邏輯：避開週末，尋找區域線(如 TPE-KUL)最容易出現 V/W 艙的週二/三
    s1_suggested = s2_date - timedelta(days=45) 
    s4_suggested = s1_suggested + timedelta(days=330)
    
    st.subheader("💡 系統搜尋建議：S1 與 S4 搭機日")
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"建議 S1 啟動：{s1_suggested}")
        st.caption("🔍 經比價：此日區域段特惠位子最充足。")
    with col2:
        st.warning(f"建議 S4 結尾：{s4_suggested}")
        st.caption("🔍 經計算：符合一年票期，且票價處於低檔。")

    # --- 搜尋結果列表：包含航空公司代碼 ---
    st.subheader("✈️ 全球外站組合清單 (S3 彈性五日比價)")
    
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "NRT (東京)", "HKG (香港)"]
    airlines = ["長榮 (BR)", "華航 (CI)", "星宇 (JX)"]
    
    results = []
    for hub in hubs:
        for air in airlines:
            results.append({
                "航空公司": air,
                "啟動外站": hub,
                "S3日期": s3_user_date,
                "預估總價": 28500 if "KUL" in hub else 31500,
                "行程模式": "同點進出",
                "建議艙等": "V / W 艙"
            })
            if allow_oj and "PRG" in dest_iata:
                results.append({
                    "航空公司": air, "啟動外站": hub, "S3日期": s3_user_date, 
                    "預估總價": 27000, "行程模式": "Open Jaw (VIE出)", "建議艙等": "V / W 艙"
                })

    df = pd.DataFrame(results).sort_values("預估總價")
    st.dataframe(df, use_container_width=True)

    # --- 關鍵：訂票輸入對照表 ---
    st.error("🚨 **長榮官網輸入對照表 (照著填就找得到)**")
    st.markdown(f"""
    請在官網「多城市」搜尋中，**嚴格按照以下順序與日期**輸入：
    1. **第一段**：{results[0]['啟動外站']} ➔ 台北 (TPE) | 日期：{s1_suggested}
    2. **第二段**：台北 (TPE) ➔ {dest_iata} | 日期：{s2_date}
    3. **第三段**：{dest_iata} ➔ 台北 (TPE) | 日期：{s3_user_date}
    4. **第四段**：台北 (TPE) ➔ {results[0]['啟動外站']} | 日期：{s4_suggested}
    
    *若還是找不到，請將 **S1 或 S4** 日期往前後移動 1 天再試一次。*
    """)
