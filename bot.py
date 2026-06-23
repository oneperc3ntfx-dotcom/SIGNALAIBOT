import asyncio
import requests
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import *
from aiogram.filters import Command
from aiogram.types import FSInputFile

from config import BOT_TOKEN, ADMIN_ID, GROUP_ID, BANK_INFO
from packages import PACKAGE_MAP
from scheduler import expiry_worker


# ================= BOT INIT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_packages = {}

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxpCkQotuD5i0RMyJ0J4Px9o2QO9Hoz2iscxJGQDIwNTM-8J6QSM5a6bMhuEn2N-YM9nQ/exec"


# ================= SIGNAL TEMPLATE =================
def generate_signal():
    return """
<blockquote>
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
</blockquote>
"""


# ================= GOOGLE SHEET =================
def add_user(user_id, username, package, price):
    try:
        requests.get(WEB_APP_URL, params={
            "action": "add_user",
            "user_id": user_id,
            "username": username,
            "package": package,
            "price": price
        }, timeout=10)
    except Exception as e:
        print("add_user error:", e)


def approve_user(user_id, expire_at):
    try:
        requests.get(WEB_APP_URL, params={
            "action": "approve",
            "user_id": user_id,
            "expire_at": expire_at
        }, timeout=10)
    except Exception as e:
        print("approve error:", e)


# ================= FIX FORMAT HELPER =================
def now_str():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


# ================= FINAL KICK FUNCTION =================
async def kick_and_disable(user_id: int):

    try:
        await bot.ban_chat_member(GROUP_ID, user_id)
        await bot.unban_chat_member(GROUP_ID, user_id)
    except:
        pass

    # premium sheet expired
    try:
        requests.get(WEB_APP_URL, params={
            "action": "expire_user",
            "user_id": user_id
        }, timeout=10)
    except:
        pass

    # trial sheet expired
    try:
        requests.get(WEB_APP_URL, params={
            "action": "expire_trial",
            "user_id": user_id
        }, timeout=10)
    except:
        pass

    try:
        await bot.send_message(
            user_id,
            "⛔ Masa aktif kamu sudah berakhir.\nSilakan berlangganan kembali untuk akses Signal AI."
        )
    except:
        pass


# ================= START =================
@dp.message(Command("start"))
async def start(message: Message):

    photo = FSInputFile("assets/signal_ai.png")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 SAYA BERSEDIA BERGABUNG", callback_data="join")]
    ])

    text = (
        "🎯 <b>SELAMAT DATANG DI SIGNAL AI SYSTEM</b>\n\n"
        "Halo 👋\n\n"
        "Mohon Di baca Gambar Diatas Sebelum Bergabung\n\n"
        "📊 <b>CONTOH SIGNAL AI TOOLS SYSTEM</b>\n\n"
        + generate_signal() +
        "\n💡 <b>Silahkan Klik Tombol Di bawah , jika sudah Memahami.</b>"
    )

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb, parse_mode="HTML")


# ================= JOIN =================
@dp.callback_query(F.data == "join")
async def join(callback: CallbackQuery):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 BULAN - 199K", callback_data="pkg_1bulan")],
        [InlineKeyboardButton(text="6 BULAN - 549K", callback_data="pkg_6bulan")],
        [InlineKeyboardButton(text="12 BULAN - 999K", callback_data="pkg_12bulan")],
        [InlineKeyboardButton(text="PERMANENT - 1.999K", callback_data="pkg_permanent")],
        [InlineKeyboardButton(text="🎁 GRATIS / TRIAL", callback_data="free_trial")]
    ])

    await callback.message.answer(
        "💰 <b>BIAYA BERLANGGANAN SIGNAL AI PREMIUM</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.message.delete()
    await callback.answer()


# ================= PACKAGE =================
@dp.callback_query(F.data.startswith("pkg_"))
async def select_package(callback: CallbackQuery):

    package = callback.data.split("_")[1]
    user_packages[callback.from_user.id] = package

    price = PACKAGE_MAP[package]["price"]

    text = (
        f"💰 Paket: {PACKAGE_MAP[package]['label']}\n"
        f"💵 Harga: Rp {price}\n\n"
        f"🏦 {BANK_INFO}\n\n"
        "Kirim bukti transfer."
    )

    await callback.message.answer(text)
    await callback.message.delete()
    await callback.answer()


# ================= FREE TRIAL =================
@dp.callback_query(F.data == "free_trial")
async def free_trial(callback: CallbackQuery):

    user_id = callback.from_user.id

    r = requests.get(WEB_APP_URL, params={
        "action": "get_trial",
        "user_id": user_id
    })

    if r.json().get("found"):
        await callback.message.answer("❌ Sudah pernah trial")
        return

    now = datetime.utcnow()
    expire_at = now + timedelta(minutes=30)

    requests.get(WEB_APP_URL, params={
        "action": "add_trial",
        "user_id": user_id,
        "username": callback.from_user.username or "no_username",
        "claim_at": now_str(),
        "expire_at": expire_at.strftime("%Y-%m-%d %H:%M:%S")   # FIX FORMAT
    })

    invite = await bot.create_chat_invite_link(
        GROUP_ID,
        member_limit=1,
        expire_date=int(expire_at.timestamp())
    )

    await bot.send_message(user_id, f"🎁 TRIAL AKTIF\n{invite.invite_link}")


# ================= PROOF =================
@dp.message(F.photo)
async def proof(message: Message):

    user = message.from_user
    package = user_packages.get(user.id, "1bulan")
    price = PACKAGE_MAP.get(package, {}).get("price", 0)

    add_user(user.id, user.username or "no_username", package, price)

    await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ SUDAH TRANSFER", callback_data=f"confirm_{user.id}")]
    ])

    await message.answer("✅ Bukti diterima", reply_markup=kb)


# ================= CONFIRM =================
@dp.callback_query(F.data.startswith("confirm_"))
async def confirm(callback: CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="TERIMA", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="TOLAK", callback_data=f"reject_{user_id}")
        ]
    ])

    await bot.send_message(ADMIN_ID, f"REQUEST USER: {user_id}", reply_markup=kb)
    await callback.answer()


# ================= APPROVE =================
@dp.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    package = user_packages.get(user_id, "1bulan")
    now = datetime.utcnow()

    if package == "1bulan":
        member_expire = now + timedelta(days=30)
    elif package == "6bulan":
        member_expire = now + timedelta(days=180)
    elif package == "12bulan":
        member_expire = now + timedelta(days=365)
    else:
        member_expire = now + timedelta(days=30)

    invite = await bot.create_chat_invite_link(
        GROUP_ID,
        member_limit=1,
        expire_date=int((now + timedelta(minutes=10)).timestamp())
    )

    await bot.send_message(user_id, f"🎉 AKSES AKTIF\n{invite.invite_link}")

    approve_user(user_id, member_expire.strftime("%Y-%m-%d %H:%M:%S"))

    await callback.answer()


# ================= REJECT =================
@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    await bot.send_message(user_id, "❌ Ditolak")
    await callback.answer()


# ================= MANUAL COMMANDS =================

@dp.message(Command("trial"))
async def cmd_trial(message: Message):

    r = requests.get(WEB_APP_URL, params={"action": "get_all_trials"})
    data = r.json().get("trials", [])

    text = "📊 ACTIVE TRIAL USERS:\n\n"

    for u in data:
        if str(u[4]).lower() != "active":
            continue
        text += f"{u[0]} | {u[1]} | {u[3]}\n"

    await message.answer(text)


@dp.message(Command("db"))
async def cmd_db(message: Message):

    r = requests.get(WEB_APP_URL, params={"action": "get_all_users"})
    data = r.json().get("users", [])

    text = "📊 ACTIVE USERS:\n\n"

    for u in data:
        if str(u[4]).lower() != "active":
            continue
        if str(u[6]) not in ["", None]:
            continue
        text += f"{u[0]} | {u[1]} | {u[5]}\n"

    await message.answer(text)


@dp.message(Command("kick"))
async def cmd_kick(message: Message):

    try:
        user_id = int(message.text.split()[1])
        await kick_and_disable(user_id)
        await message.answer(f"✅ Kicked {user_id}")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")


# ================= MAIN =================
async def main():
    asyncio.create_task(expiry_worker(bot, GROUP_ID))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
