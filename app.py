import streamlit as st

st.set_page_config(
    page_title="CÔNG TY TNHH MTV KHAI THÁC CÔNG TRÌNH THỦY LỢI HẢI DƯƠNG",
    page_icon="📄",
    layout="wide"
)

# Custom header styling
st.markdown("""
<style>
    .header-container {
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
    }
</style>
<div class="header-container">
    <div class="header-title">CÔNG TY TNHH MTV KHAI THÁC CÔNG TRÌNH THỦY LỢI HẢI DƯƠNG</div>
    <div class="header-subtitle">Hệ thống Nhập Công văn & Quản lý Tài liệu Hành chính</div>
</div>
""", unsafe_allow_html=True)

# Deployed Web App URL
web_app_url = "https://script.google.com/macros/s/AKfycbxtTL8cXznFrzJle5HOryPuv8sUEdEfgtz4MkwRMoz94dKYqNxDFCbxztVSVBSbQrBdsA/exec"

# Embed the web app inside Streamlit iframe
st.components.v1.iframe(web_app_url, height=900, scrolling=True)
