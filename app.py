# app.py – ĐÃ FIX LỖI NLTK TRÊN STREAMLIT CLOUD
import streamlit as st
import joblib
import re
import nltk
import os

# === FIX LỖI NLTK TRÊN STREAMLIT CLOUD ===
@st.cache_resource
def download_nltk_data():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

download_nltk_data()
# ==========================================

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Load model
@st.cache_resource
def load_model():
    model = joblib.load('bernoulli_model.pkl')
    tfidf = joblib.load('tfidf_vectorizer.pkl')
    return model, tfidf

model, tfidf = load_model()

# Tiền xử lý
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words and len(w) > 2]
    return ' '.join(words)

# ================== GIAO DIỆN (giữ nguyên như cũ) ==================
st.set_page_config(page_title="Phishing Detector - Bernoulli 97.83%", page_icon="Shield", layout="centered")

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

email_text = st.text_area("Dán toàn bộ nội dung email (subject + body) vào đây:", height=280)

if st.button("KIỂM TRA NGAY", type="primary", use_container_width=True):
    if email_text.strip():
        with st.spinner("Đang phân tích..."):
            clean = preprocess(email_text)
            if len(clean.split()) < 3:
                st.warning("Email quá ngắn!")
            else:
                X = tfidf.transform([clean])
                pred = model.predict(X)[0]
                prob = model.predict_proba(X)[0].max() * 100
                if pred == 1:
                    st.markdown(f'<p class="result-phish">CẢNH BÁO: EMAIL LỪA ĐẢO!</p>', unsafe_allow_html=True)
                    st.error(f"Độ tin cậy: {prob:.2f}%")
                else:
                    st.markdown(f'<p class="result-safe">Email an toàn</p>', unsafe_allow_html=True)
                    st.success(f"Độ tin cậy: {prob:.2f}%")
    else:
        st.error("Vui lòng dán nội dung email!")

st.markdown("---")
st.caption("Đồ án tốt nghiệp 2025 – Accuracy 97.83% – Dataset CEAS_08")