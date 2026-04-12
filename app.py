import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 擴大後的全球目的地資料庫 ---
GLOBAL_DESTINATIONS = {
    "歐洲": {
        "捷克": ["布拉格 (PRG)"], "奧地利": ["維也納 (VIE)"], "德國": ["慕尼黑 (MUC)", "法蘭克福 (FRA)"],
        "法國": ["巴黎 (CDG)"], "英國": ["倫敦 (LHR)"], "義大利": ["羅馬 (FCO)", "米蘭 (MXP)"], "荷蘭": ["阿姆斯特丹 (AMS)"]
    },
    "北美洲": {
        "美國": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "西雅圖 (SEA)"],
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)"]
    },
    "亞洲 (長程)": {
        "阿聯酋": ["杜拜 (DXB)"], "土耳其": ["伊斯坦堡 (IST)"], "印度": ["德里 (DEL)"]
    },
    "大洋洲": {
        "澳洲": ["悉尼 (SYD)", "墨爾本 (MEL)", "布里斯本 (BNE)"],
        "紐西蘭": ["奧克蘭 (AKL)", "基督城 (CHC)"]
    },
    "美洲 (中南美)": {
        "巴西": ["聖保羅 (GRU)"], "阿根廷": ["布宜諾斯艾利斯 (EZE)"], "秘魯": ["利馬 (LIM)"]
    },
    "非洲": {
        "埃及": ["開羅 (CAI)"], "南非": ["約翰尼斯堡 (JNB)"], "摩洛哥": ["卡薩布蘭卡 (CMN)"]
    }
}

STATION_MAP = {
    "KUL": "吉隆坡 (馬來西亞)", "BKK": "曼谷 (泰國)", "HKG": "香港", 
    "PVG": "上海 (中國)", "PEK": "北京 (中國)", "CAN": "廣州 (中國)", 
    "NRT": "東京 (日本)", "KIX": "大阪 (日本)", "FUK": "福岡 (日本)", 
    "ICN": "首爾 (韓國)", "SIN": "新加坡"
}

# 艙等代碼對照
CABIN_MAP = {
    "經濟艙 (Economy)": "economy",
    "豪華經濟艙 (Premium Economy)": "premium_economy",
    "商務艙 (Business)": "business",
    "頭等艙 (First)": "first"
}

# --- 3. 搜尋功能核心 ---
def search_flights(dep, arr, date_obj, cabin_class):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"),
        "currency": "TWD",
        "travel_class": cabin_class, # 加入艙等參數
        "api_key": SERP_API_KEY,
        "type": "2" 
    }
    try:
        res = requests.get(url, params=params).json()
        return (res.get("best_flights", []) + res.get("other_flights", []))[:1]
    except: return []

# --- 4. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("全球版外站四段票掃描：自定義長程艙等 (S2/S3)")

with st.sidebar:
    st.header("🌍 全球航點選擇")
    continent = st.selectbox("1. 選擇大洲", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇城市", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    st.divider()
    st.header("💺 長程段 (S2/S3) 艙等")
    # 讓使用者選擇 S2 (去程) 與 S3 (回程) 的希望艙等
    selected_cabin = st.selectbox("選擇主要艙等", list(CABIN_MAP.keys()), index=2) # 預設商務艙
    cabin_code = CABIN_MAP[selected_cabin]

    st.divider()
    st.header("📅 日期與策略")
    base_date = st.date_input("預估 S2 出發日期", value=datetime.today().date() + timedelta(days=61))
    accept_oj = st.toggle("自動比對 Open Jaw (鄰近城市)", value=True)
    tpe_hub = st.selectbox("台灣 Hub", ["TPE", "KHH", "TSA"])

# --- 5. 執行搜尋 ---
if st.button(f"🚀 啟動 {selected_cabin} 全球掃描 (+/- 15天)"):
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
                if d - timedelta(days=60) <= datetime.today().date(): continue
                
                # 搜尋關鍵 S2 段價格 (套用艙等)
                res = search_flights(tpe_hub, target, d, cabin_code)
                if res:
                    f = res[0]
                    all_data.append({
                        "價格 (TWD)": f.get('price', 0),
                        "啟動城市 (外站)": city_name,
                        "出發日期 (S2)": d,
                        "艙等": selected_cabin,
                        "航空公司": f['flights'][0]['airline'],
                        "模式": "同點進出" if target == dest_iata else f"Open Jaw ({target})",
                        "S1 啟動日": d - timedelta(days=60),
                        "S4 結尾日": d + timedelta(days=120)
                    })

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"✅ 掃描完成！已列出各外站之 {selected_cabin} 報價。")
        
        # 顯示可排序表格
        st.dataframe(
            df.sort_values("價格 (TWD)"), 
            use_container_width=True,
            column_config={
                "價格 (TWD)": st.column_config.NumberColumn(format="TWD %d"),
                "出發日期 (S2)": st.column_config.DateColumn(format="YYYY-MM-DD")
            }
        )
        
        # 依據您提供的網誌指南強化註記
        st.subheader("📝 四段票實戰要件註記")
        st.info(f"""
        - **艙等要件**：長程段 (S2/S3) 已鎖定為 **{selected_cabin}**。請注意，S1 與 S4 等區域航線可能會依航空公司機型配置自動降為經濟艙，請於開票時確認。
        - **外站啟動**：需於指定 S1 日期由外站啟動，否則整張票無效。
        - **行李處理**：返回 {tpe_hub} 時，務必告知櫃台行李只需掛到台北。
        - **操作建議**：如指南所述，完成 S3 之前絕對不要對 S4 進行任何系統取消，避免整張機票失效。
        """)
    else:
        st.error("此範圍內無數據。")

st.divider()
st.caption("𓃥 White 6 Studio | 2026 航空自動化比價 | 長程艙等自選系統")
