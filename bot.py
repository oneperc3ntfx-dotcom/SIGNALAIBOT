from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Signal AI sudah aktif!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
