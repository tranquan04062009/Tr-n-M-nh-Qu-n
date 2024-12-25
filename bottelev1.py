import logging
import requests
import os
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from tempfile import NamedTemporaryFile

# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Lấy token từ biến môi trường
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

if not BOT_TOKEN:
    raise ValueError("Bot token is missing! Please set the BOT_TOKEN environment variable.")

# Hàm tạo email và mật khẩu ngẫu nhiên
def generate_email_and_password():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com"])
    email = f"{random_string}@{domain}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return email, password

# Hàm lấy mã nguồn HTML
def get_source_code(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching source code from {url}: {e}")
        return None

# Lệnh /getsoucre
async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Hãy cung cấp URL để lấy mã nguồn! 🧐")
        return

    url = context.args[0]
    source_code = get_source_code(url)

    if source_code:
        with NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
            temp_file.write(source_code.encode('utf-8'))
            temp_file.close()
            await update.message.reply_document(open(temp_file.name, 'rb'))
    else:
        await update.message.reply_text(f"Không thể lấy mã nguồn từ {url}. 🛑")

# Lệnh /taomail
async def generate_mail_and_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email, password = generate_email_and_password()
    await update.message.reply_text(f"Email: {email}\nMật khẩu: {password} 🔐")

# Lệnh /randomfact
async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "Một con voi có thể nghe được tiếng con voi khác từ xa hơn 5km!",
        "Con người và chim có bộ xương tương tự nhau!",
        "Cơ thể con người chứa 60% nước!",
        "Cây bách hương có thể sống đến 3.000 năm tuổi."
    ]
    await update.message.reply_text(f"Sự thật ngẫu nhiên: {random.choice(facts)} 🤓")

# Lệnh /weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Hãy cung cấp tên thành phố! 🌤️")
        return

    city = " ".join(context.args)
    if not OPENWEATHERMAP_API_KEY:
        await update.message.reply_text("API Key OpenWeatherMap chưa được cấu hình! 🌧️")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=vi"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('cod') == 200:
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            await update.message.reply_text(
                f"Thời tiết tại {city}:\n- Nhiệt độ: {temp}°C\n- Độ ẩm: {humidity}%\n- Mô tả: {weather_desc.capitalize()} 🌞"
            )
        else:
            await update.message.reply_text(f"Không tìm thấy thông tin thời tiết cho {city}. ❌")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data for {city}: {e}")
        await update.message.reply_text(f"Lỗi khi lấy dữ liệu thời tiết cho {city}. 🛑")

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
    Lệnh khả dụng:
    /getsoucre <url> - Lấy mã nguồn HTML.
    /taomail - Tạo email & mật khẩu ngẫu nhiên.
    /randomfact - Sự thật ngẫu nhiên.
    /weather <city> - Kiểm tra thời tiết.
    /help - Hướng dẫn sử dụng.
    """)

# Hàm chính
async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("getsoucre", get_source))
    application.add_handler(CommandHandler("taomail", generate_mail_and_password))
    application.add_handler(CommandHandler("randomfact", random_fact))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("help", help_command))

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
