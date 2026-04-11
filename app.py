import streamlit as st
import requests

# 1. 配置 Secrets
RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"] # 在 Streamlit Cloud 的 Secrets 中設定
RAPID_API_HOST = "skyscanner-flights-travel-api.p.rapidapi.com"

def search_flight_leg(origin, destination, date):
    url = f"https://{RAPID_API_HOST}/v1/flights/search-onedate" # 範例 Endpoint
    querystring = {
        "fromEntityId": origin,
        "toEntityId": destination,
        "departDate": date,
        "currency": "TWD",
        "locale": "zh-TW"
    }
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

# 2. White 6 UI 整合
st.title("𓃥 White 6 Aero Explorer")

# 假設搜尋第二段：台北 -> 布拉格
if st.button("執行四段票比價"):
    # 在這裡循環執行四次搜尋 (或一次 Multi-city，視 API 版本而定)
    leg2_results = search_flight_leg("TPE", "PRG", "2026-06-10")
    
    if leg2_results:
        st.success("成功獲取布拉格即時票價！")
        # 這裡解析 JSON 並顯示價格
        # st.write(leg2_results)
