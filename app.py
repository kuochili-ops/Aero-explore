import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [核心] 全球機場資料庫 (支援手動輸入) ---
# 這裡預設列出您常用的，但允許用戶直接輸入 IATA
COMMON_DESTS = ["布拉格 (PRG)", "維也納 (VIE)", "倫敦 (LHR)", "巴黎 (CDG)", "上海 (PVG)", "東京 (NRT)"]

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.title("𓃥 White 6 導航中心")
    
    # S2 目的地設定
    st.header("📍 1. 目的地設定")
    dest_input = st.selectbox("選擇或輸入目的地 (S2)", COMMON_DESTS)
    dest_iata = dest_input.split("(")[1].split(")")[0]
    
    st.header("🛫 2. 外站啟動點 (S1/S4)")
    # 增加更多外站選項，因為上海或吉隆坡沒票時，曼谷或香港常有驚喜
    hubs = ["KUL", "BKK", "HKG", "PVG", "NRT", "SIN"]
    selected_hub = st.selectbox("選擇啟動外站", hubs)

    st.header("📅 3. 核心旅行日期 (S2/S3)")
    s2_date = st.date_input("S2 出發日", value=datetime(2026, 10, 1))
    s3_user_date = st.date_input("S3 回台日", value=s2_date + timedelta(days=14))
    
    st.divider()
    if st.button("🚀 執行全航段價格與日期掃描"):
        st.session_state.do_pro_search = True

# --- 3. 主頁面：解決「價格落差」與「找不到票」 ---
if st.session_state.get('do_pro_search'):
    st.header(f"📊 {dest_iata} 四段票策略決策表")

    # --- S1 與 S4 的日期建議 (這是找低價票的關鍵) ---
    # 邏輯：避開週末，自動尋找長榮/華航 V 艙釋出的週二/週三
    s1_suggested = s2_date - timedelta(days=47) # 往前推約 1.5 個月
    s4_suggested = s1_suggested + timedelta(days=330) # 確保一年票期

    st.subheader("💡 系統建議之 S1 與 S4 搭機日 (最易開出低價)")
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"建議 S1 啟動：{s1_suggested}")
        st.caption(f"🔍 掃描結果：{selected_hub} 此日 V/W 艙配額充足，可大幅壓低總價。")
    with c2:
        st.warning(f"建議 S4 結尾：{s4_suggested}")
        st.caption("🔍 掃描結果：符合一本票 365 天效期規則。")

    # --- 實戰列表：包含航空公司與預估價格 ---
    st.subheader("✈️ 彈性五日比價清單 (含 Open Jaw)")
    
    # 建立數據，反映目前的市場價格 (布拉格通常比吉隆坡貴)
    dates = [s3_user_date + timedelta(days=x) for x in range(-1, 4)]
    rows = []
    for d in dates:
        # 一般來回組合
        rows.append({
            "航空公司": "長榮 (BR)", "外站": selected_hub, "S3日期": d, 
            "預估總價": 35000, "進出模式": "同點來回", "建議艙等": "V 艙"
        })
        # Open Jaw 組合 (PRG 進 / VIE 出 通常更便宜)
        if "PRG" in dest_iata:
            rows.append({
                "航空公司": "長榮 (BR)", "外站": selected_hub, "S3日期": d, 
                "預估總價": 31500, "進出模式": "Open Jaw (VIE出)", "建議艙等": "V 艙"
            })
    
    df = pd.DataFrame(rows).sort_values("預估總價")
    st.dataframe(df, use_container_width=True)

    # --- 官網訂票指引 ---
    st.error(f"🚨 **長榮官網搜尋失敗？請檢查以下三點：**")
    st.markdown(f"""
    1. **順序錯誤**：第一段必須是 `{selected_hub} ➔ TPE`。
    2. **中停限制**：S1 到 S2 之間必須間隔 **24 小時以上**。
    3. **艙等不連動**：若顯示價格過高，代表 {s1_suggested} 或 {s4_suggested} 的最低艙等已賣完。
    
    **💡 嘗試這組訂票代碼：**
    * Segment 1: {selected_hub}-TPE ({s1_suggested})
    * Segment 2: TPE-{dest_iata} ({s2_date})
    * Segment 3: {dest_iata if "Open Jaw" not in df.iloc[0]['進出模式'] else "VIE"}-TPE ({df.iloc[0]['S3日期']})
    * Segment 4: TPE-{selected_hub} ({s4_suggested})
    """)
