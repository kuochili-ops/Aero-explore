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
    "亞洲 (長程)": {
        "阿聯酋": ["杜拜 (DXB)"], "土耳其": ["伊斯坦堡 (IST)"], "印度": ["德里 (DEL)"]
    },
    "北美洲": {
        "美國": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "西雅圖 (SEA)"],
        "加拿大": ["溫哥華 (YVR)", "多倫多 (YYZ)"]
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

# 外站名稱對照表 (讓您理解外站碼對應的城市)
STATION_MAP = {
    "KUL": "吉隆坡 (馬來西亞)", "BKK": "曼谷 (泰國)", "HKG": "香港", 
    "PVG": "上海 (中國)", "PEK": "北京 (中國)", "CAN": "廣州 (中國)", 
    "NRT": "東京 (日本)", "KIX": "大阪 (日本)", "FUK": "福岡 (日本)", 
    "ICN": "首爾 (韓國)", "SIN": "新加坡"
}

# --- 3. 核心功能 ---
def search_flights(dep, arr, date_obj):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights", "departure_id": dep, "arrival_id": arr,
        "outbound_date": date_obj.strftime("%Y-%m-%d"), "currency": "TWD",
        "api_key": SERP_API_KEY, "type": "2" 
    }
    try:
        res = requests.get(url, params=params).json()
        return (res.get("best_flights", []) + res.get("other_flights", []))[:1]
    except: return []

# --- 4. 介面設計 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("全球版外站四段票掃描系統 (城市全名標示)")

with st.sidebar:
    st.header("🌍 全球航點選擇")
    continent = st.selectbox("1. 選擇大洲", list(GLOBAL_DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(GLOBAL_DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇城市", GLOBAL_DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    st.divider()
    st.header("📅 日期與策略")
    base_date = st.date_input("預估 S2 出發日期", value=datetime.today().date() + timedelta(days=61))
    accept_oj = st.toggle("自動比對 Open Jaw (同國鄰近城市)", value=True)
    tpe_hub = st.selectbox("台灣 Hub", ["TPE", "KHH", "TSA"])

# --- 5. 執行搜尋 ---
if st.button(f"🚀 啟動全球外站掃描 (+/- 15天範圍)"):
    date_range = [base_date + timedelta(days=x) for x in range(-15, 16, 5)] # 範例採樣
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
                
                res = search_flights(tpe_hub, target, d)
                if res:
                    f = res[0]
                    all_data.append({
                        "價格 (TWD)": f.get('price', 0),
                        "啟動城市 (外站)": city_name,
                        "出發日期 (S2)": d,
                        "航空公司": f['flights'][0]['airline'],
                        "模式": "同點" if target == dest_iata else f"Open Jaw ({target})",
                        "S1 啟動日": d - timedelta(days=60),
                        "S4 結尾日": d + timedelta(days=120)
                    })

    if all_results := all_data:
        df = pd.DataFrame(all_results)
        st.success(f"✅ 掃描完成！已列出全球各區域外站啟動價格。")
        st.dataframe(
            df.sort_values("價格 (TWD)"), 
            use_container_width=True,
            column_config={"價格 (TWD)": st.column_config.NumberColumn(format="TWD %d")}
        )
        
        st.subheader("📝 航空實戰要件註記 (依據 2026 指南)")
        best = df.sort_values("價格 (TWD)").iloc[0]
        st.info(f"""
        - **外站啟動**：您的航程由「{best['啟動城市 (外站)']}」開始，需於 {best['S1 啟動日']} 執行第一段。
        - **行李要件**：回程返抵 {tpe_hub} 時，務必確保地勤將行李標籤註記為只掛到台北。
        - **第四段處理**：完成第三段後，若不飛 S4 ({best['S4 結尾日']})，請參考 No Show 或改降其他台灣機場策略。
        """)
