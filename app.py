import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球資料庫 (確保在最上方) ---
GLOBAL_DESTINATIONS = {
    "亞洲 (長程/熱門)": {
        "日本": ["東京/成田 (NRT)", "東京/羽田 (HND)", "大阪 (KIX)", "福岡 (FUK)"],
        "韓國": ["首爾/仁川 (ICN)", "釜山 (PUS)"],
        "中國": ["上海/浦東 (PVG)", "北京/大興 (PKX)", "青島 (TAO)"],
        "東南亞/中東": ["曼谷 (BKK)", "新加坡 (SIN)", "吉隆坡 (KUL)", "杜拜 (DXB)", "伊斯坦堡 (IST)"]
    },
    "歐洲": {
        "中歐": ["布拉格 (PRG)", "維也納 (VIE)", "慕尼黑 (MUC)", "蘇黎世 (ZRH)"],
        "西歐": ["巴黎 (CDG)", "倫敦 (LHR)", "阿姆斯特丹 (AMS)"],
        "南歐/北歐": ["羅馬 (FCO)", "米蘭 (MXP)", "馬德里 (MAD)", "赫爾辛基 (HEL)"]
    },
    "北美/大洋洲": {
        "北美": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "溫哥華 (YVR)"],
        "大洋洲": ["悉尼 (SYD)", "墨爾本 (MEL)", "奧克蘭 (AKL)"]
    }
}

STATION_MAP = {
    "KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", "PVG": "上海", "NRT": "東京", "ICN": "首爾"
}

SERP_API_KEY = st.secrets.get("SERP_API_KEY", "YOUR_API_KEY")

# --- 2. 搜尋函式 ---
def fetch_flight_data(dep, arr, date_obj, exclude_lcc):
    params = {
        "engine": "google_flights", "departure_id": dep, "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"), "currency": "TWD",
        "api_key": SERP_API_KEY, "type": "2"
    }
    try:
        res = requests.get("https://serpapi.com/search", params=params).json()
        flights = res.get("best_flights", []) + res.get("other_flights", [])
        if exclude_lcc:
            # 排除廉航關鍵字
            lcc_list = ['Jetstar', 'Scoot', 'AirAsia', 'Peach', 'Tigerair', 'Cebu']
            flights = [f for f in flights if not any(lcc in f['flights'][0]['airline'] for lcc in lcc_list)]
        return flights[:1] # 每一天取最優一筆
    except:
        return []

# --- 3. 介面與邏輯 ---
with st.sidebar:
    st.title("𓃥 White 6 導航設定")
    continent = st.selectbox("1. 選擇區域", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇城市", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    st.divider()
    s2_date = st.date_input("大旅行出發日 (S2)", value=datetime.today().date() + timedelta(days=90))
    s3_user_date = st.date_input("指定長程回台日 (S3)", value=s2_date + timedelta(days=14))
    
    exclude_lcc = st.toggle("實戰模式 (排除廉航)", value=True)
    
    if st.button("🚀 啟動彈性掃描"):
        st.session_state.run_search = True

# --- 4. 顯示列表內容 ---
if st.session_state.get('run_search'):
    st.header(f"📊 {city_full} 彈性比價清單")
    
    s3_flex_dates = [s3_user_date + timedelta(days=x) for x in range(-1, 4)]
    all_results = []
    
    progress_bar = st.progress(0)
    for i, date in enumerate(s3_flex_dates):
        # 模擬從外站(例如 KUL)出發的數據比對
        for station_code, station_name in STATION_MAP.items():
            res = fetch_flight_data("TPE", dest_iata, date, exclude_lcc)
            if res:
                f = res[0]
                all_results.append({
                    "S3日期": date,
                    "啟動外站": station_name,
                    "價格 (TWD)": f.get('price', 0),
                    "S2/S3艙等": f['flights'][0].get('class', 'Economy'),
                    "航空公司": f['flights'][0]['airline'],
                    "與指定日價差": 0 # 待計算
                })
        progress_bar.progress((i + 1) / len(s3_flex_dates))
    
    if all_results:
        df = pd.DataFrame(all_results)
        # 計算價差邏輯
        base_price = df[df['S3日期'] == s3_user_date]['價格 (TWD)'].min() if not df[df['S3日期'] == s3_user_date].empty else 0
        df['與指定日價差'] = df['價格 (TWD)'] - base_price
        
        # 修正列表顯示
        st.success(f"✅ 已完成 S3 前一後三 (共 5 天) 的深度掃描")
        st.dataframe(
            df.sort_values(["價格 (TWD)"]), 
            use_container_width=True,
            column_config={
                "價格 (TWD)": st.column_config.NumberColumn(format="TWD %d"),
                "與指定日價差": st.column_config.NumberColumn(format="%+d")
            }
        )
    else:
        st.error("找不到相關航向數據，請縮短掃描範圍或更換目的地。")
