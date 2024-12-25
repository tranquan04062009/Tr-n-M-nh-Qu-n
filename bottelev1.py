import logging
import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from faker import Faker
from tempfile import NamedTemporaryFile
import random
import string
from bs4 import BeautifulSoup
import time

# Cấu hình logging để dễ dàng theo dõi lỗi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Lấy token từ biến môi trường
my_bot_token = os.getenv('BOT_TOKEN')

# Kiểm tra nếu token không được tìm thấy
if not my_bot_token:
    raise ValueError("Bot token is missing! Please set the BOT_TOKEN environment variable.")

# Lấy API key từ môi trường (Mailinator hoặc dịch vụ tương tự)
MAILINATOR_API_KEY = os.getenv('MAILINATOR_API_KEY')

# Tạo đối tượng Faker để sinh email ngẫu nhiên
fake = Faker()

# Hàm tạo email tạm thời
def generate_temp_email():
    """Tạo email tạm thời với tên miền giả như mailinator."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{random_string}@mailinator.com"

# Hàm tạo email và mật khẩu ngẫu nhiên
def generate_email_and_password():
    """Tạo email và mật khẩu ngẫu nhiên."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{random_string}@mailinator.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))  # Mật khẩu dài 12 ký tự
    return email, password

# Hàm lấy mã xác minh từ Mailinator
def get_verification_code(email):
    """Lấy mã xác minh từ email trong Mailinator."""
    url = f"https://api.mailinator.com/v2/domains/mailinator.com/inboxes/{email}/messages"
    headers = {"Authorization": f"Bearer {MAILINATOR_API_KEY}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        messages = response.json()
        if messages.get("messages"):
            for msg in messages["messages"]:
                # Kiểm tra nội dung email có chứa mã xác minh không
                email_content = msg["data"]["body"]
                soup = BeautifulSoup(email_content, 'html.parser')
                # Giả sử mã xác minh là một chuỗi số trong email
                verification_code = soup.find(string=lambda text: text and text.isdigit())
                if verification_code:
                    return verification_code.strip()
    return None

# Hàm lấy mã nguồn HTML của trang web
def get_source_code(url):
    """Lấy mã nguồn HTML của trang web."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Hàm xử lý lệnh /getsoucre
async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Chà, bạn quên cung cấp URL rồi! Cung cấp đường dẫn trang web cho mình nha! 🧐")
        return

    url = context.args[0]
    
    # Lấy mã nguồn HTML của trang web
    source_code = get_source_code(url)
    
    if source_code:
        # Tạo file tạm thời chứa mã nguồn HTML
        with NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
            temp_file.write(source_code.encode('utf-8'))
            temp_file.close()

            # Gửi file cho người dùng
            await update.message.reply_text(f"Đây là mã nguồn của trang web {url} 🖥️:")
            await update.message.reply_document(open(temp_file.name, 'rb'))
    else:
        await update.message.reply_text(f"Không thể lấy mã nguồn từ trang web {url}. Có thể trang web bị lỗi hoặc không tồn tại. 😢")

# Hàm xử lý lệnh /laymail10p
async def generate_temp_mail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tạo email tạm thời
    email = generate_temp_email()
    
    # Gửi email cho người dùng
    await update.message.reply_text(f"Đây là email tạm thời của bạn: {email} 📧")
    
    # Thông báo thời gian hết hạn
    await update.message.reply_text(f"Lưu ý rằng email này sẽ hết hạn sau 10 phút! ⏰")

    # Chờ 10 phút (600 giây)
    time.sleep(600)

    # Kiểm tra hộp thư của email và lấy mã xác minh nếu có
    verification_code = get_verification_code(email)
    
    if verification_code:
        await update.message.reply_text(f"Đã nhận mã xác minh từ email {email}: {verification_code} 🎯")
    else:
        await update.message.reply_text(f"Không có mã xác minh nào trong email {email}. Hãy thử lại sau! 😔")

# Hàm xử lý lệnh /taomail
async def generate_mail_and_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tạo email và mật khẩu ngẫu nhiên
    email, password = generate_email_and_password()
    
    # Gửi thông tin email và mật khẩu cho người dùng
    await update.message.reply_text(f"Đây là email và mật khẩu ngẫu nhiên của bạn:\n\nEmail: {email}\nMật khẩu: {password} 🔐")

# Hàm chính để khởi tạo và chạy bot
async def main():
    # Tạo ứng dụng bot với token lấy từ biến môi trường
    application = Application.builder().token(my_bot_token).build()
    
    # Đăng ký các lệnh /laymail10p, /getsoucre, /taomail
    application.add_handler(CommandHandler("laymail10p", generate_temp_mail))
    application.add_handler(CommandHandler("getsoucre", get_source))
    application.add_handler(CommandHandler("taomail", generate_mail_and_password))
    
    # Bắt đầu bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
