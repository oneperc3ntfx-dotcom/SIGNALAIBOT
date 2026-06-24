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

        "Mohon luangkan waktu sejenak untuk membaca "
        "informasi pada gambar di atas agar Anda memahami "
        "cara kerja layanan kami dan dapat menggunakan signal "
        "dengan lebih optimal.\n\n"

        "<b>📊 CONTOH SIGNAL PREMIUM</b>\n\n"

        f"{signal_example()}\n"

        "<b>✨ Keuntungan Member Premium</b>\n\n"

        "✅ Signal harian berkualitas\n"
        "✅ Analisa market berbasis AI\n"
        "✅ Update market secara berkala\n"
        "✅ Akses grup member eksklusif\n"
        "✅ Support dan edukasi trading\n\n"

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


# ================= JOIN (TOMBOL HILANG) =================
@dp.callback_query(F.data == "join")
async def join(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💎 1 BULAN • Rp199K",
                    callback_data="pkg_1bulan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 6 BULAN • Rp549K",
                    callback_data="pkg_6bulan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 12 BULAN • Rp999K",
                    callback_data="pkg_12bulan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 PERMANENT • Rp1.999K",
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


# ================= PACKAGE (TOMBOL HILANG) =================
@dp.callback_query(F.data.startswith("pkg_"))
async def select_package(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    package = callback.data.replace("pkg_", "")

    user_packages[callback.from_user.id] = package

    data = PACKAGE_MAP[package]

    text = (
        f"💎 <b>Paket:</b> {data['label']}\n"
        f"💰 <b>Biaya:</b> Rp {data['price']:,}\n\n"

        f"{BANK_INFO}\n\n"

        "━━━━━━━━━━━━\n\n"

        "📸 Setelah melakukan pembayaran, "
        "silakan kirim bukti transfer ke chat ini.\n\n"

        "⏳ Tim kami akan segera melakukan verifikasi pembayaran Anda."
    )

    await callback.message.answer(text, parse_mode="HTML")
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
        "✅ <b>Bukti transfer berhasil diterima.</b>\n\n"
        "Silakan klik tombol di bawah untuk mengirim "
        "permintaan verifikasi kepada admin.\n\n"
        "⏳ Proses verifikasi biasanya hanya memerlukan beberapa menit.",
        reply_markup=kb,
        parse_mode="HTML"
    )


# ================= CONFIRM (TOMBOL HILANG) =================
@dp.callback_query(F.data == "confirm_transfer")
async def confirm_transfer(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    user = callback.from_user

    package_key = user_packages.get(user.id)

    if not package_key:
        await callback.answer("Silakan pilih paket terlebih dahulu.", show_alert=True)
        return

    proof = user_proofs.get(user.id)

    if not proof:
        await callback.answer("Bukti transfer belum ditemukan.", show_alert=True)
        return

    data = PACKAGE_MAP[package_key]

    username = f"@{user.username}" if user.username else "Tidak ada username"

    admin_text = (
        "🔔 <b>PERMINTAAN VERIFIKASI PEMBAYARAN</b>\n\n"
        f"👤 <b>Username:</b> {username}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n\n"
        f"📦 <b>Paket:</b> {data['label']}\n"
        f"💰 <b>Nominal:</b> Rp {data['price']:,}\n\n"
        "📸 Bukti transfer terlampir di atas.\n\n"
        "Silakan lakukan verifikasi pembayaran dan pilih tindakan di bawah."
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
        ADMIN_ID,
        photo=proof,
        caption=admin_text,
        reply_markup=kb,
        parse_mode="HTML"
    )

    await callback.message.answer(
        "✅ Permintaan verifikasi berhasil dikirim ke admin.\n\n"
        "Mohon tunggu proses pengecekan pembayaran.",
        parse_mode="HTML"
    )

    await callback.answer()


# ================= APPROVE (TOMBOL HILANG) =================
@dp.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    user_id = int(callback.data.split("_")[1])

    invite = await bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        member_limit=1
    )

    await bot.send_message(
        user_id,
        f"""
🎉 <b>Pembayaran Berhasil Diverifikasi</b>

Selamat! Akun Anda telah berhasil diaktifkan sebagai member premium.

🔗 Silakan bergabung ke grup eksklusif melalui tautan berikut:

{invite.invite_link}

📈 Selamat trading dan semoga profit konsisten!

Terima kasih telah bergabung bersama Signal AI Premium 🚀
""",
        parse_mode="HTML"
    )

    await callback.message.answer("✅ User berhasil diapprove.")
    await callback.answer()


# ================= REJECT (TOMBOL HILANG) =================
@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):

    await callback.message.edit_reply_markup(reply_markup=None)

    user_id = int(callback.data.split("_")[1])

    await bot.send_message(
        user_id,
        """
❌ <b>Pembayaran Belum Dapat Diverifikasi</b>

Mohon maaf, pembayaran Anda belum dapat kami konfirmasi.

Silakan periksa kembali bukti transfer yang dikirim atau hubungi admin untuk bantuan lebih lanjut.

🙏 Terima kasih atas pengertiannya.
""",
        parse_mode="HTML"
    )

    await callback.message.answer("❌ User berhasil ditolak.")
    await callback.answer()


# ================= MAIN =================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
