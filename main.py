import os
import logging
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"မင်္ဂလာပါ {user_name}! ငါက သင့်ရဲ့ Daily Online Income Personal Mentor ပါ။\n"
        f"ဒီနေ့ ဘာတွေ ဆွေးနွေးချင်လဲ? စကားစပြောလို့ ရပါပြီ ခင်ဗျား!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Mentor Persona System Prompt
    prompt = f"""
    You are an expert Online Business & Freelancing Mentor for Myanmar youth.
    Respond in friendly, encouraging Burmese language.
    Guide the user step-by-step to earn daily income online with zero investment.
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

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    app.add_handler(start_handler)
    app.add_handler(message_handler)
    
    print("Bot is running...")
    app.run_polling()
