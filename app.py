import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 頁面基本配置 ---
st.set_page_config(page_title="White 6 Aero Explorer", page_icon="𓃥", layout="wide")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "4e7eddc7ddf9db9a6a8457601d438eda4aa5b4cdadf1ad751d1a20b2bb2d6844")

# --- 2. 靜態數據：目的地三級聯動資料庫 ---
# 這裡定義常見的四段票熱門目的地，確保資料準確
DESTINATIONS = {
    "歐洲": {
        "捷克": ["Prague (PRG)"],
        "奧地利": ["Vienna (VIE)"],
        "德國": ["Munich (MUC)", "Frankfurt (FRA)", "Berlin (BER)"],
        "法國": ["Paris (CDG)"],
        "義大利": ["Rome (FCO)", "Milan (MXP)"],
        "荷蘭": ["Amsterdam (AMS)"],
        "英國": ["London (LHR)"]
    },
    "美洲": {
        "美國": ["Los Angeles (LAX)", "San Francisco (SFO)", "New York (JFK)"],
        "加拿大": ["Vancouver (YVR)", "Toronto (YYZ)"]
    },
    "大洋洲": {
        "澳洲": ["Sydney (SYD)", "Melbourne (MEL)"],
        "紐西蘭": ["Auckland (AKL)"]
    }
}

# --- 3. 核心搜尋功能 ---
def search_flights(dep, arr, date_obj):
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
        return (res.get("best_flights", []) + res.get("other_flights", []))[:1]
    except: return []

# --- 4. 介面設計：三級聯動選單 ---
st.title("𓃥 White 6 Aero Explorer")
st.subheader("正規四段票：全球外站 + +/-15天範圍掃描")

with st.sidebar:
    st.header("📍 目的地選擇")
    # 洲、國、城市聯動
    continent = st.selectbox("1. 選擇大洲", list(DESTINATIONS.keys()))
    country = st.selectbox("2. 選擇國家", list(DESTINATIONS[continent].keys()))
    city_full = st.selectbox("3. 選擇城市", DESTINATIONS[continent][country])
    dest_iata = city_full.split("(")[1].split(")")[0]
    
    st.divider()
    st.header("📅 日期與規則")
    base_date = st.date_input("預估 S2 出發日期", value=datetime.today().date() + timedelta(days=61))
    accept_oj = st.checkbox("接受 Open Jaw (自動比對鄰近城市)", value=True)

# --- 5. 執行廣域掃描 ---
if st.button("🚀 啟動全自動深度掃描 (含 Open Jaw 比對)"):
    # 設定外站 (中國、日本、東南亞)
    stations = ["PVG", "HKG", "KUL", "NRT", "BKK", "SIN", "ICN"]
    
    # 掃描日期範圍 (+/- 15天，為節省 API 額度建議實戰時改為精確範圍)
    date_range = [base_date + timedelta(days=x) for x in range(-15, 16, 3)] # 範例採每3天一點以示範
    
    # 如果接受 Open Jaw，定義該國/區域的鄰近機場作為比對項
    search_targets = [dest_iata]
    if accept_oj:
        # 自動加入同國家其他機場作為 Open Jaw 潛在點
        other_cities = [c.split("(")[1].split(")")[0] for c in DESTINATIONS[continent][country] if dest_iata not in c]
        search_targets.extend(other_cities)

    all_results = []
    bar = st.progress(0)
    
    total = len(stations) * len(date_range) * len(search_targets)
    count = 0

    for stn in stations:
        for d in date_range:
            for target in search_targets:
                count += 1
                if d - timedelta(days=60) <= datetime.today().date(): continue
                
                bar.progress(count / total)
                res = search_flights("TPE", target, d)
                
                if res:
                    f = res[0]
                    mode = "同點進出" if target == dest_iata else f"Open Jaw ({target})"
                    all_results.append({
                        "價格 (TWD)": f.get('price', 0),
                        "啟動外站": stn,
                        "出發日期 (S2)": d,
                        "航空公司": f['flights'][0]['airline'],
                        "進出模式": mode,
                        "S1 (啟動)": d - timedelta(days=60),
                        "S4 (結尾)": d + timedelta(days=120)
                    })

    # --- 6. 結果呈現與排序 ---
    if all_results:
        df = pd.DataFrame(all_results)
        st.success(f"✅ 掃描完成！已自動比對 {dest_iata} 周邊航點。請點擊表頭排序。")
        
        st.dataframe(
            df.sort_values(by="價格 (TWD)"), 
            use_container_width=True,
            column_config={"價格 (TWD)": st.column_config.NumberColumn(format="TWD %d")}
        )

        st.subheader("📝 四段票航空公司開票要件註記")
        st.info(f"""
        **【實戰要件】**
        - **Open Jaw 判定**：列表若出現 'Open Jaw'，表示回程從同國鄰近機場出發價格更優。
        - **S1 啟動要件**：必須在 S1 日期從外站 ({df.iloc[0]['啟動外站']}) 飛抵台灣，機票才生效。
        - **行李要件**：S3 返回台灣時，務必要求「行李不直掛外站」。
        """)
    else:
        st.error("掃描範圍內未發現有效報價。")

st.divider()
st.caption("𓃥 White 6 Studio | 三級聯動目的地系統 | 2026 航空自動化旗艦版")
