from duffel_api import Duffel
from datetime import datetime, timedelta

# 初始化 Duffel 客戶端
# 建議將 token 放入 Streamlit 的 secrets.toml 中
client = Duffel(access_token="你的_duffel_test_token")

def search_white6_four_segments(outstation, destination, s2_date_str):
    """
    outstation: 外站 (如 'HKG')
    destination: 主目的地 (如 'PRG')
    s2_date_str: 第二段出發日期 'YYYY-MM-DD'
    """
    
    # 邏輯計算日期
    s2_date = datetime.strptime(s2_date_str, '%Y-%m-%d')
    s1_date = (s2_date - timedelta(days=60)).strftime('%Y-%m-%d') # 提前兩個月
    s3_date = (s2_date + timedelta(days=10)).strftime('%Y-%m-%d') # 玩 10 天
    s4_date = (s2_date + timedelta(days=120)).strftime('%Y-%m-%d') # 四個月後飛最後一段

    # 構建多段行程 (Multi-segment slices)
    slices = [
        {"origin": outstation, "destination": "TPE", "departure_date": s1_date},
        {"origin": "TPE", "destination": destination, "departure_date": s2_date_str},
        {"origin": destination, "destination": "TPE", "departure_date": s3_date},
        {"origin": "TPE", "destination": outstation, "departure_date": s4_date}
    ]

    try:
        # 1. 建立搜尋請求
        search_request = client.offer_requests.create().volumes([
            {"slices": slices, "passengers": [{"type": "adult"}]}
        ]).execute()
        
        # 2. 獲取回傳的所有方案
        offers = search_request.offers
        
        return offers
    except Exception as e:
        print(f"搜尋出錯: {e}")
        return []

# 測試調用
# results = search_white6_four_segments("HKG", "PRG", "2026-06-10")
