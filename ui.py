import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="钢材表面缺陷检测系统", layout="centered")

st.title("🔬 热轧带钢表面缺陷检测系统")
st.markdown("上传钢材表面图像，系统将自动识别缺陷类型")

uploaded_file = st.file_uploader("选择图片...", type=["jpg", "jpeg", "png", "bmp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="上传的图片", use_container_width=True)
    
    if st.button("🔍 开始检测"):
        with st.spinner("检测中，请稍候..."):
            try:
                files = {"file": uploaded_file.getvalue()}
                response = requests.post("http://localhost:8000/predict", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ 检测完成！")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("缺陷类型", result["predicted_label"])
                    with col2:
                        st.metric("置信度", f"{result['confidence']*100:.1f}%")
                    # 这行已修改或删除，不再报错
                    # st.info(f"类别代码: {result['predicted_class']}")  
                else:
                    st.error("检测失败，请确保后端服务已启动")
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务，请先启动 FastAPI 服务")

st.markdown("---")
st.caption("基于 ResNet18 迁移学习 | NEU 表面缺陷数据集")