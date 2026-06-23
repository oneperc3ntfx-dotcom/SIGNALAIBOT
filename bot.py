import asyncio
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import TOKEN, ADMIN_ID
from packages import PACKAGE_MAP

from storage import *
from sheet import save_member, save_trial
from scheduler import activate_user


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ref = context.args[0] if context.args else ""
    set_ref(update.message.from_user.id, ref)

    keyboard = [[InlineKeyboardButton("Saya Bersedia", callback_data="agree")]]

    await update.message.reply_text(
        "🎯 SELAMAT DATANG DI SIGNAL AI SYSTEM",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= AGREE =================
async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [
        [InlineKeyboardButton("Paket", callback_data="packages")],
        [InlineKeyboardButton("Trial 60 Menit", callback_data="trial")]
    ]

    await q.edit_message_text("Pilih:", reply_markup=InlineKeyboardMarkup(keyboard))


# ================= PACKAGES =================
async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    buttons = []
    for k, v in PACKAGE_MAP.items():
        buttons.append([
            InlineKeyboardButton(f"{v['label']} - {v['price']}", callback_data=f"buy_{k}")
        ])

    await q.edit_message_text("Pilih paket:", reply_markup=InlineKeyboardMarkup(buttons))


# ================= BUY =================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    key = q.data.replace("buy_", "")
    package = PACKAGE_MAP[key]

    set_pending_payment(q.from_user.id, {
        "package": key,
        "username": q.from_user.username,
        "ref": get_ref(q.from_user.id)
    })

    await q.edit_message_text(
        f"💰 {package['label']}\n💳 Transfer lalu kirim bukti."
    )


# ================= TRIAL =================
async def trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user = q.from_user

    if has_used_trial(user.id):
        await q.edit_message_text("Sudah pakai trial.")
        return

    expire = datetime.now() + timedelta(minutes=60)

    save_trial({
        "user_id": user.id,
        "username": user.username,
        "claim_at": str(datetime.now()),
        "expire_at": str(expire),
        "status": "ACTIVE",
        "ref": get_ref(user.id)
    })

    mark_trial_used(user.id)

    await q.edit_message_text("Trial aktif 60 menit")


# ================= PHOTO =================
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    pending = get_pending_payment(user.id)

    if not pending:
        return await update.message.reply_text("Tidak ada transaksi")

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""
BUKTI BAYAR
User: {user.id}
Package: {pending['package']}
"""
    )

    await update.message.reply_text("Menunggu approval admin")


# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(agree, pattern="agree"))
    app.add_handler(CallbackQueryHandler(show_packages, pattern="packages"))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy_"))
    app.add_handler(CallbackQueryHandler(trial, pattern="trial"))

    app.add_handler(MessageHandler(filters.PHOTO, photo))

    print("BOT RUNNING")
    app.run_polling()


if __name__ == "__main__":
    main()
