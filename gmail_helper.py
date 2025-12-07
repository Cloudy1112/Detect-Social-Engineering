# gmail_helper.py
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service_auto():
    """
    Tự động bật trình duyệt, đăng nhập và trả về service.
    Không cần copy paste code.
    """
    try:
        # Cấu hình Flow cho Web Application
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            SCOPES
        )
        
        # Hàm này sẽ:
        # 1. Tự mở trình duyệt
        # 2. Chờ người dùng login
        # 3. Tự đóng trình duyệt và lấy token
        # Lưu ý: Port phải khớp với cái đã khai báo trên Google Cloud (8080)
        creds = flow.run_local_server(port=8080)
        
        
        return creds
    except Exception as e:
        print(f"Lỗi login: {e}")
        return None

def fetch_emails(credentials, num_emails=10):
    # (Hàm này giữ nguyên như cũ không thay đổi)
    try:
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().messages().list(userId='me', maxResults=num_emails).execute()
        messages = results.get('messages', [])
        
        email_data = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = txt['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(Không tiêu đề)")
            snippet = txt.get('snippet', "")
            email_data.append({"id": msg['id'], "subject": subject, "body": snippet})
        return email_data
    except Exception as e:
        return []