# gmail_helper.py - PHIÊN BẢN NÂNG CẤP (FULL BODY)
import streamlit as st
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service_auto():
    """
    Tự động bật trình duyệt, đăng nhập và trả về service.
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            SCOPES
        )
        
        # run_local_server sẽ tự mở trình duyệt. 
        # Nếu muốn copy link thủ công thì thêm open_browser=False
        creds = flow.run_local_server(
            port=8080, 
            open_browser=True, # Đặt True để tự mở, False để copy link
            authorization_prompt_message=""
        )
        return creds
    except Exception as e:
        print(f"Lỗi login: {e}")
        return None

# === HÀM MỚI 1: GIẢI MÃ BASE64 ===
def clean_body(data):
    """Giải mã dữ liệu từ định dạng Base64 URL-safe của Gmail"""
    try:
        # Chuẩn hóa ký tự thay thế
        clean_data = data.replace("-", "+").replace("_", "/")
        # Giải mã ra bytes
        decoded_bytes = base64.b64decode(clean_data)
        # Chuyển bytes thành string (UTF-8)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return ""

# === HÀM MỚI 2: ĐỆ QUY TÌM NỘI DUNG ===
def get_email_content(payload):
    """
    Duyệt cây cấu trúc email để tìm phần văn bản (text/plain).
    """
    body = ""
    
    # Trường hợp A: Email đơn giản (không đính kèm, không chia phần)
    if 'body' in payload and 'data' in payload['body']:
        return clean_body(payload['body']['data'])
    
    # Trường hợp B: Email phức tạp (Multipart - Chứa nhiều phần lồng nhau)
    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType')
            
            # Ưu tiên số 1: Lấy văn bản thuần (text/plain)
            # Đây là dạng tốt nhất cho AI xử lý
            if mime_type == 'text/plain':
                if 'data' in part['body']:
                    return clean_body(part['body']['data'])
            
            # Ưu tiên số 2: Nếu là hộp chứa (multipart), đi sâu vào trong (Đệ quy)
            elif mime_type == 'multipart/alternative' or mime_type == 'multipart/mixed':
                found_text = get_email_content(part)
                if found_text: # Nếu tìm thấy text bên trong thì trả về ngay
                    return found_text
                    
    return body

def fetch_emails(credentials, num_emails=10):
    try:
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().messages().list(userId='me', maxResults=num_emails).execute()
        messages = results.get('messages', [])
        
        email_data = []
        for msg in messages:
            # Lấy toàn bộ dữ liệu email (format='full')
            txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            payload = txt.get('payload', {})
            headers = payload.get('headers', [])
            
            # Lấy Subject
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(Không tiêu đề)")
            
            # Lấy Snippet (Dự phòng)
            snippet = txt.get('snippet', "")
            
            # --- GỌI HÀM LẤY FULL BODY ---
            full_body = get_email_content(payload)
            
            # Nếu vì lý do gì đó mà full_body rỗng (ví dụ chỉ có ảnh), dùng tạm snippet
            if not full_body or not full_body.strip():
                full_body = snippet

            email_data.append({
                "id": msg['id'],
                "subject": subject,
                "body": full_body # Đã chứa toàn bộ nội dung giải mã
            })
        return email_data
    except Exception as e:
        st.error(f"Lỗi khi lấy email: {e}")
        return []