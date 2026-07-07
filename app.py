import streamlit as st
import requests
import base64
import datetime

# Page configuration
st.set_page_config(
    page_title="Hệ thống quản lý công văn - Thủy lợi Hải Dương",
    page_icon="📄",
    layout="centered"
)

# Custom Styling (Dark/Indigo Modern Aesthetic)
st.markdown("""
<style>
    /* Global Background and Typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header card */
    .header-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        padding: 2.5rem;
        border-radius: 24px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .header-logo {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
        color: white;
        font-size: 28px;
        font-weight: bold;
    }
    
    .header-title {
        background: linear-gradient(to right, #ffffff, #c7d2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 1.8rem;
        line-height: 1.3;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 300;
    }
    
    /* Input field borders and shadows */
    div[data-baseweb="input"], div[data-baseweb="select"], textarea {
        border-radius: 12px !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
    }
    
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Styled Submit Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 14px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
    }
    
    /* Alert / Link buttons */
    .sheet-link-btn {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981 !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        text-decoration: none;
        font-weight: 500;
        margin-top: 1rem;
        transition: all 0.2s ease;
    }
    
    .sheet-link-btn:hover {
        background-color: rgba(16, 185, 129, 0.25);
        border-color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Render Header
st.markdown("""
<div class="header-card">
    <div class="header-logo">📄</div>
    <div class="header-title">CÔNG TY TNHH MTV KHAI THÁC CÔNG TRÌNH THỦY LỢI HẢI DƯƠNG</div>
    <div class="header-subtitle">Hệ thống Nhập Công văn & Quản lý Tài liệu Hành chính (Streamlit REST API)</div>
</div>
""", unsafe_allow_html=True)

# Google Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxtTL8cXznFrzJle5HOryPuv8sUEdEfgtz4MkwRMoz94dKYqNxDFCbxztVSVBSbQrBdsA/exec"

# Fetch Company Documents for linkage
@st.cache_data(ttl=60)
def fetch_company_documents():
    try:
        r = requests.get(f"{WEB_APP_URL}?action=getCompanyDocs", timeout=12)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.warning(f"Không thể kết nối lấy danh mục công văn liên kết: {str(e)}")
    return []

# Fetch docs
company_docs = fetch_company_documents()
doc_options = ["-- Không liên kết --"] + [f"{d['docNumber']} - {d['summary'][:45]}" for d in company_docs if d.get('docNumber')]

# Form
with st.form("doc_input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        doc_type = st.selectbox(
            "Loại văn bản 🏷️",
            ["Công văn", "Quyết định", "Tờ trình", "Báo cáo", "Thông báo", "Hợp đồng", "Khác"]
        )
        
        target_sheet = st.selectbox(
            "Lưu vào trang tính 🗄️",
            ["Danh sách Công văn", "Công văn của công ty"]
        )
        
    with col2:
        doc_number = st.text_input("Số / Ký hiệu 🔢", placeholder="Ví dụ: 12/CV-UBND")
        
        # Link document selection
        if target_sheet == "Danh sách Công văn":
            linked_doc_selection = st.selectbox(
                "Công văn Công ty liên kết 🔗",
                doc_options
            )
        else:
            linked_doc_selection = "-- Không liên kết --"
            st.info("Trang tính Công văn của công ty không cần liên kết ngược.")

    col3, col4 = st.columns(2)
    with col3:
        publish_date = st.date_input("Ngày ban hành 📅", value=datetime.date.today())
    with col4:
        receive_date = st.date_input("Ngày nhận / Ngày gửi 📅", value=datetime.date.today())

    issuer = st.text_input("Cơ quan ban hành 🏢", placeholder="Tên cơ quan, doanh nghiệp phát hành văn bản")
    receiver = st.text_input("Nơi nhận / Người xử lý 👥", placeholder="Ví dụ: Ban Giám đốc, Phòng HC-NS...")
    
    summary = st.text_area("Trích yếu nội dung 📝", placeholder="Tóm tắt ngắn gọn nội dung cốt lõi của công văn", rows=3)
    
    # File attachment
    uploaded_file = st.file_uploader(
        "Tệp đính kèm (PDF, Docx, Image) 📎", 
        type=["pdf", "doc", "docx", "png", "jpg", "jpeg"]
    )
    
    submit_button = st.form_submit_button("Lưu Công Văn 📤")

# Handling submission
if submit_button:
    if not doc_number.strip():
        st.error("Vui lòng điền Số / Ký hiệu văn bản.")
    elif not issuer.strip():
        st.error("Vui lòng điền Cơ quan ban hành.")
    elif not receiver.strip():
        st.error("Vui lòng điền Nơi nhận / Người xử lý.")
    elif not summary.strip():
        st.error("Vui lòng điền Trích yếu nội dung.")
    else:
        with st.spinner("Đang xử lý dữ liệu và tải lên Google Drive..."):
            file_data_url = None
            if uploaded_file is not None:
                # Read and convert file to base64
                file_bytes = uploaded_file.read()
                file_b64 = base64.b64encode(file_bytes).decode("utf-8")
                file_data_url = f"data:{uploaded_file.type};base64,{file_b64}"
            
            # Extract linked doc number
            linked_doc_value = ""
            if linked_doc_selection != "-- Không liên kết --":
                linked_doc_value = linked_doc_selection.split(" - ")[0]
                
            # Build payload
            payload = {
                "docType": doc_type,
                "targetSheet": target_sheet,
                "linkedDoc": linked_doc_value,
                "docNumber": doc_number,
                "publishDate": publish_date.strftime("%Y-%m-%d"),
                "receiveDate": receive_date.strftime("%Y-%m-%d"),
                "issuer": issuer,
                "receiver": receiver,
                "summary": summary,
                "fileData": file_data_url,
                "fileName": uploaded_file.name if uploaded_file else None,
                "fileType": uploaded_file.type if uploaded_file else None
            }
            
            try:
                # Send POST request
                r = requests.post(WEB_APP_URL, json=payload, timeout=30)
                if r.status_code == 200:
                    response_json = r.json()
                    if response_json.get("success"):
                        st.success(f"🎉 {response_json.get('message')}")
                        st.balloons()
                        
                        sheet_url = response_json.get("sheetUrl")
                        if sheet_url:
                            st.markdown(
                                f'<a href="{sheet_url}" target="_blank" class="sheet-link-btn">👉 Nhấn vào đây để xem Google Sheets</a>',
                                unsafe_allow_html=True
                            )
                        # Clear cache to reflect new doc in list
                        st.cache_data.clear()
                    else:
                        st.error(f"Lỗi: {response_json.get('message')}")
                else:
                    st.error(f"Lỗi kết nối máy chủ Google (Status code: {r.status_code})")
            except Exception as e:
                st.error(f"Có lỗi xảy ra trong quá trình gửi yêu cầu: {str(e)}")
