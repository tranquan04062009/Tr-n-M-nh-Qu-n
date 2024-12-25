import logging
import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from tempfile import NamedTemporaryFile
import random
import string

# Cấu hình logging để dễ dàng theo dõi lỗi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Lấy token từ biến môi trường
my_bot_token = os.getenv('BOT_TOKEN')

# Kiểm tra nếu token không được tìm thấy
if not my_bot_token:
    raise ValueError("Bot token is missing! Please set the BOT_TOKEN environment variable.")

# Hàm tạo email và mật khẩu ngẫu nhiên
def generate_email_and_password():
    """Tạo email và mật khẩu ngẫu nhiên."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com"])  # Chọn ngẫu nhiên một domain từ danh sách
    email = f"{random_string}@{domain}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))  # Mật khẩu dài 12 ký tự
    return email, password

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

# Hàm xử lý lệnh /taomail
async def generate_mail_and_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tạo email và mật khẩu ngẫu nhiên
    email, password = generate_email_and_password()
    
    # Gửi thông tin email và mật khẩu cho người dùng
    await update.message.reply_text(f"Đây là email và mật khẩu ngẫu nhiên của bạn:\n\nEmail: {email}\nMật khẩu: {password} 🔐")

# Tính năng mới: Cung cấp sự thật ngẫu nhiên
async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "Một con voi có thể nghe được tiếng con voi khác kêu từ xa hơn 5km!",
        "Tất cả các loài chim có xương sống, không chỉ là các loài biết bay.",
        "Con người và loài chim đều có bộ xương giống nhau trong cấu trúc cơ bản!",
        "Có khoảng 60% nước trong cơ thể con người, giúp duy trì các chức năng cơ thể.",
        "Cây bách hương có thể sống đến 3.000 năm tuổi."
    ]
    fact = random.choice(facts)
    await update.message.reply_text(f"Sự thật ngẫu nhiên: {fact} 🤓")

# Tính năng mới: Kiểm tra thời tiết của thành phố (Sử dụng OpenWeatherMap API)
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Vui lòng cung cấp tên thành phố để kiểm tra thời tiết! 🌤️")
        return

    city = " ".join(context.args)
    
    # API của OpenWeatherMap
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')
    
    if not api_key:
        await update.message.reply_text("API key cho OpenWeatherMap chưa được cấu hình! 🌧️")
        return
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=vi"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('cod') == 200:
            weather_data = data['weather'][0]
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            weather_desc = weather_data['description']
            
            weather_message = f"Thời tiết tại {city}:\n- Nhiệt độ: {temp}°C\n- Độ ẩm: {humidity}%\n- Mô tả: {weather_desc.capitalize()}"
            await update.message.reply_text(weather_message)
        else:
            await update.message.reply_text(f"Không thể lấy thông tin thời tiết cho {city}. Kiểm tra lại tên thành phố và thử lại. ❌")
    else:
        await update.message.reply_text(f"Không thể lấy dữ liệu thời tiết từ OpenWeatherMap. ❌")

# Tính năng mới: Lệnh /help để hướng dẫn sử dụng
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Các lệnh có sẵn của bot:
    
    /getsoucre <url> - Lấy mã nguồn HTML của trang web.
    /taomail - Tạo email và mật khẩu ngẫu nhiên.
    /randomfact - Cung cấp sự thật ngẫu nhiên.
    /weather <city> - Kiểm tra thời tiết của thành phố.
    /help - Xem hướng dẫn về các lệnh.
    """
    await update.message.reply_text(help_text)

# Hàm chính để khởi tạo và chạy bot
async def main():
    # Tạo ứng dụng bot với token lấy từ biến môi trường
    application = Application.builder().token(my_bot_token).build()
    
    # Đăng ký các lệnh
    application.add_handler(CommandHandler("getsoucre", get_source))
    application.add_handler(CommandHandler("taomail", generate_mail_and_password))
    application.add_handler(CommandHandler("randomfact", random_fact))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("help", help_command))
    
    # Bắt đầu bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
