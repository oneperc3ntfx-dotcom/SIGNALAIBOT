import asyncio
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import TOKEN, ADMIN_ID
from config.packages import PACKAGE_MAP

from storage import (
    set_ref,
    get_ref,
    set_pending_payment,
    get_pending_payment,
    clear_pending_payment,
    mark_trial_used,
    has_used_trial
)

from sheet import save_member, save_trial
from scheduler import activate_user


# =========================
# START + REFERRAL + LANDING
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    ref = context.args[0] if context.args else ""
    set_ref(user.id, ref)

    caption = """
🎯 SELAMAT DATANG DI SIGNAL AI SYSTEM

Halo 👋

📊 CONTOH SIGNAL AI TOOLS SYSTEM

📊 XAUUSD SIGNAL

🕒 2026-06-22 23:00:00 WIB

📈 BIAS: BUY

📌 ENTRY: BUY LIMIT @ 4182.53

🎯 TP1: 4189.53
🎯 TP2: 4197.53
⛔️ SL : 4177.53

💡 Klik tombol di bawah jika sudah memahami.
"""

    keyboard = [
        [InlineKeyboardButton("Saya Bersedia Bergabung", callback_data="agree")]
    ]

    await update.message.reply_photo(
        photo=open("assets/signal_ai.png", "rb"),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# AGREE BUTTON
# =========================
async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📦 Pilih Paket", callback_data="packages")],
        [InlineKeyboardButton("🆓 Trial 60 Menit", callback_data="trial")]
    ]

    await query.edit_message_text(
        "Silahkan pilih:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# SHOW PACKAGES
# =========================
async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = []

    for key, p in PACKAGE_MAP.items():
        buttons.append([
            InlineKeyboardButton(
                f"{p['label']} - Rp {p['price']}",
                callback_data=f"buy_{key}"
            )
        ])

    await query.edit_message_text(
        "📦 Pilih Paket:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================
# BUY PACKAGE
# =========================
async def buy_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    key = query.data.replace("buy_", "")
    package = PACKAGE_MAP[key]

    user = query.from_user

    set_pending_payment(user.id, {
        "package": key,
        "username": user.username,
        "ref": get_ref(user.id)
    })

    text = f"""
💰 Paket: {package['label']}
💵 Harga: Rp {package['price']}

🏦 BANK SMBC
👤 a/n Yuriandi Arma
💳 90240573080

🏦 CIMB NIAGA
💳 708420455200

📸 Kirim bukti transfer setelah pembayaran.
"""

    await query.edit_message_text(text)


# =========================
# TRIAL SYSTEM
# =========================
async def trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    if has_used_trial(user.id):
        await query.edit_message_text("❌ Kamu sudah pernah menggunakan trial.")
        return

    expire_at = datetime.now() + timedelta(minutes=60)

    save_trial({
        "user_id": user.id,
        "username": user.username,
        "claim_at": str(datetime.now()),
        "expire_at": str(expire_at),
        "status": "ACTIVE",
        "ref": get_ref(user.id)
    })

    mark_trial_used(user.id)

    await query.edit_message_text("⏳ Trial aktif 60 menit.")


# =========================
# HANDLE BUKTI TRANSFER
# =========================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1].file_id

    pending = get_pending_payment(user.id)

    if not pending:
        await update.message.reply_text("❌ Kamu belum memilih paket.")
        return

    context.user_data[user.id] = {
        "photo": photo,
        "pending": pending
    }

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"""
📥 BUKTI PEMBAYARAN

User ID: {user.id}
Username: @{user.username}
Package: {pending['package']}
Ref: {pending.get('ref')}
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("📩 Bukti diterima, menunggu admin.")


# =========================
# ADMIN APPROVE / REJECT
# =========================
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    data = context.user_data.get(user_id)

    if not data:
        await query.edit_message_text("Data tidak ditemukan.")
        return

    pending = data["pending"]
    package_key = pending["package"]

    # EXPIRY
    if package_key == "trial":
        expire_at = datetime.now() + timedelta(minutes=60)
    else:
        map_days = {
            "1bulan": 30,
            "6bulan": 180,
            "12bulan": 365,
            "permanent": None
        }
        days = map_days.get(package_key)
        expire_at = None if days is None else datetime.now() + timedelta(days=days)

    # APPROVE
    if action == "approve":

        save_member({
            "user_id": user_id,
            "username": pending["username"],
            "package": package_key,
            "price": PACKAGE_MAP[package_key]["price"],
            "status": "ACTIVE",
            "expire_at": str(expire_at),
            "kicked_at": "",
            "invited": "YES",
            "ref": pending.get("ref")
        })

        activate_user(user_id, expire_at)
        clear_pending_payment(user_id)

        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 WELCOME SIGNAL AI\nAkses kamu sudah aktif!"
        )

        await query.edit_message_text("✅ APPROVED")

    # REJECT
    elif action == "reject":

        clear_pending_payment(user_id)

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Pembayaran ditolak. Hubungi admin @ADMOnePercentsFX"
        )

        await query.edit_message_text("❌ REJECTED")


# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(agree, pattern="agree"))
    app.add_handler(CallbackQueryHandler(show_packages, pattern="packages"))
    app.add_handler(CallbackQueryHandler(buy_package, pattern="buy_"))
    app.add_handler(CallbackQueryHandler(trial, pattern="trial"))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(admin_action, pattern="approve_"))
    app.add_handler(CallbackQueryHandler(admin_action, pattern="reject_"))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
