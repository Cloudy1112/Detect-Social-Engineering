# app.py
import streamlit as st
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Load model (phải cùng thư mục)
@st.cache_resource
def load_model():
    model = joblib.load('bernoulli_model.pkl')
    tfidf = joblib.load('tfidf_vectorizer.pkl')
    return model, tfidf

model, tfidf = load_model()

# Tiền xử lý giống hệt lúc train
nltk.data.path.append("nltk_data")  # nếu lỗi thì bỏ dòng này
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words and len(w) > 2]
    return ' '.join(words)

# GIAO DIỆN SIÊU ĐẸP
st.set_page_config(page_title="Phishing Detector - Bernoulli 97.83%", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
    .title {font-size: 48px; font-weight: bold; color: #FF4B4B; text-align: center;}
    .subtitle {font-size: 20px; color: #666; text-align: center;}
    .result-safe {font-size: 32px; color: #00C853; font-weight: bold;}
    .result-phish {font-size: 32px; color: #D50000; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">PHÁT HIỆN EMAIL LỪA ĐẢO</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Bernoulli Naïve Bayes + GridSearch | Accuracy 97.83% trên CEAS_08<br>'
            'Vượt nghiên cứu gốc Sinkron 2023 (97.38%)</p>', unsafe_allow_html=True)

st.markdown("---")

email_text = st.text_area("Dán toàn bộ nội dung email (subject + body) vào đây:", height=280, placeholder="Ví dụ: Urgent! Your account will be suspended...")

if st.button("KIỂM TRA NGAY", type="primary", use_container_width=True):
    if email_text.strip():
        with st.spinner("Đang phân tích email..."):
            clean = preprocess(email_text)
            if len(clean.split()) < 3:
                st.warning("Email quá ngắn hoặc không có nội dung hợp lệ!")
            else:
                X = tfidf.transform([clean])
                pred = model.predict(X)[0]
                prob = model.predict_proba(X)[0].max() * 100

                if pred == 1:
                    st.markdown(f'<p class="result-phish">CẢNH BÁO: EMAIL LỪA ĐẢO – PHISHING!</p>', unsafe_allow_html=True)
                    st.error(f"Độ tin cậy: {prob:.2f}%")
                    st.warning("Không click link, không cung cấp thông tin cá nhân!")
                else:
                    st.markdown(f'<p class="result-safe">Email an toàn – Safe Email</p>', unsafe_allow_html=True)
                    st.success(f"Độ tin cậy: {prob:.2f}%")
    else:
        st.error("Vui lòng dán nội dung email!")

st.markdown("---")
st.caption("Đồ án tốt nghiệp 2025 – Dựa trên bài báo Sinkron Vol.8 No.4, 2023 – Accuracy 97.83%")