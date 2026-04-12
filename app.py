import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 全球目的地資料庫 (三級聯動) ---
GLOBAL_DESTINATIONS = {
    "歐洲": {
        "捷克": ["布拉格 (PRG)"], "奧地利": ["維也納 (VIE)"], "德國": ["慕尼黑 (MUC)", "法蘭克福 (FRA)"],
        "法國": ["巴黎 (CDG)"], "英國": ["倫敦 (LHR)"], "義大利": ["羅馬 (FCO)", "米蘭 (MXP)"]
    },
    "北美洲": {
        "美國": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)"],
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)"]
    },
    "大洋洲": {
        "澳洲": ["悉尼 (SYD)", "墨爾本 (MEL)"], "紐西蘭": ["奧克蘭 (AKL)"]
    },
    "亞洲/非洲/美洲": {
        "中國": ["上海 (PVG)", "北京 (PEK)"], "日本": ["東京 (NRT)", "大阪 (KIX)"],
        "其他": ["杜拜 (DXB)", "開羅 (CAI)", "聖保羅 (GRU)"]
    }
}

STATION_MAP = {
    "KUL": "吉隆坡 (馬來西亞)", "BKK": "曼谷 (泰國)", "HKG": "香港", 
    "PVG": "上海 (中國)", "NRT": "東京 (日本)", "ICN": "首爾 (韓國)", "SIN": "新加坡"
}

# --- 3. 核心搜尋引擎 (不設艙等過濾，確保有結果) ---
def search_flights_unfiltered(dep, arr, date_obj):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "api_key": SERP_API_KEY,
        "type": "2" 
    }
    try:
        res = requests.get(url, params=params).json()
        # 抓取搜尋結果，並保留其中的艙等資訊 (Travel Class)
        flights = res.get("best_flights", []) + res.get("other_flights", [])
        return flights[:1]
    except: return []

# --- 4. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("四段票全球自動掃描系統 (自動辨識艙等模式)")

with st.sidebar:
    st.header("📍 目的地設定")
    continent = st.selectbox("1. 選擇大洲", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇城市備選", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    st.divider()
    st.header("📅 日期與規則")
    base_date = st.date_input("預估 S2 出發日期", value=datetime.today().date() + timedelta(days=61))
    accept_oj = st.toggle("自動比對 Open Jaw", value=True)
    tpe_hub = st.selectbox("台灣 Hub", ["TPE", "KHH", "TSA"])

# --- 5. 執行廣域掃描 ---
if st.button("🚀 啟動全方位掃描 (抓取所有可用數據)"):
    # 設定日期掃描點 (前後15天，採樣增加成功率)
    date_range = [base_date + timedelta(days=x) for x in range(-15, 16, 5)] 
    search_targets = [dest_iata]
    if accept_oj:
        search_targets.extend([c.split("(")[1].split(")")[0] for c in GLOBAL_DESTINATIONS[continent][country] if dest_iata not in c])

    all_data = []
    bar = st.progress(0)
    total = len(STATION_MAP) * len(date_range) * len(search_targets)
    count = 0

    for code, city_name in STATION_MAP.items():
        for d in date_range:
            for target in search_targets:
                count += 1
                bar.progress(count / total)
                
                # 執行搜尋 (不帶艙等參數，由 Google 決定最優解)
                res = search_flights_unfiltered(tpe_hub, target, d)
                
                if res:
                    f = res[0]
                    # 從原始數據中提取「艙等」
                    cabin_info = f['flights'][0].get('class', 'Economy')
                    
                    all_data.append({
                        "價格 (TWD)": f.get('price', 0),
                        "啟動城市 (外站)": city_name,
                        "出發日期 (S2)": d,
                        "S2/S3 實得艙等": cabin_info, # 這是您要求的註記
                        "航空公司": f['flights'][0]['airline'],
                        "進出模式": "同點" if target == dest_iata else f"Open Jaw ({target})",
                        "S1 啟動日": d - timedelta(days=60),
                        "S4 結尾日": d + timedelta(days=120)
                    })

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"✅ 掃描完成！已列出所有可用航段與對應艙等。")
        
        # 顯示可排序表格
        st.dataframe(
            df.sort_values("價格 (TWD)"), 
            use_container_width=True,
            column_config={
                "價格 (TWD)": st.column_config.NumberColumn(format="TWD %d"),
                "出發日期 (S2)": st.column_config.DateColumn(format="YYYY-MM-DD")
            }
        )
        
        # 實戰註記
        st.subheader("📝 四段票航空公司開票要件註記")
        st.info(f"""
        - **艙等註記**：表格中已列出該價格對應的 **S2/S3 實際艙等**。若發現商務艙價格異常低，即為外站票的最佳進場點。
        - **行李處理**：不論艙等，返台時請務必要求行李「只掛到台北」。
        - **S4 策略**：根據網誌指南，完成第三段後再處理第四段 (No Show 或改降) 最為安全。
        """)
    else:
        st.error("目前所有外站與日期組合均無回傳數據，請嘗試更換目的地或將預估日期往後調整。")

st.divider()
st.caption("𓃥 White 6 Studio | 2026 全球掃描版 | 自動辨識艙等功能")
