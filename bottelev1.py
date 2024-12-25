import logging
import os
import random
import string
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from tempfile import NamedTemporaryFile

# Cấu hình logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Lấy token từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Bot token is missing! Please set the BOT_TOKEN environment variable.")

# Hàm tạo email và mật khẩu ngẫu nhiên
def generate_email_and_password():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com"])
    email = f"{random_string}@{domain}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return email, password

# Hàm lấy mã nguồn HTML của trang web
def get_source_code(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Lệnh /getsoucre
async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Bạn quên cung cấp URL! Hãy gửi đường dẫn trang web.")
        return

    url = context.args[0]
    source_code = get_source_code(url)

    if source_code:
        with NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
            temp_file.write(source_code.encode("utf-8"))
            temp_file.close()
            await update.message.reply_document(open(temp_file.name, "rb"))
    else:
        await update.message.reply_text(f"Không thể lấy mã nguồn từ {url}.")

# Lệnh /taomail
async def generate_mail_and_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email, password = generate_email_and_password()
    await update.message.reply_text(f"Email: {email}\nMật khẩu: {password}")

# Lệnh /randomfact
async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "Một con voi có thể nghe tiếng kêu từ xa hơn 5km!",
        "Tất cả loài chim đều có xương sống.",
        "Con người và loài chim có bộ xương tương tự nhau.",
        "60% cơ thể con người là nước.",
        "Cây bách hương có thể sống đến 3.000 năm."
    ]
    fact = random.choice(facts)
    await update.message.reply_text(f"Sự thật ngẫu nhiên: {fact}")

# Lệnh /weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Vui lòng cung cấp tên thành phố!")
        return

    city = " ".join(context.args)
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")

    if not api_key:
        await update.message.reply_text("API key chưa được cấu hình!")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=vi"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("cod") == 200:
            weather_data = data["weather"][0]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            weather_desc = weather_data["description"]
            weather_message = f"Thời tiết tại {city}:\n- Nhiệt độ: {temp}°C\n- Độ ẩm: {humidity}%\n- Mô tả: {weather_desc.capitalize()}"
            await update.message.reply_text(weather_message)
        else:
            await update.message.reply_text(f"Không thể lấy thông tin thời tiết cho {city}.")
    else:
        await update.message.reply_text(f"Không thể lấy dữ liệu thời tiết từ OpenWeatherMap.")

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Các lệnh có sẵn:
    /getsoucre <url> - Lấy mã nguồn HTML.
    /taomail - Tạo email và mật khẩu.
    /randomfact - Sự thật ngẫu nhiên.
    /weather <city> - Kiểm tra thời tiết.
    /help - Hướng dẫn.
    """
    await update.message.reply_text(help_text)

# Hàm chính để khởi chạy bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Đăng ký lệnh
    application.add_handler(CommandHandler("getsoucre", get_source))
    application.add_handler(CommandHandler("taomail", generate_mail_and_password))
    application.add_handler(CommandHandler("randomfact", random_fact))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("help", help_command))

    # Chạy bot
    application.run_polling()

if __name__ == "__main__":
    main()
