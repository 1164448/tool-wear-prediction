import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd
from datetime import datetime
import plotly.express as px

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="智能表面缺陷检测系统",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 初始化 session_state
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "detect_count" not in st.session_state:
    st.session_state.detect_count = 0
if "class_count" not in st.session_state:
    st.session_state.class_count = {
        "裂纹": 0, "夹杂物": 0, "斑块": 0,
        "麻点": 0, "氧化皮": 0, "划痕": 0
    }
if "show_chart" not in st.session_state:
    st.session_state.show_chart = False

# ============================================================
# 自定义CSS样式
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: #0b1a2e;
    }
    .main > div {
        background: transparent;
    }
    
    /* ===== 强制主区域所有文字为白色 ===== */
    .main * {
        color: #ffffff !important;
    }
    .main .stButton button {
        color: #ffffff !important;
    }
    
    /* ===== 侧边栏（蓝色系） ===== */
    .css-1d391kg, .css-1wrcr25 {
        background: linear-gradient(180deg, #0a1628 0%, #0d1f33 100%) !important;
    }
    .css-1d391kg *,
    .css-1wrcr25 * {
        color: #4FC3F7 !important;
    }
    .css-1d391kg .stButton button,
    .css-1wrcr25 .stButton button {
        color: #ffffff !important;
    }
    .css-1d391kg .sidebar-value,
    .css-1wrcr25 .sidebar-value {
        color: #64B5F6 !important;
    }
    .css-1d391kg .sidebar-title,
    .css-1wrcr25 .sidebar-title {
        color: #4FC3F7 !important;
        border-bottom: 1px solid #1a3a5a;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .css-1d391kg .sidebar-label,
    .css-1wrcr25 .sidebar-label {
        color: #4FC3F7 !important;
    }
    
    /* ===== 顶部导航栏 ===== */
    .header-container {
        background: linear-gradient(135deg, #0a1628 0%, #1a3050 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 6px solid #4FC3F7;
        border-bottom: 1px solid #1a3a5a;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .header-title {
        color: #ffffff !important;
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 0;
    }
    .header-subtitle {
        color: #ffffff !important;
        font-size: 0.9rem;
        margin: 0;
        letter-spacing: 2px;
    }
    .header-badge {
        background: rgba(79, 195, 247, 0.15);
        color: #ffffff !important;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        border: 1px solid rgba(79, 195, 247, 0.2);
    }
    
    /* ===== 卡片 ===== */
    .card {
        background: linear-gradient(145deg, #0f2137, #162b45);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #1a3a5a;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
    }
    .card-title {
        color: #ffffff !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .card-value {
        color: #ffffff !important;
        font-size: 2rem;
        font-weight: 700;
    }
    .card-value-small {
        color: #ffffff !important;
        font-size: 1.2rem;
        font-weight: 600;
    }
    .card-desc {
        color: #ffffff !important;
        font-size: 0.8rem;
        opacity: 0.8;
    }
    
    /* ===== 上传区域 ===== */
    .upload-area {
        border: 2px dashed #1a3a5a;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        background: rgba(255, 255, 255, 0.02);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .upload-area:hover {
        border-color: #4FC3F7;
        background: rgba(79, 195, 247, 0.05);
    }
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .upload-text {
        color: #ffffff !important;
        font-size: 1.1rem;
    }
    .upload-hint {
        color: #ffffff !important;
        font-size: 0.85rem;
        opacity: 0.7;
    }
    
    /* ===== 结果展示 ===== */
    .result-defect {
        color: #66BB6A !important;
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
    }
    .result-confidence {
        color: #ffffff !important;
        font-size: 1.2rem;
    }
    .result-confidence-bar {
        background: #1a3a2a;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin-top: 8px;
    }
    .result-confidence-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #43A047, #66BB6A);
        transition: width 0.8s ease;
    }
    .result-meta {
        color: #ffffff !important;
        font-size: 0.8rem;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid #1a3a2a;
        opacity: 0.8;
    }
    
    /* ===== 按钮 ===== */
    .stButton > button {
        background: linear-gradient(135deg, #1565C0, #0D47A1) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(21, 101, 192, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(21, 101, 192, 0.5) !important;
    }
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    
    /* ===== 文件上传器 ===== */
    .stFileUploader > div > button {
        background: transparent !important;
        color: #ffffff !important;
        border: 1px dashed #1a3a5a !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }
    .stFileUploader > div > button:hover {
        border-color: #4FC3F7 !important;
        background: rgba(79, 195, 247, 0.05) !important;
    }
    
    /* ===== 历史记录表格 ===== */
    .history-table {
        background: #0f2137;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #1a3a5a;
    }
    .stDataFrame, .stDataFrame table, .stDataFrame th, .stDataFrame td {
        color: #ffffff !important;
    }
    
    /* ===== 图表容器 ===== */
    .chart-container {
        background: #0f2137;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #1a3a5a;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:0.5rem 0 1rem 0;">
        <div style="font-size:2.8rem;">🏭</div>
        <div style="color:#4FC3F7;font-size:1.2rem;font-weight:600;">质检控制台</div>
        <div style="color:#64B5F6;font-size:0.75rem;letter-spacing:2px;">V1.0 · 工业版</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="sidebar-title">📊 系统状态</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sidebar-label">状态</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-value"><span class="status-indicator status-online"></span>在线</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="sidebar-label">模型</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-value">ResNet18</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-label">检测总量</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-value" style="font-size:1.8rem;font-weight:700;color:#4FC3F7;">{st.session_state.detect_count}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="sidebar-title">📈 缺陷分布</div>', unsafe_allow_html=True)
    for name, count in st.session_state.class_count.items():
        pct = (count / st.session_state.detect_count * 100) if st.session_state.detect_count > 0 else 0
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:3px 0;">
            <span style="color:#4FC3F7;font-size:0.85rem;">{name}</span>
            <span style="color:#64B5F6;font-size:0.85rem;font-weight:600;">{count}</span>
        </div>
        <div style="background:#1a2a3a;border-radius:4px;height:4px;margin-bottom:4px;overflow:hidden;">
            <div style="background:#4FC3F7;height:100%;width:{pct:.1f}%;border-radius:4px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<div class="sidebar-title">⚙️ 快捷操作</div>', unsafe_allow_html=True)
    if st.button("🗑️ 清空历史记录", use_container_width=True):
        st.session_state.history = []
        st.session_state.detect_count = 0
        st.session_state.class_count = {k: 0 for k in st.session_state.class_count}
        st.rerun()
    st.caption("🔬 基于 ResNet18 迁移学习 · NEU 数据集")

# ============================================================
# 主区域 - 顶部标题
# ============================================================
st.markdown("""
<div class="header-container">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
        <div>
            <div class="header-title">🔬 智能表面缺陷检测系统</div>
            <div class="header-subtitle">热轧带钢 · 六类缺陷自动识别 · 工业质检平台</div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <span class="header-badge">🟢 系统就绪</span>
            <span class="header-badge">📡 实时检测</span>
            <span class="header-badge">🏭 工业级</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 统计看板
# ============================================================
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📊 总检测数</div>
        <div class="card-value">{st.session_state.detect_count}</div>
        <div class="card-desc">累计检测图像数量</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    avg_conf = 0
    if st.session_state.history:
        avg_conf = sum(h.get("confidence", 0) for h in st.session_state.history) / len(st.session_state.history)
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🎯 平均置信度</div>
        <div class="card-value">{avg_conf*100:.1f}%</div>
        <div class="card-desc">所有检测结果平均值</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    last_result = "无"
    if st.session_state.history:
        last_result = st.session_state.history[-1].get("label", "无")
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🔍 最近检测</div>
        <div class="card-value-small">{last_result}</div>
        <div class="card-desc">最新一次检测结果</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat4:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🕐 系统时间</div>
        <div class="card-value-small">{now}</div>
        <div class="card-desc">当前服务器时间</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# 主功能区
# ============================================================
col_upload, col_result = st.columns([4, 8])

with col_upload:
    st.markdown('<div class="card"><div class="card-title">📤 图像采集</div></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "选择或拖拽上传图片",
        type=["jpg", "jpeg", "png", "bmp"],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="待检测图像", use_container_width=True)
    else:
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">🖼️</div>
            <div class="upload-text">点击或拖拽上传图像</div>
            <div class="upload-hint">支持 JPG · PNG · BMP</div>
        </div>
        """, unsafe_allow_html=True)

with col_result:
    st.markdown('<div class="card"><div class="card-title">🎯 缺陷检测</div></div>', unsafe_allow_html=True)
    if uploaded_file is not None:
        if st.button("🚀 执行检测", use_container_width=True):
            with st.spinner("🔄 模型推理中，请稍候..."):
                try:
                    files = {"file": uploaded_file.getvalue()}
                    response = requests.post("http://localhost:8000/predict", files=files, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        predicted_label = result.get("predicted_label", "未知")
                        confidence = result.get("confidence", 0.0)
                        predicted_class = result.get("predicted_class", "")
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.session_state.history.append({
                            "time": now,
                            "label": predicted_label,
                            "class": predicted_class,
                            "confidence": confidence
                        })
                        st.session_state.detect_count += 1
                        if predicted_label in st.session_state.class_count:
                            st.session_state.class_count[predicted_label] += 1
                        
                        st.markdown(f"""
                        <div style="background:linear-gradient(145deg,#0a2a1a,#0d3a25);border:1px solid #2a7a4a;border-radius:16px;padding:2rem;margin-top:0.5rem;box-shadow:0 4px 20px rgba(76,175,80,0.08);">
                            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                                <div>
                                    <div style="color:#90CAF9;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;">检测结果</div>
                                    <div style="color:#66BB6A;font-size:2.8rem;font-weight:700;margin:0;">{predicted_label}</div>
                                </div>
                                <div style="text-align:right;">
                                    <div style="color:#90CAF9;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;">置信度</div>
                                    <div style="color:#ffffff;font-size:1.2rem;">{confidence*100:.1f}%</div>
                                </div>
                            </div>
                            <div style="background:#1a3a2a;border-radius:10px;height:8px;overflow:hidden;margin-top:8px;">
                                <div style="height:100%;border-radius:10px;background:linear-gradient(90deg,#43A047,#66BB6A);width:{confidence*100:.1f}%;transition:width 0.8s ease;"></div>
                            </div>
                            <div style="color:#ffffff;font-size:0.8rem;margin-top:0.8rem;padding-top:0.8rem;border-top:1px solid #1a3a2a;opacity:0.8;">
                                检测时间：{now} ｜ 类别代码：{predicted_class}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ 检测失败 (HTTP {response.status_code})")
                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务，请确认 `app.py` 正在运行")
                except Exception as e:
                    st.error(f"❌ 检测异常：{str(e)}")
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0;">
            <div style="font-size:4rem;opacity:0.3;">⏳</div>
            <div style="color:#ffffff;font-size:1rem;">请从左侧上传待检测图像</div>
            <div style="color:#ffffff;font-size:0.8rem;margin-top:0.3rem;opacity:0.7;">上传后点击「执行检测」按钮</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 历史记录
# ============================================================
st.markdown("---")
st.markdown('<div style="color:#ffffff;font-size:1.1rem;font-weight:600;padding:0 0.5rem;">📋 检测历史记录</div>', unsafe_allow_html=True)

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    df["confidence"] = df["confidence"].apply(lambda x: f"{x*100:.1f}%")
    df = df.rename(columns={
        "time": "检测时间",
        "label": "缺陷类型",
        "class": "类别代码",
        "confidence": "置信度"
    })
    col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 8])
    with col_filter1:
        filter_label = st.selectbox(
            "🔍 按缺陷类型筛选",
            ["全部"] + list(st.session_state.class_count.keys()),
            label_visibility="collapsed"
        )
    with col_filter2:
        st.markdown(f'<div style="color:#ffffff;font-size:0.85rem;padding-top:0.5rem;opacity:0.8;">共 {len(df)} 条记录</div>', unsafe_allow_html=True)
    if filter_label != "全部":
        df = df[df["缺陷类型"] == filter_label]
    
    st.markdown('<div class="history-table">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     "检测时间": st.column_config.TextColumn("检测时间", width="medium"),
                     "缺陷类型": st.column_config.TextColumn("缺陷类型", width="small"),
                     "类别代码": st.column_config.TextColumn("类别代码", width="small"),
                     "置信度": st.column_config.TextColumn("置信度", width="small"),
                 })
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_export1, col_export2, col_export3 = st.columns([2, 2, 8])
    with col_export1:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 导出报告 (CSV)",
            data=csv,
            file_name=f"检测报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_export2:
        if st.button("📊 查看统计图表", use_container_width=True):
            st.session_state.show_chart = not st.session_state.show_chart
else:
    st.markdown("""
    <div style="text-align:center;padding:2rem 0;">
        <div style="font-size:2rem;opacity:0.3;">📭</div>
        <div style="color:#ffffff;">暂无检测记录</div>
        <div style="color:#ffffff;font-size:0.85rem;opacity:0.7;">执行检测后，历史记录将在此显示</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 统计图表
# ============================================================
if st.session_state.get("show_chart", False) and st.session_state.history:
    st.markdown("---")
    st.markdown('<div style="color:#ffffff;font-size:1.1rem;font-weight:600;padding:0 0.5rem;margin-bottom:1rem;">📊 检测统计分析</div>', unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        df_hist = pd.DataFrame(st.session_state.history)
        class_dist = df_hist["label"].value_counts().reset_index()
        class_dist.columns = ["缺陷类型", "数量"]
        if not class_dist.empty:
            fig = px.pie(
                class_dist,
                values="数量",
                names="缺陷类型",
                title="缺陷类型分布",
                color_discrete_sequence=px.colors.qualitative.Set2,
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff", size=14),
                title_font=dict(color="#ffffff", size=16),
                legend=dict(font=dict(color="#ffffff"))
            )
            fig.update_traces(textfont=dict(color="#ffffff"))
            # ✅ 恢复了工具栏（移除了 config={'displayModeBar': False}）
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_chart2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if not df_hist.empty:
            fig = px.histogram(
                df_hist,
                x="confidence",
                nbins=20,
                title="置信度分布",
                labels={"confidence": "置信度", "count": "频次"},
                color_discrete_sequence=["#4FC3F7"],
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff", size=14),
                title_font=dict(color="#ffffff", size=16),
                xaxis_title_font=dict(color="#ffffff"),
                yaxis_title_font=dict(color="#ffffff"),
                xaxis=dict(tickfont=dict(color="#ffffff")),
                yaxis=dict(tickfont=dict(color="#ffffff")),
                legend=dict(font=dict(color="#ffffff"))
            )
            # ✅ 恢复了工具栏
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 底部
# ============================================================
st.markdown("---")
st.markdown("""
<div style="display:flex;justify-content:space-between;color:#ffffff;font-size:0.8rem;padding:0.5rem 0;flex-wrap:wrap;opacity:0.7;">
    <span>🏭 工业质检系统 · 课程设计演示</span>
    <span>基于 ResNet18 迁移学习 · NEU 表面缺陷数据集</span>
    <span>© 2026 智造24-1 · 陈树涵</span>
</div>
""", unsafe_allow_html=True)