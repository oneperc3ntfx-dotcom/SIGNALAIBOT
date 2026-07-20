import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import BOT_TOKEN, ADMIN_ID, GROUP_ID, BANK_INFO
from packages import PACKAGE_MAP

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_packages = {}
user_proofs = {}

# ================= TAMBAHAN: REFERRAL =================
user_referral = {}

# ================= TAMBAHAN: BROADCAST GROUP =================
BROADCAST_GROUP_ID = -1004311537613

# ================= GROUP VERIFIKASI =================
PAYMENT_GROUP_ID = -1001234567890

def signal_example():
    return """
<blockquote>
📊 XAUUSD SIGNAL

🕒 22 Juni 2026 • 23:00 WIB

📈 BIAS : BUY

📌 ENTRY : BUY LIMIT @ 4182.53

🎯 TAKE PROFIT
• TP1 : 4189.53
• TP2 : 4197.53

⛔ STOP LOSS
• SL : 4177.53

🧠 ANALISA
• Bullish Liquidity Sweep
• Bullish Reversal Confirmation
• Momentum Shift Up

━━━━━━━━━━━━
⚠️ Gunakan manajemen risiko yang baik pada setiap transaksi.
</blockquote>
"""


# ================= START =================
@dp.message(Command("start"))
async def start(message: Message):

    ref = None
    if message.text and len(message.text.split()) > 1:
        ref = message.text.split()[1]

    if ref:
        user_referral[message.from_user.id] = ref

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 SAYA SIAP BERGABUNG",
                    callback_data="join"
                )
            ]
        ]
    )

    text = (
        "<b>🎯 SELAMAT DATANG DI SIGNAL AI SYSTEM</b>\n\n"
        "Halo 👋\n\n"
        "Terima kasih telah mengunjungi layanan "
        "<b>Signal AI Premium</b>.\n\n"
        "<b>📊 CONTOH SIGNAL PREMIUM</b>\n\n"
        f"{signal_example()}\n\n"
        "<b>✨ Keuntungan Member Premium</b>\n\n"
        "✅ Signal harian berbasi AI\n"
        "✅ Analisa market berbasis AI\n"
        "✅ Update market secara berkala\n"
        "✅ Akses grup member eksklusif\n"
        "✅ Info NEWS XAUUSD\n\n"
        "💡 Jika Anda sudah memahami layanan ini dan siap "
        "bergabung bersama member premium kami, "
        "silakan klik tombol di bawah."
    )

    try:
        photo = FSInputFile("assets/signal_ai.jpg")

        await message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=kb,
            parse_mode="HTML"
        )

    except Exception as e:
        print("Photo error:", e)

        await message.answer(
            text,
            reply_markup=kb,
            parse_mode="HTML"
        )


# ================= JOIN =================
@dp.callback_query(F.data == "join")
async def join(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📅 1 Hari • Rp50.000",
                callback_data="pkg_1day"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 7 Hari • Rp150.000",
                callback_data="pkg_7day"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 1 Bulan • Rp250.000",
                callback_data="pkg_1month"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 6 Bulan • Rp500.000",
                callback_data="pkg_6month"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 12 Bulan • Rp750.000",
                callback_data="pkg_12month"
            )
        ],
        [
            InlineKeyboardButton(
                text="👑 Permanent • Rp1.500.000",
                callback_data="pkg_permanent"
            )
        ]
    ]
)
    await callback.message.answer(
        "<b>💰 PILIH PAKET LANGGANAN SIGNAL AI PREMIUM</b>\n\n"
        "Silakan pilih paket yang sesuai dengan kebutuhan Anda.",
        reply_markup=kb,
        parse_mode="HTML"
    )

    await callback.answer()


# ================= PACKAGE =================
# ================= PACKAGE =================
@dp.callback_query(F.data.startswith("pkg_"))
async def select_package(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    package = callback.data.replace("pkg_", "")

    user_packages[callback.from_user.id] = package

    data = PACKAGE_MAP[package]

    qris = FSInputFile("assets/qris.jpg")

    caption = (
        f"💎 <b>Paket:</b> {data['label']}\n"
        f"💰 <b>Harga:</b> Rp {data['price']:,}\n\n"
        "📱 Silakan lakukan pembayaran dengan melakukan scan pada kode QR di atas.\n\n"
        "⚠️ Pastikan nominal pembayaran sesuai dengan harga paket yang dipilih.\n\n"
        "📸 Setelah pembayaran berhasil, kirim bukti pembayaran (screenshot atau foto) ke chat ini."
    )

    await callback.message.answer_photo(
        photo=qris,
        caption=caption,
        parse_mode="HTML"
    )

    await callback.answer()

# ================= PROOF =================
@dp.message(F.photo)
async def receive_proof(message: Message):

    user_proofs[message.from_user.id] = message.photo[-1].file_id

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ SAYA SUDAH TRANSFER",
                    callback_data="confirm_transfer"
                )
            ]
        ]
    )

    await message.answer(
        "✅ <b>Bukti diterima.</b>\nTekan tombol (SAYA SUDAH TRANSFER) di bawah untuk verifikasi.",
        reply_markup=kb,
        parse_mode="HTML"
    )


# ================= CONFIRM =================
@dp.callback_query(F.data == "confirm_transfer")
async def confirm_transfer(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    user = callback.from_user

    package_key = user_packages.get(user.id)

    if not package_key:
        await callback.answer("Pilih paket dulu.", show_alert=True)
        return

    proof = user_proofs.get(user.id)

    if not proof:
        await callback.answer("Bukti tidak ditemukan.", show_alert=True)
        return

    data = PACKAGE_MAP[package_key]

    username = f"@{user.username}" if user.username else "Tidak ada username"

    ref = user_referral.get(user.id, "Tidak ada")

    admin_text = (
        "🔔 <b>VERIFIKASI PEMBAYARAN</b>\n\n"
        f"👤 Username: {username}\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"📦 Paket: {data['label']}\n"
        f"💰 Nominal: Rp {data['price']:,}\n"
        f"🔗 Referral: {ref}\n"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ TERIMA", callback_data=f"approve_{user.id}"),
                InlineKeyboardButton(text="❌ TOLAK", callback_data=f"reject_{user.id}")
            ]
        ]
    )

    await bot.send_photo(
        PAYMENT_GROUP_ID,
        photo=proof,
        caption=admin_text,
        reply_markup=kb,
        parse_mode="HTML"
    )

    await callback.message.answer("⏳ Menunggu verifikasi admin...")
    await callback.answer()


# ================= APPROVE =================
@dp.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    user_id = int(callback.data.split("_")[1])

    invite = await bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        member_limit=1
    )

    user = await bot.get_chat(user_id)
    admin_name = callback.from_user.full_name
    username = f"@{user.username}" if user.username else "Tidak ada username"

    ref = user_referral.get(user_id, "Tidak ada")
    package = user_packages.get(user_id, "Unknown")

    # ================= FIX TAMBAHAN (INI YANG KURANG) =================
    data = PACKAGE_MAP.get(package, {})
    label = data.get("label", package)
    price = data.get("price", 0)

    text_success = (
    "🎉 <b>SUCCESS JOIN TO GROUP</b>\n\n"
    f"👤 Username: {username}\n"
    f"🆔 User ID: {user_id}\n"
    f"📦 Paket: {label}\n"
    f"💰 Harga: Rp {price:,}\n"
    f"⏳ Durasi: {label}\n"
    f"🔗 Referral: {ref}\n\n"

    "━━━━━━━━━━━━━━━━━━━━\n\n"

    "🔗 <b>Invite Link (1x Pakai)</b>\n"
    f"{invite.invite_link}\n\n"

    "━━━━━━━━━━━━━━━━━━━━\n\n"

    "🏆 <b>Broker yang Kami Sarankan</b>\n\n"

    "Kami menyarankan menggunakan broker <b>FXGT-IDN</b> karena "
    "perhitungan harga, ratio, dan spread memiliki kesamaan dengan "
    "broker yang kami gunakan untuk analisa dan backtest signal.\n\n"

    "Apabila Anda menggunakan broker lain, terdapat kemungkinan "
    "harga Entry, Take Profit (TP), maupun Stop Loss (SL) sedikit "
    "berbeda dari hasil backtest kami.\n\n"
    "Kunjungi Website Resmi nya di Browser atau google FXGT-IDN.COM"
    "🌐 https://fxgt-idn.com"
)

    # ================= USER =================
    await bot.send_message(user_id, text_success, parse_mode="HTML")

    # ================= ADMIN =================
    await bot.send_message(ADMIN_ID, text_success, parse_mode="HTML")

    # ================= GROUP BROADCAST =================
    await bot.send_message(BROADCAST_GROUP_ID, text_success, parse_mode="HTML")

    await callback.message.answer(
        f"✅ Disetujui oleh : {admin_name}"
)

    await callback.answer()


# ================= REJECT =================
@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    user_id = int(callback.data.split("_")[1])

    await bot.send_message(
        user_id,
        "❌ Pembayaran ditolak. Hubungi admin -> @ADMOnePercentsFX ",
        parse_mode="HTML"
    )

    admin_name = callback.from_user.full_name

    await callback.message.answer(
        f"❌ Ditolak oleh : {admin_name}"
)
    
    await callback.answer()


# ================= MAIN =================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
