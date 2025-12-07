# app.py
import streamlit as st
import joblib
import re
import nltk
import os
from gmail_helper import get_gmail_service_auto, fetch_emails # Import hàm hỗ trợ

# === FIX LỖI NLTK ===
@st.cache_resource
def download_nltk_data():
    try: nltk.data.find('corpora/stopwords')
    except LookupError: nltk.download('stopwords')
    try: nltk.data.find('tokenizers/punkt')
    except LookupError: nltk.download('punkt')

download_nltk_data()
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# === LOAD MODEL (Giữ nguyên) ===
@st.cache_resource
def load_model():
    # Lưu ý: Đảm bảo file .pkl có trong thư mục
    try:
        model = joblib.load('bernoulli_model.pkl')
        tfidf = joblib.load('tfidf_vectorizer.pkl')
        return model, tfidf
    except:
        return None, None

model, tfidf = load_model()

# === TIỀN XỬ LÝ (Giữ nguyên) ===
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words and len(w) > 2]
    return ' '.join(words)

# ================== CẤU HÌNH TRANG ==================
st.set_page_config(page_title="Phishing Detector", page_icon="Shield", layout="centered")

# === SIDEBAR MỚI: SIÊU ĐƠN GIẢN ===
with st.sidebar:
    st.header("📧 Gmail Login")
    
    # Init session
    if 'google_creds' not in st.session_state: st.session_state.google_creds = None
    if 'email_list' not in st.session_state: st.session_state.email_list = []
    
    # 1. NẾU CHƯA ĐĂNG NHẬP
    if not st.session_state.google_creds:
        st.info("Bấm nút dưới để mở cửa sổ đăng nhập Google.")
        
        # Nút bấm duy nhất
        if st.button("Đăng nhập bằng Google"):
            with st.spinner("Đang mở trình duyệt... Vui lòng đăng nhập!"):
                # Gọi hàm tự động
                creds = get_gmail_service_auto()
                
                if creds:
                    st.session_state.google_creds = creds
                    st.success("Đăng nhập thành công!")
                    st.rerun() # Tự load lại trang ngay lập tức
                else:
                    st.error("Đăng nhập thất bại hoặc bị hủy.")

    # 2. NẾU ĐÃ ĐĂNG NHẬP (Phần này giữ nguyên y hệt cũ)
    else:
        st.success(f"✅ Đã kết nối")
        if st.button("Tải lại Email"):
            st.session_state.email_list = fetch_emails(st.session_state.google_creds)
            
        if st.session_state.email_list:
            options = [f"{e['subject'][:30]}..." for e in st.session_state.email_list]
            choice = st.radio("Inbox:", options)
            idx = options.index(choice)
            
            if st.button("Chọn email này >>"):
                # Lấy cả tiêu đề và nội dung
                subj = st.session_state.email_list[idx]['subject']
                body = st.session_state.email_list[idx]['body']
                
                # Nối lại thành một chuỗi duy nhất
                # Kỹ thuật: f-string giúp chèn biến vào chuỗi dễ dàng
                full_text = f"Subject: {subj}\n\n{body}"
                
                # Gán vào biến chung để đưa sang màn hình chính
                st.session_state.content_to_fill = full_text
                st.toast("Đã lấy Tiêu đề + Nội dung!")

        if st.button("Đăng xuất"):
            st.session_state.google_creds = None
            st.session_state.email_list = []
            st.rerun()

# ================== GIAO DIỆN CHÍNH (GIỮ NGUYÊN CŨ) ==================
st.markdown("""
<style>
    .title {font-size: 48px; font-weight: bold; color: #FF4B4B; text-align: center;}
    .subtitle {font-size: 20px; color: #666; text-align: center;}
    .result-safe {font-size: 32px; color: #00C853; font-weight: bold;}
    .result-phish {font-size: 32px; color: #D50000; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">PHÁT HIỆN EMAIL LỪA ĐẢO</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Bernoulli Naïve Bayes + GridSearch | Accuracy 97.83%</p>', unsafe_allow_html=True)
st.markdown("---")

# Logic điền nội dung tự động từ Sidebar
default_val = ""
if 'content_to_fill' in st.session_state:
    default_val = st.session_state.content_to_fill

# Ô nhập liệu (có thể nhập tay HOẶC tự điền từ Gmail)
email_text = st.text_area("Dán nội dung email vào đây (subject + body):", value=default_val, height=280)

if st.button("KIỂM TRA NGAY", type="primary", use_container_width=True):
    if email_text.strip():
        if model:
            with st.spinner("Đang phân tích..."):
                clean = preprocess(email_text)
                if len(clean.split()) < 3:
                    st.warning("Email quá ngắn!")
                else:
                    X = tfidf.transform([clean])
                    pred = model.predict(X)[0]
                    prob = model.predict_proba(X)[0].max() * 100
                    
                    st.markdown("---")
                    if pred == 1:
                        st.markdown(f'<p class="result-phish">CẢNH BÁO: EMAIL LỪA ĐẢO!</p>', unsafe_allow_html=True)
                        st.error(f"Độ tin cậy: {prob:.2f}%")
                    else:
                        st.markdown(f'<p class="result-safe">Email an toàn</p>', unsafe_allow_html=True)
                        st.success(f"Độ tin cậy: {prob:.2f}%")
        else:
             st.error("Lỗi: Không tìm thấy file Model!")
    else:
        st.error("Vui lòng dán nội dung email!")

st.markdown("---")
st.caption("Đồ án tốt nghiệp 2025 – Accuracy 97.83%")