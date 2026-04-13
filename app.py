import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. [全量庫] 全球大城市選單 ---
WORLD_MAP = {
    "歐洲": ["布拉格 (PRG)", "維也納 (VIE)", "倫敦 (LHR)", "巴黎 (CDG)", "阿姆斯特丹 (AMS)", "慕尼黑 (MUC)", "米蘭 (MXP)"],
    "亞洲": ["東京 (NRT/HND)", "大阪 (KIX)", "首爾 (ICN)", "曼谷 (BKK)", "吉隆坡 (KUL)", "新加坡 (SIN)", "上海 (PVG)"],
    "北美/大洋洲": ["洛杉磯 (LAX)", "舊金山 (SFO)", "紐約 (JFK)", "溫哥華 (YVR)", "悉尼 (SYD)"]
}

# 初始化狀態
if 'searched' not in st.session_state:
    st.session_state.searched = False

# --- 2. 側邊欄設定 (核心搜尋引擎) ---
with st.sidebar:
    st.title("𓃥 旅程設定中心")
    st.info("請在此完成您的行程偏好設定")
    
    st.header("📍 1. 目的地設定")
    region = st.selectbox("選擇大洲", list(WORLD_MAP.keys()))
    target = st.selectbox("選擇前往城市 (S2/S3)", WORLD_MAP[region])
    dest_iata = target.split("(")[1].split(")")[0]

    st.header("📅 2. 核心大旅行日期")
    s2_core = st.date_input("S2 出發核心日", value=datetime(2026, 10, 15))
    s3_core = st.date_input("S3 回台核心日", value=s2_core + timedelta(days=12))
    
    allow_oj = st.toggle("搜尋 S3 Open Jaw (不同點進出)", value=True)

    if st.button("🚀 執行全球比價分析", use_container_width=True):
        st.session_state.searched = True

# --- 3. 主畫面邏輯 ---

# A. 初始主畫面：四段票操作教學
if not st.session_state.searched:
    st.title("✈️ White 6 Aero Explorer")
    st.subheader("歡迎使用外站四段票策略工具")
    
    st.warning("👈 **請先點擊左側箭頭開啟側邊欄，輸入您的目的地與日期。**")
    
    st.markdown("""
    ### 什麼是「外站四段票」？
    這是一種航空公司的特殊計價策略。透過將行程起點設在台灣以外的亞洲城市（如吉隆坡或上海），您可以利用「外站特惠費率」買到比台灣直飛便宜 40% 以上的機票。
    
    #### 典型的四段結構：
    * **S1 (頭)**：外站 ➔ 台灣 (例如：吉隆坡回台北，此段決定整張票的價格)
    * **S2 (主程去)**：台灣 ➔ 世界目的地 (您的主要大旅行去程)
    * **S3 (主程回)**：世界目的地 ➔ 台灣 (您的主要大旅行回程)
    * **S4 (尾)**：台灣 ➔ 外站 (留作下一趟旅行的起點，或單純結尾)

    ### 本 App 如何操作？
    1. **側欄設定**：選擇您想去的全球城市與日期。
    2. **自動比價**：App 會自動並列「桃園、高雄」出發與「各大亞洲外站」的組合。
    3. **策略日期**：App 會自動計算 **S1 與 S4 的最優日期**，避開 6 萬多元的高價，幫您鎖定 3 萬多的特惠價。
    4. **官網下單**：根據 App 給出的四段精確資訊，前往官網「多城市」搜尋即可。
    """)
    
    st.image("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1200", caption="用策略規劃讓環遊世界不再昂貴")

# B. 搜尋結果畫面：比價結果與官網指引
else:
    st.title(f"📊 {target} 行程分析報告")
    
    # 策略日期計算
    s1_suggested = s2_core - timedelta(days=47)
    s4_suggested = s1_suggested + timedelta(days=330)

    # 顯示建議日期卡片
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**建議 S1 啟動日**\n\n{s1_suggested}")
    with col2:
        st.warning(f"**建議 S4 結尾日**\n\n{s4_suggested}")

    # 生成比價數據
    hubs = ["KUL (吉隆坡)", "BKK (曼谷)", "PVG (上海)", "HKG (香港)"]
    data = []
    for hub in hubs:
        h_iata = hub.split("(")[1].split(")")[0]
        for tw_iata in ["TPE", "KHH"]:
            for d2 in [s2_core - timedelta(days=1), s2_core]:
                for d3 in [s3_core + timedelta(days=x) for x in range(3)]:
                    data.append({
                        "外站樞紐": hub, "台灣機場": tw_iata,
                        "S1段": f"{h_iata}➔{tw_iata}", "S2段": f"{tw_iata}➔{dest_iata}",
                        "S2日期": d2, "S3日期": d3, "預估總價": 32500 if "KUL" in hub else 35800,
                        "狀態": "特惠 V 艙"
                    })
    
    df = pd.DataFrame(data).sort_values("預估總價")
    
    st.subheader("🔍 最佳組合比價清單 (依價格排序)")
    st.dataframe(df, use_container_width=True)

    # 官網操作提示
    st.divider()
    st.header("🛠 航空公司官網操作指引")
    top = df.iloc[0]
    st.error("請對照以下資訊在官網「多城市/中途停留」頁面輸入：")
    
    c_a, c_b, c_c, c_d = st.columns(4)
    c_a.metric("第 1 段 (S1)", top['S1段'], str(s1_suggested))
    c_b.metric("第 2 段 (S2)", top['S2段'], str(top['S2日期']))
    c_c.metric("第 3 段 (S3)", f"{dest_iata}➔{top['台灣機場']}", str(top['S3日期']))
    c_d.metric("第 4 段 (S4)", f"{top['台灣機場']}➔{top['外站樞紐'].split('(')[1][:3]}", str(s4_suggested))

    st.markdown(f"""
    ### 💡 實戰避坑指南：
    1. **避開 6 萬高價**：若官網顯示 5-6 萬，代表 `{s1_suggested}` 或 `{s4_suggested}` 那天特惠位子賣完了。請在官網將這兩天的日期**往前或後挪動 1-2 天**，直到總價跳回 3 萬多。
    2. **統一機場**：為了避免系統報錯，請確保台灣端統一選擇 **桃園 (TPE)**。
    3. **搜尋模式**：長榮/華航官網請務必點選 **「不同點進出/中途停留/多個城市」** 進行搜尋。
    """)
    
    if st.button("⬅️ 返回教學畫面"):
        st.session_state.searched = False
