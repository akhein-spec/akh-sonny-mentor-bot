import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Fetch Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# --- Flask Web Server for Render Port Binding ---
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is running and alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app_flask.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
# ------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"မင်္ဂလာပါ {user_name}! ငါက သင့်ရဲ့ Daily Online Income Personal Mentor ပါ။\nဒီနေ့ ဘာတွေ ဆွေးနွေးချင်လဲ? စကားစပြောလို့ ရပြီ ခင်ဗျား!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    prompt = f"""
    You are an expert Online Business & Freelancing Mentor.
    Respond in friendly, encouraging Burmese.
    Guide the user step-by-step to earn daily online income.
    User Message: {user_text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("တောင်းပန်ပါတယ်၊ အမှားတစ်ခု ဖြစ်သွားလို့ပါ။ နောက်တစ်ကြိမ် ပြန်ကြိုးစားကြည့်ပေးပါနော်။")

def main():
    # Start Flask server first to satisfy Render port binding
    keep_alive()
    
    # Build Telegram Bot
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)

    app.add_handler(start_handler)
    app.add_handler(message_handler)

    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
