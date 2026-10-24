import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Render Port Binding အတွက် Flask Keep-Alive Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Token နှင့် API Key များ
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client ချိန်ညှိခြင်း
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"မင်္ဂလာပါ {user_name}! ငါက သင့်ရဲ့ Daily Online Income Personal Mentor ပါ။ "
        f"ဒီနေ့ ဘာတွေ ဆွေးနွေးချင်လဲ? စကားစပြောလို့ ရပြီ ခင်ဗျား!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        if not client:
            raise ValueError("GEMINI_API_KEY ကို မတွေ့ရှိပါ သို့မဟုတ် မှားယွင်းနေပါသည်။")
        
        # Gemini API မှ စာပြန်ထုတ်ယူခြင်း
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        # Error တိတိကျကျကို Render Log မှာ မြင်ရအောင် print လုပ်ခြင်း
        print(f"=== GEMINI ERROR LOG: {e} ===")
        await update.message.reply_text(f"Error တက်သွားပါသည်:\n{str(e)[:150]}")

def main():
    # Flask ကို Thread ဖြင့် သီးသန့် Run ခြင်း
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Telegram Bot စတင်ခြင်း
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
