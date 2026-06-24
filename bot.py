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
📊 XAUUSD SIGNAL

🕒 2026-06-22 23:00:00 WIB

📈 BIAS: BUY

📌 ENTRY: BUY LIMIT @ 4182.53

🎯 TP1: 4189.53
🎯 TP2: 4197.53
⛔️ SL : 4177.53

🧠 REASON:
- Liquidity sweep bullish
- Bullish reversal
- Momentum shift up

━━━━━━━━━━━━
"""


@dp.message(Command("start"))
async def start(message: Message):

    photo = FSInputFile("assets/signal_ai.jpg")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 SAYA BERSEDIA BERGABUNG",
                    callback_data="join"
                )
            ]
        ]
    )

    text = (
        "🎯 SELAMAT DATANG DI SIGNAL AI SYSTEM\n\n"
        "Halo 👋\n\n"
        "Mohon Di baca Gambar Diatas Sebelum Bergabung\n\n"
        "📊 CONTOH SIGNAL AI TOOLS SYSTEM\n\n"
        f"{signal_example()}\n"
        "💡 Silahkan Klik Tombol Di bawah , jika sudah Memahami."
    )

    await message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=kb
    )


@dp.callback_query(F.data == "join")
async def join(callback: CallbackQuery):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="1 BULAN - 199K",
                    callback_data="pkg_1bulan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="6 BULAN - 549K",
                    callback_data="pkg_6bulan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="12 BULAN - 999K",
                    callback_data="pkg_12bulan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="PERMANENT - 1.999K",
                    callback_data="pkg_permanent"
                )
            ]
        ]
    )

    await callback.message.answer(
        "💰 Pilih Paket Langganan",
        reply_markup=kb
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("pkg_"))
async def select_package(callback: CallbackQuery):

    package = callback.data.replace("pkg_", "")

    user_packages[callback.from_user.id] = package

    data = PACKAGE_MAP[package]

    text = (
        f"💰 Paket: {data['label']}\n"
        f"💵 Harga: Rp {data['price']:,}\n\n"
        f"{BANK_INFO}\n\n"
        "Kirim bukti transfer ke sini ya."
    )

    await callback.message.answer(text)

    await callback.answer()


@dp.message(F.photo)
async def receive_proof(message: Message):

    file_id = message.photo[-1].file_id

    user_proofs[message.from_user.id] = file_id

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ SUDAH TRANSFER",
                    callback_data="confirm_transfer"
                )
            ]
        ]
    )

    await message.answer(
        "✅ Bukti diterima.\n\nSilakan klik tombol di bawah jika Anda sudah transfer.",
        reply_markup=kb
    )


@dp.callback_query(F.data == "confirm_transfer")
async def confirm_transfer(callback: CallbackQuery):

    user = callback.from_user

    package_key = user_packages.get(user.id)

    if not package_key:
        await callback.answer("Pilih paket terlebih dahulu")
        return

    package = PACKAGE_MAP[package_key]

    proof = user_proofs.get(user.id)

    admin_text = (
        "🔔 REQUEST PEMBAYARAN BARU\n\n"
        f"👤 Username: @{user.username}\n"
        f"🆔 User ID: {user.id}\n\n"
        f"📦 Paket: {package['label']}\n"
        f"💵 Harga: Rp {package['price']:,}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ TERIMA",
                    callback_data=f"approve_{user.id}"
                ),
                InlineKeyboardButton(
                    text="❌ TOLAK",
                    callback_data=f"reject_{user.id}"
                )
            ]
        ]
    )

    await bot.send_photo(
        ADMIN_ID,
        photo=proof,
        caption=admin_text,
        reply_markup=kb
    )

    await callback.message.answer(
        "✅ Permintaan berhasil dikirim ke admin.\nMohon tunggu verifikasi."
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    invite = await bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        member_limit=1
    )

    await bot.send_message(
        user_id,
        f"🎉 Pembayaran diterima.\n\nSilakan bergabung:\n{invite.invite_link}"
    )

    await callback.message.answer("✅ User berhasil diapprove")
    await callback.answer()


@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    await bot.send_message(
        user_id,
        "❌ Pembayaran ditolak.\nSilakan hubungi admin."
    )

    await callback.message.answer("❌ User ditolak")
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
