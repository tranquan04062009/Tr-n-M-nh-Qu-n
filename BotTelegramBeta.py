import logging
from telegram import __version__ as TG_VER
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ChatMemberHandler
from PIL import Image, ImageDraw, ImageFont
import os

# Lấy token từ biến môi trường
my_bot_token = os.getenv('BOT_TOKEN')

# Kiểm tra nếu token không được tìm thấy
if not my_bot_token:
    raise ValueError("Bot token is missing! Please set the BOT_TOKEN environment variable.")

application = Application.builder().token(my_bot_token).build()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")

async def stylize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    if user_message is None:
        await update.message.reply_text("Please send a text message to stylize.")
        return

    img = Image.new('RGB', (500, 200), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.load_default()
    d.text((50, 90), user_message, font=fnt, fill=(255, 255, 0))

    img_path = '/tmp/styled_text.png'
    img.save(img_path)

    with open(img_path, 'rb') as photo:
        await update.message.reply_photo(photo=photo)

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_members = update.message.new_chat_members
    for member in new_members:
        await update.message.reply_text(f"Chào mừng {member.full_name} đến với nhóm!")

def main() -> None:
    application = Application.builder().token(my_bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, stylize)
    )
    application.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.MY_CHAT_MEMBER))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
