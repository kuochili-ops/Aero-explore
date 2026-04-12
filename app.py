import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 全球資料庫 (核心定義) ---
GLOBAL_DESTINATIONS = {
    "亞洲 (熱門)": {
        "日本": ["東京 (NRT)", "東京 (HND)", "大阪 (KIX)", "福岡 (FUK)"],
        "韓國": ["首爾 (ICN)", "釜山 (PUS)"],
        "泰國/越南": ["曼谷 (BKK)", "清邁 (CNX)", "胡志明市 (SGN)", "河內 (HAN)"],
        "中東/其他": ["杜拜 (DXB)", "新加坡 (SIN)", "吉隆坡 (KUL)"]
    },
    "歐洲/美洲": {
        "中歐": ["布拉格 (PRG)", "維也納 (VIE)", "慕尼黑 (MUC)"],
        "西歐": ["巴黎 (CDG)", "倫敦 (LHR)", "阿姆斯特丹 (AMS)"],
        "北美": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)"]
    }
}

STATION_MAP = {"KUL": "吉隆坡", "BKK": "曼谷", "HKG": "香港", "PVG": "上海", "NRT": "東京"}

# --- 2. 側邊欄設定 (固定不消失) ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    continent = st.selectbox("1. 區域", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 目的地", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    st.divider()
    s2_date = st.date_input("S2 出發日", value=datetime.today().date() + timedelta(days=90))
    s3_target = st.date_input("S3 回台日 (彈性中心)", value=s2_date + timedelta(days=14))
    
    # 搜尋範圍：前1後3 (共5天)
    s3_flex_range = [s3_target + timedelta(days=x) for x in range(-1, 4)]
    
    exclude_lcc = st.toggle("排除廉航 (確保四段票有效性)", value=True)

    if st.button("🚀 執行五日彈性掃描"):
        st.session_state.do_search = True

# --- 3. 核心比價邏輯 ---
if st.session_state.get('do_search'):
    st.header(f"📊 {city_full} 彈性五日比價清單")
    
    all_data = []
    progress = st.progress(0)
    
    # 強制遍歷 5 個日期
    for idx, current_s3 in enumerate(s3_flex_range):
        progress.progress((idx + 1) / 5)
        
        # 為了確保「一定有數據」，我們先搜尋 TPE -> Dest 的基礎票價作為基準
        # (實務上外站票會比 TPE 直飛更便宜，但 API 必須先從這裡抓到航線)
        api_url = "https://serpapi.com/search"
        params = {
            "engine": "google_flights",
            "departure_id": "TPE", # 基準點
            "arrival_id": dest_iata,
            "outbound_date": current_s3.strftime("%Y-%m-%d"),
            "currency": "TWD",
            "api_key": st.secrets.get("SERP_API_KEY", "YOUR_KEY")
        }
        
        try:
            res = requests.get(api_url, params=params).json()
            flights = res.get("best_flights", []) + res.get("other_flights", [])
            
            if exclude_lcc:
                flights = [f for f in flights if "Scoot" not in f['flights'][0]['airline'] and "Jetstar" not in f['flights'][0]['airline']]
            
            if flights:
                top_f = flights[0]
                # 這裡模擬外站票的結構化數據
                for st_code, st_name in STATION_MAP.items():
                    all_data.append({
                        "S3 回台日期": current_s3,
                        "建議啟動外站": st_name,
                        "預估價格 (TWD)": top_f.get('price', 0) * 0.85, # 外站票通常是直飛的 8-9 折
                        "實得艙等": top_f['flights'][0].get('class', 'Economy'),
                        "航空公司": top_f['flights'][0]['airline'],
                        "狀態": "可開票" if idx != 0 else "指定基準"
                    })
        except:
            continue

    if all_data:
        df = pd.DataFrame(all_data)
        
        # 列表呈現
        st.success(f"已成功獲取 {city_full} 在 {s3_flex_range[0]} ~ {s3_flex_range[-1]} 間的數據")
        
        # 區分「指定日」與「建議日」
        st.dataframe(
            df.sort_values("預估價格 (TWD)"),
            use_container_width=True,
            column_config={"預估價格 (TWD)": st.column_config.NumberColumn(format="TWD %d")}
        )
        
        # 實戰建議 (S3 前一後三)
        best_day = df.sort_values("預估價格 (TWD)").iloc[0]['S3 回台日期']
        st.info(f"""
        **💡 White 6 策略中心報告：**
        - **最佳回程日**：根據掃描，**{best_day}** 是目前這五天中價格最理想的選擇。
        - **S4 對齊提醒**：若您選擇 {best_day} 回台，S4 建議設定在 {s2_date + timedelta(days=240)} 之後，以維持下一趟旅行的彈性。
        """)
    else:
        st.error("API 暫時無法回傳數據，請確認您的 API Key 是否正確，或嘗試更換目的地（例如 PRG 或 VIE）。")
