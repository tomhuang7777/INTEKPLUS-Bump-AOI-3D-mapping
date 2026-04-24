import streamlit as st
import pandas as pd
import plotly.express as px
import re
我老婆好正
# ==========================================
# 1. 網頁基本設定 & CSS 護眼/質感魔法注入
# ==========================================
st.set_page_config(page_title="AOI 3D Data Viewer", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background-color: #F0F4F8; }
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #FFFFFF; }
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(90deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%);
    color: white; border: none; border-radius: 8px;
    transition: all 0.3s ease 0s; font-weight: bold;
}
[data-testid="stFormSubmitButton"] button:hover {
    box-shadow: 0 5px 15px rgba(67, 100, 247, 0.4);
    transform: translateY(-2px); border-color: transparent; color: white;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 多國語系字典檔
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "INTEKPLUS Bump AOI 3D mapping tool",
        "subtitle": "Version 1: 支援本機與雲端載入，優化 3D 渲染流暢度 (手機版建議橫向檢視)",
        "sidebar_title": "🌐 語言與設定 / Language",
        "header_row": "設定 CSV 標題列位置 (0 代表第一列)",
        "step1": "📁 步驟 1：載入機台檢測報表",
        "upload_csv": "📂 方式 A：上傳本機 CSV 檔案",
        "gdrive_url": "🔗 方式 B：貼上 Google 雲端公開連結",
        "load_success": "✅ 數據載入成功！",
        "preview": "👁️ 預覽載入的原始資料 (點擊展開)",
        "step2": "⚙️ 步驟 2：設定 XYZ 座標軸與料片分析",
        "select_x": "選擇 X 座標",
        "select_y": "選擇 Y 座標",
        "select_z": "選擇 Z 軸 (Data Value)",
        "select_chip": "選擇 Chip No. 欄位在哪一個 (可選)",
        "no_chip": "無 (不分 Chip)，全部疊一起",
        "select_target_chip": "請選擇要繪製的 Chip (可多選)",
        "step3": "📊 步驟 3：進階設定與建立散佈圖",
        "enable_range": "啟用手動設定座標軸範圍 (多料片統一全球距)",
        "submit_btn": "🚀 套用設定並建立 3D 散佈圖",
        "loading": "正在將數據載入記憶體，請稍候...",
        "drawing": "啟動 GPU 渲染，正在繪製高畫質 3D 圖表...",
        "err_no_chip": "請先在上方選擇至少一顆 Chip！"
    },
    "English": {
        "title": "INTEKPLUS Bump AOI 3D mapping tool",
        "subtitle": "Version 1: Supports local & cloud data, optimized rendering (Landscape recommended)",
        "sidebar_title": "🌐 Language Settings",
        "header_row": "Set CSV Header Row Index (0 = first row)",
        "step1": "📁 Step 1: Load Inspection Data",
        "upload_csv": "📂 Method A: Upload Local CSV",
        "gdrive_url": "🔗 Method B: Paste Google Drive Public Link",
        "load_success": "✅ Data loaded successfully!",
        "preview": "👁️ Preview Raw Data (Click to Expand)",
        "step2": "⚙️ Step 2: Set XYZ Axes & Chip Analysis",
        "select_x": "Select X Axis",
        "select_y": "Select Y Axis",
        "select_z": "Select Z Axis (Data Value)",
        "select_chip": "Select which column is Chip No. (Optional)",
        "no_chip": "None (No Chip distinction), all stacked",
        "select_target_chip": "Select Chips to Plot (Multiple allowed)",
        "step3": "📊 Step 3: Advanced Settings & Generation",
        "enable_range": "Enable Manual Axis Range (Global Scale)",
        "submit_btn": "🚀 Apply & Create 3D Scatter Plot",
        "loading": "Loading data into memory, please wait...",
        "drawing": "Starting GPU rendering, generating 3D plot...",
        "err_no_chip": "Please select at least one Chip above!"
    },
    "한국어": {
        "title": "INTEKPLUS Bump AOI 3D mapping tool",
        "subtitle": "Version 1: 로컬/클라우드 지원, 렌더링 최적화 (모바일 가로 모드 권장)",
        "sidebar_title": "🌐 언어 설정",
        "header_row": "CSV 헤더 행 인덱스 설정 (0 = 첫 번째 행)",
        "step1": "📁 1단계: 검사 데이터 로드",
        "upload_csv": "📂 방법 A: 로컬 CSV 파일 업로드",
        "gdrive_url": "🔗 방법 B: 공개 Google 드라이브 링크 붙여넣기",
        "load_success": "✅ 데이터가 성공적으로 로드되었습니다!",
        "preview": "👁️ 원본 데이터 미리보기 (클릭하여 확장)",
        "step2": "⚙️ 2단계: XYZ 축 및 칩 분석 설정",
        "select_x": "X 축 좌표 선택",
        "select_y": "Y 축 좌표 선택",
        "select_z": "Z 축 선택 (데이터 값)",
        "select_chip": "어떤 열이 Chip No.인지 선택 (선택 사항)",
        "no_chip": "없음 (칩 구분 없음), 모두 겹쳐서 표시",
        "select_target_chip": "시각화할 칩 선택 (다중 선택 가능)",
        "step3": "📊 3단계: 고급 설정 및 산점도 생성",
        "enable_range": "수동 좌표축 범위 설정 (전역 스케일 통일)",
        "submit_btn": "🚀 적용 및 3D 산점도 생성",
        "loading": "메모리에 데이터를 로드하는 중입니다...",
        "drawing": "GPU 렌더링 시작, 고화질 3D 차트 생성 중...",
        "err_no_chip": "위에서 하나 이상의 칩을 선택해주세요!"
    }
}

# ==========================================
# 3. 側邊欄：語言與初始設定
# ==========================================
st.sidebar.markdown(f"### {LANG_DICT['繁體中文']['sidebar_title']}")
selected_lang = st.sidebar.selectbox("Language / 언어", options=["繁體中文", "English", "한국어"], label_visibility="collapsed")
t = LANG_DICT[selected_lang]

st.sidebar.divider()
header_row = st.sidebar.number_input(t["header_row"], min_value=0, value=0, step=1)

@st.cache_data(show_spinner=False)
def load_data(file_source, header_idx):
    if hasattr(file_source, 'seek'):
        file_source.seek(0)
    return pd.read_csv(file_source, header=header_idx)

def convert_gdrive_url(url):
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

# ==========================================
# 4. 主畫面介面
# ==========================================
st.title(t["title"])
st.markdown(f"**{t['subtitle']}**")
st.divider()

with st.container(border=True):
    st.subheader(t["step1"])
    col_upload, col_url = st.columns(2)
    with col_upload:
        uploaded_file = st.file_uploader(t["upload_csv"], type=['csv'])
    with col_url:
        gdrive_url = st.text_input(t["gdrive_url"], placeholder="https://drive.google.com/file/d/.../view")

data_source = None
if uploaded_file is not None:
    data_source = uploaded_file
elif gdrive_url:
    data_source = convert_gdrive_url(gdrive_url)

if data_source is not None:
    try:
        with st.spinner(t["loading"]):
            df = load_data(data_source, header_row)
        
        st.success(t["load_success"])
        
        with st.expander(t["preview"]):
            st.dataframe(df.head())

        columns = df.columns.tolist()
        
        def get_smart_index(col_names, keywords, fallback=0):
            for i, col in enumerate(col_names):
                col_lower = str(col).lower()
                for kw in keywords:
                    if kw.lower() in col_lower:
                        return i
            return fallback if fallback < len(col_names) else 0

        idx_x = get_smart_index(columns, ['cad x', 'x座標', 'x_pos', 'x'], 0)
        idx_y = get_smart_index(columns, ['cad y', 'y座標', 'y_pos', 'y'], 0)
        idx_z = get_smart_index(columns, ['bump height', 'copl', 'btv', 'ctv', 'height', 'z'], 0)
        idx_chip_raw = get_smart_index(columns, ['chip no', 'core no', 'chip'], -1)
        idx_chip = idx_chip_raw + 1 if idx_chip_raw != -1 else 0
        
        with st.container(border=True):
            st.subheader(t["step2"])
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                x_col = st.selectbox(t["select_x"], options=columns, index=idx_x)
            with col2:
                y_col = st.selectbox(t["select_y"], options=columns, index=idx_y)
            with col3:
                z_col = st.selectbox(t["select_z"], options=columns, index=idx_z)
            with col4:
                chip_options = [t["no_chip"]] + columns
                chip_col = st.selectbox(t["select_chip"], options=chip_options, index=idx_chip)

            # 🌟 終極修復魔法：強制作業與向下填滿 🌟
            # 1. 確保 XYZ 欄位都是數字，若是夾雜英文字母或空白，直接轉為 NaN
            df[x_col] = pd.to_numeric(df[x_col], errors='coerce')
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df[z_col] = pd.to_numeric(df[z_col], errors='coerce')

            # 2. 如果使用者有選擇 Chip No，使用 ffill() 讓空白的 Bump 列自動繼承上方的 Core ID
            if chip_col != t["no_chip"]:
                df[chip_col] = df[chip_col].ffill()

            # 3. 剔除座標缺漏的無效資料
            plot_df = df.dropna(subset=[x_col, y_col, z_col])

            # 4. 防呆保護：如果剔除後沒有有效資料，顯示警告而非直接崩潰
            if plot_df.empty:
                st.warning("⚠️ 找不到有效的 3D 數值。請確認您左側的【CSV 標題列位置】是否設定正確，或檢查選取的 XYZ 欄位是否存在資料。")
            else:
                selected_chips = []
                if chip_col != t["no_chip"]:
                    unique_chips = plot_df[chip_col].dropna().unique().tolist()
                    selected_chips = st.multiselect(t["select_target_chip"], options=unique_chips, default=unique_chips[:1])

            with st.container(border=True):
                st.subheader(t["step3"])
                
                with st.form("plot_settings_form", border=False):
                    use_custom_range = st.checkbox(t["enable_range"])
                    
                    c1, c2, c3 = st.columns(3)
                    
                    # 加入安全預設值，防止空資料導致 NaN 崩潰
                    safe_x_min = float(plot_df[x_col].min()) if not plot_df.empty else 0.0
                    safe_x_max = float(plot_df[x_col].max()) if not plot_df.empty else 100.0
                    safe_y_min = float(plot_df[y_col].min()) if not plot_df.empty else 0.0
                    safe_y_max = float(plot_df[y_col].max()) if not plot_df.empty else 100.0
                    safe_z_min = float(plot_df[z_col].min()) if not plot_df.empty else 0.0
                    safe_z_max = float(plot_df[z_col].max()) if not plot_df.empty else 100.0

                    with c1:
                        x_min = st.number_input("X Min", value=safe_x_min)
                        x_max = st.number_input("X Max", value=safe_x_max)
                    with c2:
                        y_min = st.number_input("Y Min", value=safe_y_min)
                        y_max = st.number_input("Y Max", value=safe_y_max)
                    with c3:
                        z_min = st.number_input("Z Min", value=safe_z_min)
                        z_max = st.number_input("Z Max", value=safe_z_max)

                    submitted = st.form_submit_button(t["submit_btn"], use_container_width=True)

            if submitted and not plot_df.empty:
                if chip_col != t["no_chip"] and not selected_chips:
                    st.error(t["err_no_chip"])
                else:
                    with st.spinner(t["drawing"]):
                        plots_to_draw = []
                        
                        if chip_col == t["no_chip"]:
                            plots_to_draw.append((f"{z_col} Scatter Plot", plot_df))
                        else:
                            for chip in selected_chips:
                                chip_df = plot_df[plot_df[chip_col] == chip]
                                plots_to_draw.append((f"Chip: {chip} | {z_col} Scatter Plot", chip_df))
                        
                        for title, data_subset in plots_to_draw:
                            if data_subset.empty:
                                continue
                            
                            fig = px.scatter_3d(
                                data_subset, x=x_col, y=y_col, z=z_col,
                                color=z_col, color_continuous_scale="Turbo", title=title
                            )
                            
                            fig.update_traces(marker=dict(size=2, opacity=1.0, line=dict(width=0)))
                            
                            scene_layout = dict(
                                xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col,
                                aspectmode='cube' 
                            )

                            if use_custom_range:
                                scene_layout['xaxis'] = dict(range=[x_min, x_max])
                                scene_layout['yaxis'] = dict(range=[y_min, y_max])
                                scene_layout['zaxis'] = dict(range=[z_min, z_max])

                            fig.update_layout(
                                margin=dict(l=0, r=0, b=0, t=40),
                                scene=scene_layout
                            )

                            with st.container(border=True):
                                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 檔案讀取或處理發生錯誤！")
        st.warning(f"系統錯誤代碼: {e}")