# redeploy test

import streamlit as st
import pandas as pd
import plotly.express as px
import ssl
import datetime

# 忽略 SSL 憑證驗證錯誤
ssl._create_default_https_context = ssl._create_unverified_context

# ===== 頁面設定 =====
st.set_page_config(page_title="醫工室儀表板", layout="wide")

# ===== Session 狀態（頁面切換） =====
if "page" not in st.session_state:
    st.session_state.page = "main"

# ===== 自訂按鈕樣式 =====
def custom_button(text, color, hover, text_color, width, height, font_size, radius, key):
    """
    建立自訂樣式的按鈕。
    """
    st.markdown(
        f"""
        <style>
        div[data-testid="stButton"][key="{key}"] button {{
            background-color: {color};
            color: {text_color};
            font-size: {font_size};
            border-radius: {radius};
            width: {width};
            height: {height};
            font-weight: 600;
            transition: 0.3s;
            margin: 6px;
        }}
        div[data-testid="stButton"][key="{key}"] button:hover {{
            background-color: {hover};
            transform: scale(1.05);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ===== 按鈕樣式設定 =====
BUTTON_STYLE = {
    "repair": {
        "text": "🛠️ 維修保養",
        "color": "#4a90e2",
        "hover": "#357ABD",
        "text_color": "white",
        "width": "220px",
        "height": "60px",
        "font_size": "18px",
        "radius": "12px",
    },
    "contract": {
        "text": "📄 合約資訊",
        "color": "#2e7d32",
        "hover": "#256628",
        "text_color": "white",
        "width": "220px",
        "height": "60px",
        "font_size": "18px",
        "radius": "12px",
    },
    "equipment": {
        "text": "⚙️ 設備資訊",
        "color": "#9c27b0",
        "hover": "#7b1fa2",
        "text_color": "white",
        "width": "220px",
        "height": "60px",
        "font_size": "18px",
        "radius": "12px",
    },
    "Parts": {
        "text": "⚙️ 庫房管理",
        "color": "#9c27b0",
        "hover": "#7b1fa2",
        "text_color": "white",
        "width": "220px",
        "height": "60px",
        "font_size": "18px",
        "radius": "12px",
    },
}

維修保養資訊顏色 = "#8FA9FF"

# ===== 自訂 CSS =====
st.markdown("""
    <style>
        body { background-color: #0e1117; color: #e8e8e8; }
        h1, h2, h3 { color: #d0d8ff; text-align: center; }

        .kpi-card {
            background-color: #1c1f26;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.25);
            border: 1px solid #333;
            text-align: center;
            transition: transform 0.2s ease;
            margin-bottom: 12px;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.35);
        }
        .kpi-label {
            color: #ccc;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 26px;
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

# ===== KPI 顯示函數 =====
def colored_metric(label, value, color):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def rate_color(rate):
    if rate < 0.8:
        return "#FF6347"
    elif rate < 0.9:
        return "#FFD700"
    else:
        return "#32CD32"

# ===== Google Sheet 設定 =====
SHEET_ID = "1-_9tP9j7yDdbcgQHSCycxDzaPCOHYSrCoQ2mZjPLI3I"
SHEET_GIDS = {
    "各同仁維修保養": "0",
    #"各同仁維修分析": "484715663",
    "維修": "221547120",
    "合約清單": "1945804832",
    "合約內容": "1994309175",
    "未完工": "662979561",
    "未完成保養": "1848891402",
    "到期合約":"602739837",
    "設備清單":"1444544478"
}
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid="

@st.cache_data(ttl=600)
def load_data_from_gsheets():
    def safe_read(name, gid):
        url = BASE_URL + gid
        try:
            return pd.read_csv(url)
        except Exception as e:
            st.error(f"❌ 無法讀取【{name}】(GID:{gid})，錯誤：{e}")
            return pd.DataFrame()
    return (
        safe_read("各同仁維修保養", SHEET_GIDS["各同仁維修保養"]),
        #safe_read("各同仁維修分析", SHEET_GIDS["各同仁維修分析"]),
        safe_read("維修", SHEET_GIDS["維修"]),
        safe_read("合約清單", SHEET_GIDS["合約清單"]),
        safe_read("合約內容", SHEET_GIDS["合約內容"]),
        safe_read("未完工", SHEET_GIDS["未完工"]),
        safe_read("未完成保養", SHEET_GIDS["未完成保養"]),
        safe_read("到期合約", SHEET_GIDS["到期合約"]),
        safe_read("設備清單", SHEET_GIDS["設備清單"])
    )

# ===== 輔助函數：用於設定設備類別 Session State =====
def set_selected_device(device_name):
    """將選中的設備名稱存入 Session State。"""
    st.session_state.selected_device = device_name


# ===== 主頁面 =====
if st.session_state.page == "main":
    各同仁維修保養, 維修, 合約清單, 合約內容, 未完工, 未完成保養, 到期合約, 設備清單 = load_data_from_gsheets()

    st.markdown("<h1>🏥 醫工室儀表板</h1>", unsafe_allow_html=True)

    # ===== 三個按鈕列排列 =====
    col1, col2, col3,col4 = st.columns(4, gap="large")

    with col1:
        custom_button(**BUTTON_STYLE["repair"], key="repair_btn")
        if st.button(BUTTON_STYLE["repair"]["text"], key="repair_click"):
            st.session_state.page = "repair"
            st.rerun()

    with col2:
        custom_button(**BUTTON_STYLE["contract"], key="contract_btn")
        if st.button(BUTTON_STYLE["contract"]["text"], key="contract_click"):
            st.session_state.page = "contract"
            st.rerun()

    with col3:
        custom_button(**BUTTON_STYLE["equipment"], key="equipment_btn")
        if st.button(BUTTON_STYLE["equipment"]["text"], key="equipment_click"):
            st.session_state.page = "equipment"
            st.rerun()
    with col4:
        custom_button(**BUTTON_STYLE["Parts"], key="Parts_btn")
        if st.button(BUTTON_STYLE["Parts"]["text"], key="Parts_click"):
            st.session_state.page = "Parts"
            st.rerun()

    st.markdown("---")

    # ===== KPI =====
    if not 各同仁維修保養.empty:
        維修總件數 = 各同仁維修保養["維修總件數"].sum()
        已完成維修件數 = 各同仁維修保養["已完成維修件數"].sum()
        三十天內完成件數 = 各同仁維修保養["三十天內完成件數"].sum()
        未完成維修件數 = 維修總件數 - 已完成維修件數
        維修完成率 = 三十天內完成件數 / 維修總件數 if 維修總件數 else 0

        保養總件數 = 各同仁維修保養["保養總件數"].sum()
        已完成保養件數 = 各同仁維修保養["已完成保養件數"].sum()
        未保養件數 = 保養總件數 - 已完成保養件數
        保養完成率 = 已完成保養件數 / 保養總件數 if 保養總件數 else 0

        五日內內修完成件數 = 各同仁維修保養.get("五日內內修完成件數", pd.Series([0])).sum()
        自修件數 = 各同仁維修保養.get("自修件數", pd.Series([0])).sum()
        五日完修率 = 五日內內修完成件數 / 自修件數 if 自修件數 else 0
    else:
        維修總件數 = 保養總件數 = 已完成維修件數 = 已完成保養件數 = 未完成維修件數 = 未保養件數 = 五日完修率 = 0
    
    # ===== 合約統計 =====
    fig_contract = None
    合約總筆數 = 合約總台數 = 0
    if not 合約清單.empty and not 合約內容.empty:
        if "ContractNo" in 合約清單.columns and "ContractNo" in 合約內容.columns:
#            合約清單["ContractNo"] = 合約清單["ContractNo"].astype(str).str.strip()
#            合約內容["ContractNo"] = 合約內容["ContractNo"].astype(str).str.strip()
            合約交集 = sorted( set(合約內容["ContractNo"].astype(str).str.strip()) & set(合約清單["ContractNo"].astype(str).str.strip()))
            合約總筆數 = len(合約交集)

        if not 合約內容.empty and "CLASS" in 合約內容.columns and "Date_T" in 合約內容.columns:
            未結束合約 = 合約內容[合約內容["Date_T"].isna()]
            class_count = 未結束合約["CLASS"].value_counts().reset_index()
            class_count.columns = ["合約類型", "台數"]
            if not class_count.empty:
                fig_contract = px.bar(
                    class_count, x="合約類型", y="台數", text="台數",
                    title="📊 合約類型分佈圖", color="合約類型"
                )
                fig_contract.update_traces(textposition="outside")
                fig_contract.update_layout(title_x=0.5, plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                合約總台數 = class_count["台數"].sum()
            else:
                 class_count = pd.DataFrame({'合約類型': [], '台數': []}) # 確保 class_count 存在

    col1, col2, col3= st.columns([0.4, 0.4, 0.2])
    with col1:
        c1, c2 = st.columns(2)
        with c1: colored_metric("維修總件數", f"{維修總件數:,}", "#00BFFF")
        with c2: colored_metric("未完成維修件數", f"{未完成維修件數:,}", "#EE5959")
        c3, c4 = st.columns(2)
        with c3: colored_metric("維修完成率", f"{維修完成率*100:.2f}%", rate_color(維修完成率))
        with c4: colored_metric("五日完修率", f"{五日完修率*100:.2f}%", rate_color(五日完修率))
    with col2:
        c1, c2 = st.columns(2)
        with c1: colored_metric("保養總件數", f"{保養總件數:,}", "#1E90FF")
        with c2: colored_metric("未保養件數", f"{未保養件數:,}", "#EE5959")
        c3, c4 = st.columns(2)
        with c3: colored_metric("保養完成率", f"{保養完成率*100:.2f}%", rate_color(保養完成率))
        with c4: st.empty()
    with col3:
        # 由於 class_count 可能在上面未定義，這裡加個防護
        if 'class_count' in locals() and not class_count.empty:
            colored_metric("合約總筆數", f"{len(合約交集):,}", "#BA55D3")
            colored_metric("合約內容筆數", f"{class_count['台數'].sum():,}", "#00CED1")
        else:
            colored_metric("合約總筆數", f"{合約總筆數:,}", "#BA55D3")
            colored_metric("合約內容筆數", f"{合約總台數:,}", "#00CED1")

    st.markdown("---")

    # ===== 圖表展示區 =====
    col10, col11, col12 = st.columns(3)
    fig_units = fig_reasons  = None

    if not 維修.empty:
        try:
            if "成本中心名稱" in 維修.columns:
                top_units = (
                    維修["成本中心名稱"]
                    .value_counts()
                    .head(10)
                    .rename_axis("成本中心名稱")
                    .reset_index(name="件數")
                )
                fig_units = px.pie(top_units, names="成本中心名稱", values="件數",
                                title="維修件數前10名單位", hole=0.4)
                fig_units.update_layout(title_x=0.5, plot_bgcolor="rgba(0,0,0,0)")

            if "故障原因" in 維修.columns:
                top_reasons = (
                    維修["故障原因"]
                    .value_counts()
                    .head(10)
                    .rename_axis("故障原因")
                    .reset_index(name="件數")
                )
                fig_reasons = px.pie(top_reasons, names="故障原因", values="件數",
                                    title="故障原因前10名", hole=0.4)
                fig_reasons.update_layout(title_x=0.5, plot_bgcolor="rgba(0,0,0,0)")
        except Exception as e:
            st.error(f"❌ 圖表產生錯誤：{e}")

    if fig_units is not None: col10.plotly_chart(fig_units, use_container_width=True)
    if fig_reasons is not None: col11.plotly_chart(fig_reasons, use_container_width=True)
    if fig_contract is not None: col12.plotly_chart(fig_contract, use_container_width=True)


# ===== 第二頁：維修保養資訊 =====
if st.session_state.page == "repair":
    # 🔹 左上角返回儀表板按鈕
    col_top_left, col_top_right = st.columns([1, 6])
    with col_top_left:
        if st.button("⬅️ 返回儀表板"):
            st.session_state.page = "main"
            st.rerun()
    # 變更處 4：呼叫新的函數
    各同仁維修保養,維修, 合約清單, 合約內容, 未完工, 未完成保養, 到期合約, 設備清單 = load_data_from_gsheets()

    st.markdown(f"<h2 style='text-align:center; color:{維修保養資訊顏色};'>🧰 維修保養資訊</h2>", unsafe_allow_html=True)

    # 預設年月為當前年月 (格式: 202510 → 11410 需視資料格式調整)
    now = datetime.datetime.now()
    current_yyyymm = (now.year - 1911) * 100 + now.month  # 假設資料年月格式是民國年+月份，例如11410
    年月清單 = sorted(各同仁維修保養["年月"].dropna().unique())
    年月字串清單 = [str(y) for y in 年月清單]

    工程師清單 = sorted(各同仁維修保養["工程師"].dropna().unique())

    col_filter1, col_filter2 = st.columns([0.5, 0.5])
    with col_filter1:
        選工程師 = st.selectbox("選擇工程師", ["全部"] + 工程師清單)
    with col_filter2:
        預設年月字串 = str(current_yyyymm) if str(current_yyyymm) in 年月字串清單 else (年月字串清單[-1] if 年月字串清單 else "整年度")
        
        # 處理 index，避免在清單為空時出錯
        try:
             # 如果清單不為空，且預設字串在清單內，則將預設選項設為選單開頭 (預設選單開頭是 "整年度")
            default_index = 年月字串清單.index(預設年月字串) + 1 if 預設年月字串 != "整年度" and 預設年月字串 in 年月字串清單 else 0
        except ValueError:
             default_index = 0 # 找不到時預設選 "整年度"
        
        選年月 = st.selectbox("查詢年月（或選整年度）", ["整年度"] + 年月字串清單, index=default_index)

    # === 篩選 ===
    df_filtered = 各同仁維修保養.copy()

    if 選工程師 != "全部":
        df_filtered = df_filtered[df_filtered["工程師"] == 選工程師]

    if 選年月 != "整年度":
        選年月_int = int(選年月)    # 字串轉 int
        df_filtered = df_filtered[df_filtered["年月"] == 選年月_int]

    # === KPI ===
    維修總件數 = df_filtered["維修總件數"].sum()
    保養總件數 = df_filtered["保養總件數"].sum()
    未完成維修件數 = df_filtered["未完成維修件數"].sum()
    自修件數 = df_filtered["自修件數"].sum()
    自修率 = df_filtered["自修百分比"].mean()
    維修完成率 = (df_filtered["三十天內完成件數"].sum() / 維修總件數) if 維修總件數 else 0
    保養完成率 = (df_filtered["已完成保養件數"].sum() / 保養總件數) if 保養總件數 else 0
    五日內內修完成率 = (df_filtered["五日內內修完成件數"].sum() / 自修件數) if 自修件數 else 0
    自行已保養件數 = df_filtered["保養_自行已完成"].sum()
    委外已保養件數 = df_filtered["保養_委外已完成"].sum()
    租賃已保養件數 = df_filtered["保養_租賃已完成"].sum()
    保固已保養件數 = df_filtered["保養_保固已完成"].sum()
    自行未保養件數 = df_filtered["保養_自行未完成"].sum()
    委外未保養件數 = df_filtered["保養_委外未完成"].sum()
    租賃未保養件數 = df_filtered["保養_租賃未完成"].sum()
    保固未保養件數 = df_filtered["保養_保固未完成"].sum()
   
    st.markdown("---")
    st.markdown("### 🧾 維修資訊")
    col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5)
    with col_k1: colored_metric("維修總件數", f"{維修總件數:,}", "#00BFFF")
    with col_k2: colored_metric("未完成維修件數", f"{未完成維修件數:,}", "#00BFFF")
    with col_k3: colored_metric("維修完成率", f"{維修完成率*100:.2f}%", rate_color(維修完成率))
    with col_k5: colored_metric("五日內自修完成率", f"{五日內內修完成率*100:.2f}%", rate_color(五日內內修完成率))
    with col_k4: colored_metric("自修率", f"{自修率:.2f}%", rate_color(自修率))
    
    st.markdown("---")
    st.markdown("### 🧾 保養資訊")
    col_k11 ,col_k12 = st.columns(2)
    with col_k11: colored_metric("保養總件數", f"{保養總件數:,}", "#1E90FF")
    with col_k12: colored_metric("保養完成率", f"{保養完成率*100:.2f}%", rate_color(保養完成率))

    #st.markdown("---")
    col_k21 ,col_k22,col_k23,col_k24 = st.columns(4)
    with col_k21: colored_metric("自行已保養件數", f"{自行已保養件數:,}", "#1E90FF")
    with col_k22: colored_metric("委外已保養件數", f"{委外已保養件數:,}", "#7FED8A")
    with col_k23: colored_metric("保固已保養件數", f"{保固已保養件數:,}", "#ECE36A")
    with col_k24: colored_metric("租賃已保養件數", f"{租賃已保養件數:,}", "#E3A383")

    #st.markdown("---")
    col_k31 ,col_k32,col_k33,col_k34 = st.columns(4)
    with col_k31: colored_metric("自行未保養件數", f"{自行未保養件數:,}", "#1E90FF")
    with col_k32: colored_metric("委外未保養件數", f"{委外未保養件數:,}", "#7FED8A")
    with col_k33: colored_metric("保固未保養件數", f"{保固未保養件數:,}", "#ECE36A")
    with col_k34: colored_metric("租賃未保養件數", f"{租賃未保養件數:,}", "#E3A383")

    st.markdown("---")
    st.markdown("### 🧾 各工程師維修與保養相關資訊")
    # ===== 圖表展示區 =====
    col1, col2 = st.columns(2)

    # === 折線圖 ===
    if not df_filtered.empty:
        # 聚合資料
        df_line = df_filtered.groupby("工程師").agg({
            "維修總件數": "sum",
            "三十天內完成件數": "sum",
            "保養總件數": "sum",
            "已完成保養件數": "sum"
        }).reset_index()

        df_line["維修完成率"] = df_line["三十天內完成件數"] / df_line["維修總件數"].replace(0, 1)
        df_line["保養完成率"] = df_line["已完成保養件數"] / df_line["保養總件數"].replace(0, 1)

        fig_line = px.line(
            df_line,
            x="工程師",
            y=["維修完成率", "保養完成率"],
            markers=True,
            title="",
            labels={"value": "完成率 (%)", "variable": ""},
            hover_data={"value": ':.0%'},
            color_discrete_map={
                "維修完成率": "#1f77b4",
                "保養完成率": "#ff7f0e"
            }
        )
        fig_line.update_layout(
            title_x=0.5,
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            yaxis=dict(
                title="完成率 (%)",
                tickformat=".0%",
                range=[0, 1],
                dtick=0.2
            )
        )

        col1.plotly_chart(fig_line, use_container_width=True)
    else:
        col1.info("查無符合篩選條件的資料")

    # === 長條圖 ===
    if not df_filtered.empty:
        df_bar = df_filtered[["工程師", "維修總件數", "保養總件數"]].melt(
            id_vars="工程師", var_name="項目", value_name="件數"
        )

        color_map = {
            "維修總件數": "#1f77b4",
            "保養總件數": "#ff7f0e"
        }

        fig_bar = px.bar(
            df_bar,
            x="工程師",
            y="件數",
            color="項目",
            barmode="group",
            title="-",
            color_discrete_map=color_map
        )
        fig_bar.update_layout(
            title_x=0.5,
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text=""
        )

        col2.plotly_chart(fig_bar, use_container_width=True)

    # === 故障原因長條圖（可選擇顯示 Top N）===
    if not 維修.empty:
        df_維修_filtered = 維修.copy()

        # 篩選工程師
        if 選工程師 != "全部" and "工程師" in df_維修_filtered.columns:
            df_維修_filtered = df_維修_filtered[df_維修_filtered["工程師"] == 選工程師]

        # 篩選年月
        if 選年月 != "整年度" and "請修單年月" in df_維修_filtered.columns:
            try:
                df_維修_filtered = df_維修_filtered[
                    df_維修_filtered["請修單年月"].astype(str) == 選年月
                ]
            except:
                st.warning("請修單年月欄位格式不正確，無法篩選。")

        # 排除「無」或空值的故障原因
        if not df_維修_filtered.empty and "故障原因" in df_維修_filtered.columns:
            df_維修_filtered = df_維修_filtered[
                df_維修_filtered["故障原因"].notna() &
                (df_維修_filtered["故障原因"].astype(str).str.strip() != "無") &
                (df_維修_filtered["故障原因"].astype(str).str.strip() != "")
            ]

            if not df_維修_filtered.empty:
                # 故障原因統計
                counts = df_維修_filtered["故障原因"].value_counts()

                # === 使用者可選 Top N ===
                選TopN = st.selectbox("顯示前 N 名故障原因", [5, 10, 15, "全部"], index=1)

                if 選TopN != "全部":
                    counts = counts.head(int(選TopN))

                top_reasons = counts.reset_index()
                top_reasons.columns = ["故障原因", "件數"]

                # 依件數排序（由大到小）
                top_reasons = top_reasons.sort_values(by="件數", ascending=False)

                # === 建立長條圖 ===
                fig_bar = px.bar(
                    top_reasons,
                    x="故障原因",
                    y="件數",
                    title=f"故障原因分佈（Top {選TopN}）" if 選TopN != "全部" else "故障原因分佈（全部）",
                    text="件數",
                    color="故障原因",
                    color_discrete_sequence=px.colors.qualitative.Light24  # 多色亮色系
                )

                # 美化顯示
                fig_bar.update_traces(
                    texttemplate='%{y}件',
                    textposition='outside'
                )
                fig_bar.update_layout(
                    title_x=0.5,
                    xaxis_title="故障原因",
                    yaxis_title="件數",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    uniformtext_minsize=10,
                    uniformtext_mode='hide'
                )

                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("查無符合篩選條件的維修故障原因資料")
        else:
            st.info("查無符合篩選條件的維修故障原因資料")

    # === 未完成維修清單與未完成保養清單 ===
    st.markdown("---")
    st.markdown("### 🧾 未完成維修清單")
    if not 未完工.empty:
        df_unfinished_maintain = 未完工.copy()
        if 選工程師 != "全部" and "工程師" in df_unfinished_maintain.columns:
            df_unfinished_maintain = df_unfinished_maintain[df_unfinished_maintain["工程師"] == 選工程師]
        if 選年月 != "整年度" and "請修單年月" in df_unfinished_maintain.columns:
            try:
                df_unfinished_maintain = df_unfinished_maintain[df_unfinished_maintain["請修單年月"].astype(str) == 選年月]
            except:
                st.warning("未完工清單的請修單年月欄位格式不正確，無法篩選。")
                
        st.dataframe(df_unfinished_maintain, use_container_width=True)
    else:
        st.info("無未完成維修清單資料")

    st.markdown("### 🧾 未完成保養清單")
    if not 未完成保養.empty:
        df_unfinished_service = 未完成保養.copy()
        if 選工程師 != "全部" and "工程師" in df_unfinished_service.columns:
            df_unfinished_service = df_unfinished_service[df_unfinished_service["工程師"] == 選工程師]
        if 選年月 != "整年度" and "保養單年月" in df_unfinished_service.columns:
            try:
                df_unfinished_service = df_unfinished_service[df_unfinished_service["保養單年月"].astype(str) == 選年月]
            except:
                st.warning("未完成保養清單的保養單年月欄位格式不正確，無法篩選。")

        st.dataframe(df_unfinished_service, use_container_width=True)
    else:
        st.info("無未完成保養清單資料")

    st.markdown("---")
    
# ===== 第三頁：合約資訊 =====
if st.session_state.page == "contract":    # 🔹 左上角返回儀表板按鈕
    col_top_left, col_top_right = st.columns([1, 6])
    with col_top_left:
        if st.button("⬅️ 返回儀表板"):
            st.session_state.page = "main"
            st.rerun()

    # 重新載入資料
    各同仁維修保養, 維修, 合約清單, 合約內容, 未完工, 未完成保養, 到期合約, 設備清單 = load_data_from_gsheets()

    st.markdown("<h2 style='text-align:center; color:#6EC6FF;'>📘 合約資訊</h2>", unsafe_allow_html=True)

    # ===== KPI 資料計算（以你的合約內容表為例） =====
    # 總合約數與總金額仍算全部
    total_contracts = len(合約內容["ContractNo"].unique()) if "ContractNo" in 合約內容.columns else 0
    total_amount = 合約內容["Cost"].sum() if "Cost" in 合約內容.columns else 0

    # === 只統計未結束合約 (Date_T 為空者) ===
    if "Date_T" in 合約內容.columns:
        有效合約 = 合約內容[合約內容["Date_T"].isna()]
    else:
        有效合約 = pd.DataFrame() # 避免欄位不存在時出錯

    # 未結束合約的設備總台數
    total_assets = len(有效合約["AssetNo"].unique()) if "AssetNo" in 有效合約.columns else 0

    # 各類型合約台數（僅未結束合約）
    if "CLASS" in 有效合約.columns:
        full_contracts = 有效合約[有效合約["CLASS"].str.contains("全責", na=False)].shape[0]
        half_contracts = 有效合約[有效合約["CLASS"].str.contains("半責", na=False)].shape[0]
        labor_contracts = 有效合約[有效合約["CLASS"].str.contains("勞務", na=False)].shape[0]
        mix_contracts = 有效合約[有效合約["CLASS"].str.contains("複合", na=False)].shape[0]
    else:
        full_contracts = half_contracts = labor_contracts = mix_contracts = 0


    # ===== KPI 方塊樣式 =====
    st.markdown("""
        <style>
        .kpi-box {
            background-color: #11131a;
            border: 2px solid #2a2d36;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            margin: 5px;
        }
        .kpi-title {
            font-size: 20px;
            color: #d4d4d4;
        }
        .kpi-value {
            font-size: 50px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # ===== KPI 區塊排列（分兩列） =====
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

    with row1_col1:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">維護合約總件數</div>
                <div class="kpi-value" style="color:#99ccff;">{total_contracts}</div>
            </div>
        """, unsafe_allow_html=True)

    with row1_col2:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">維護合約金額</div>
                <div class="kpi-value" style="color:#ffb6c1;">{total_amount:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with row1_col3:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">合約設備總台數</div>
                <div class="kpi-value" style="color:#a4d8ff;">{total_assets}</div>
            </div>
        """, unsafe_allow_html=True)

    with row2_col1:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">全責合約台數</div>
                <div class="kpi-value" style="color:#fff8a3;">{full_contracts}</div>
            </div>
        """, unsafe_allow_html=True)

    with row2_col2:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">半責合約台數</div>
                <div class="kpi-value" style="color:#c7b5ff;">{half_contracts}</div>
            </div>
        """, unsafe_allow_html=True)

    with row2_col3:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">勞務台數</div>
                <div class="kpi-value" style="color:#e5f8cc;">{labor_contracts}</div>
            </div>
        """, unsafe_allow_html=True)

    with row2_col4:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">複合型合約台數</div>
                <div class="kpi-value" style="color:#ffb3b3;">{mix_contracts}</div>
            </div>
        """, unsafe_allow_html=True)

    # ===== 清單區塊 =====
    st.markdown("<br><h2 style='color:white;'>合約清單</h2>", unsafe_allow_html=True)
    column_configuration = {
        "ContractNo": "合約案號",
        "ContractName": "合約名稱",
        "SDate": "開始日期",
        "EDate": "結束日期",
        "Cost": "合約金額",
        "ContractYear": "合約年限",
        # 確保這裡列出了您想要顯示和重新命名的所有欄位
    }

    # 步驟 2: 呼叫 st.dataframe
    st.dataframe(
        合約清單,
        use_container_width=True,
        hide_index=True,
        column_config=column_configuration,
        # 步驟 3: 修正 column_order，使用 DataFrame 的原始欄位名稱
        column_order=["ContractNo", "ContractName", "SDate", "EDate", "Cost", "ContractYear"] 
    )

    st.markdown("<br><h2 style='color:white;'>半年內到期合約</h2>", unsafe_allow_html=True)
    st.dataframe(到期合約, use_container_width=True, hide_index=True)


# ===== 第四頁：設備資訊 =====
if st.session_state.page == "equipment":

    # 🔹 返回按鈕
    col_top_left, col_top_right = st.columns([1, 6])
    with col_top_left:
        # 重置 selected_device，避免返回儀表板再回來時還停留在舊的狀態
        if st.button("⬅️ 返回儀表板", key="return_to_main_eq"):
            st.session_state.page = "main"
            if "selected_device" in st.session_state:
                 del st.session_state.selected_device
            st.rerun()

    # 🔹 讀取資料
    各同仁維修保養, 維修, 合約清單, 合約內容, 未完工, 未完成保養, 到期合約, 設備清單 = load_data_from_gsheets()

    st.markdown("<h2 style='text-align:center; color:#6EC6FF;'>⚙️ 設備資訊</h2>", unsafe_allow_html=True)

    # === 篩選欄位 ===
    if 設備清單.empty:
        st.error("設備清單資料為空，無法顯示內容。")
    else:
        # 確保欄位存在且非空
        設備種類 = sorted(設備清單["設備類別"].dropna().unique())
        保管單位 = sorted(設備清單["部門名稱"].dropna().unique())
    
        col_filter1, col_filter2 = st.columns([0.5,0.5])
        with col_filter1:
            選設備種類 = st.selectbox("選擇設備種類", ["全部"] + 設備種類, key="select_device_type")
        with col_filter2:
            選保管單位 = st.selectbox("選擇保管單位", ["全部"] + 保管單位, key="select_department")
    
        # === 篩選資料 ===
        df_filtered = 設備清單.copy()
        if 選設備種類 != "全部":
            df_filtered = df_filtered[df_filtered["設備類別"] == 選設備種類]
        if 選保管單位 != "全部":
            df_filtered = df_filtered[df_filtered["部門名稱"] == 選保管單位]
    
        # === 統計每個設備種類的數量 ===
        設備統計 = df_filtered.groupby("設備類別").size().reset_index(name="數量")
    
        st.markdown("---")
    
        # === 標題列 ===
        st.markdown("""
            <div style='display:flex; justify-content:center; gap:250px; color:white; font-weight:600; font-size:20px;'>
                <div>設備種類</div>
                <div>數量</div>
                <div>設備種類</div>
                <div>數量</div>
            </div>
        """, unsafe_allow_html=True)
    
        # === 顏色設定 ===
        color_sequence = ["#6EC6FF", "#9AFF9A", "#FFB6B6", "#FFF59D"]
    
        # === CSS 樣式 ===
        st.markdown("""
            <style>
            .kpi-card {
                background-color: #111;
                border: 1.5px solid #444;
                border-radius: 25px;
                padding: 10px 0;
                text-align: center;
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 10px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
            </style>
        """, unsafe_allow_html=True)
    
        # === 顯示設備種類（每列兩組，共四欄） ===
        selected_device = st.session_state.get("selected_device", None)
        rows = 設備統計.reset_index(drop=True)
    
        for i in range(0, len(rows), 2):
            cols = st.columns(4)
            for j in range(2):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    color = color_sequence[(i + j) % len(color_sequence)]
                    key = f"btn_equip_{i}_{j}_{row['設備類別']}"
                    
                    st.markdown(
                        f"""
                        <style>
                        div[data-testid="stButton"][key="{key}"] button {{
                            background-color: #111;
                            color: {color};
                            border: 1.5px solid #444;
                            border-radius: 25px;
                            padding: 10px 0;
                            font-size: 20px;
                            font-weight: 600;
                            width: 100%;
                            margin-bottom: 10px;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
                            transition: all 0.2s ease-in-out;
                        }}
                        div[data-testid="stButton"][key="{key}"] button:hover {{
                            border-color: #888;
                            background-color: #1a1a1a;
                            box-shadow: 0 0 8px rgba(150, 220, 255, 0.4);
                            transform: scale(1.03);
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )

                    with cols[j*2]:
                        st.button(
                            row['設備類別'],
                            key=key, 
                            on_click=set_selected_device, 
                            args=(row['設備類別'],), 
                            use_container_width=True
                        )
    
                    with cols[j*2 + 1]:
                        st.markdown(
                            f"<div class='kpi-card' style='color:{color}; font-size:22px; font-weight:700;'>{row['數量']}</div>",
                            unsafe_allow_html=True,
                        )
    
        # === 點擊設備類別後顯示統計圖表 ===
        if selected_device:
            st.markdown("---")
            st.markdown(f"<h3 style='text-align:center; color:#6EC6FF;'>📊 {selected_device} 分布統計</h3>", unsafe_allow_html=True)
    
            subset = df_filtered[df_filtered["設備類別"] == selected_device]
    
            if not subset.empty:
                colA, colB = st.columns(2)
    
                # 統一 Plotly 樣式
                pie_template = dict(
                    paper_bgcolor="#0E0E0E",
                    plot_bgcolor="#0E0E0E",
                    font=dict(color="#E0E0E0"),
                    margin=dict(t=50, b=20, l=20, r=20),
                    legend=dict(bgcolor="#111", bordercolor="#555", borderwidth=1),
                    title_x=0.5
                )
    
                with colA:
                    if "廠牌" in subset.columns:
                        brand_counts = subset["廠牌"].value_counts().head(10).reset_index()
                        brand_counts.columns = ["廠牌", "數量"]
                        fig1 = px.pie(
                            brand_counts,
                            names="廠牌",
                            values="數量",
                            title="廠牌分布",
                            hole=0.4,
                            color_discrete_sequence=color_sequence
                        )
                        fig1.update_layout(**pie_template)
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.info("資料中缺少 '廠牌' 欄位。")
    
                with colB:
                    if "型號" in subset.columns:
                        model_counts = subset["型號"].value_counts().head(10).reset_index()
                        model_counts.columns = ["型號", "數量"]
                        fig2 = px.pie(
                            model_counts,
                            names="型號",
                            values="數量",
                            title="型號分布",
                            hole=0.4,
                            color_discrete_sequence=color_sequence
                        )
                        fig2.update_layout(**pie_template)
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.info("資料中缺少 '型號' 欄位。")
                #print([col.strip() for col in 設備清單.columns])

                # === 使用年數分布長條圖（下拉選擇互動 + 指定欄位表格） ===
                if "使用年數" in subset.columns:
                    subset = subset.dropna(subset=["使用年數"]).copy()
                    subset["使用年數"] = pd.to_numeric(subset["使用年數"], errors="coerce")
                    subset = subset[subset["使用年數"] > 0]

                    if subset.empty:
                        st.info("無可用的使用年數資料。")
                    else:
                        max_year = int(subset["使用年數"].max())
                        bins = list(range(0, max_year + 6, 5))
                        subset["使用年數區間"] = pd.cut(subset["使用年數"], bins=bins, right=False)

                        # 統計各區間數量
                        year_counts = subset["使用年數區間"].value_counts().reset_index()
                        year_counts.columns = ["使用年數區間", "數量"]
                        year_counts = year_counts[year_counts["數量"] > 0]

                        if year_counts.empty:
                            st.info("所有使用年數區間的數量皆為 0。")
                        else:
                            # 計算比例
                            total = year_counts["數量"].sum()
                            year_counts["比例 (%)"] = (year_counts["數量"] / total * 100).round(1)
                            year_counts["區間起始"] = year_counts["使用年數區間"].apply(lambda x: int(x.left))
                            year_counts = year_counts.sort_values("區間起始", ascending=False)

                            # 轉成文字顯示於圖表與下拉選單
                            year_counts["使用年數區間_str"] = year_counts["使用年數區間"].apply(
                                lambda x: f"{int(x.left)}–{int(x.right-1)}"
                            )
                            subset["使用年數區間_str"] = subset["使用年數區間"].apply(
                                lambda x: f"{int(x.left)}–{int(x.right-1)}"
                            )

                            color_sequence = px.colors.qualitative.Bold + px.colors.qualitative.Set3 + px.colors.qualitative.Pastel

                            # 長條圖
                            fig3 = px.bar(
                                year_counts,
                                x="使用年數區間_str",
                                y="數量",
                                title="使用年數分布（依範圍分組）",
                                text="數量",
                                color="使用年數區間_str",
                                color_discrete_sequence=color_sequence,
                                hover_data={"比例 (%)": True, "數量": True},
                            )
                            fig3.update_traces(
                                textposition="outside",
                                marker_line_color="#FFFFFF",
                                marker_line_width=1.2,
                                hovertemplate="使用年數區間: %{x}<br>數量: %{y} 台<br>比例: %{customdata[0]}%",
                            )
                            fig3.update_layout(
                                paper_bgcolor="#0E0E0E",
                                plot_bgcolor="#0E0E0E",
                                font=dict(color="#E0E0E0"),
                                margin=dict(t=50, b=50, l=40, r=20),
                                title_x=0.5,
                                xaxis=dict(
                                    title="使用年數區間",
                                    categoryorder="array",
                                    categoryarray=year_counts["使用年數區間_str"].tolist(),
                                ),
                                yaxis=dict(title="數量"),
                                showlegend=False,
                            )

                            st.plotly_chart(fig3, use_container_width=True)

                            # 下拉選單互動
                            interval_options = year_counts["使用年數區間_str"].tolist()
                            selected_interval = st.selectbox("選擇使用年數區間查看設備明細", ["全部"] + interval_options)

                            if selected_interval and selected_interval != "全部":
                                left, right = map(int, selected_interval.split("–"))
                                details = subset[(subset["使用年數"] >= left) & (subset["使用年數"] <= right)]
                            else:
                                details = subset

                            st.markdown("### 設備明細")
                            # 只顯示指定欄位
                            display_cols = ["財產編號", "廠牌", "型號", "取得日期","部門名稱","使用年數"]  # 可自行修改
                            display_cols = [c for c in display_cols if c in details.columns]
                            st.dataframe(details[display_cols].reset_index(drop=True))

                else:
                    st.info("資料中缺少 '使用年數' 欄位。")

# ===== 第五頁 庫房管理 =====
if st.session_state.page == "Parts":

    # 🔹 返回按鈕
    col_top_left, col_top_right = st.columns([1, 6])
    with col_top_left:
        # 重置 selected_device，避免返回儀表板再回來時還停留在舊的狀態
        if st.button("⬅️ 返回儀表板", key="return_to_main_eq"):
            st.session_state.page = "main"
            if "selected_device" in st.session_state:
                 del st.session_state.selected_device
            st.rerun()

    # 🔹 讀取資料
    各同仁維修保養, 維修, 合約清單, 合約內容, 未完工, 未完成保養, 到期合約, 設備清單 = load_data_from_gsheets()

    st.markdown("<h2 style='text-align:center; color:#6EC6FF;'>📘 庫房管理</h2>", unsafe_allow_html=True)