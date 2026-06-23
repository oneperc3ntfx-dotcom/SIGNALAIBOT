import asyncio
from datetime import datetime

from storage import PENDING_PAYMENT
from config import VIP_CHAT_ID  # nanti kamu set di config.py

# contoh memory active users (nanti bisa diganti DB/Sheet)
ACTIVE_USERS = {}


# =========================
# ACTIVATE USER
# =========================

def activate_user(user_id, expire_at):
    ACTIVE_USERS[user_id] = expire_at


# =========================
# KICK USER FUNCTION
# =========================

async def kick_user(bot, user_id):
    try:
        await bot.ban_chat_member(chat_id=VIP_CHAT_ID, user_id=user_id)
        await bot.unban_chat_member(chat_id=VIP_CHAT_ID, user_id=user_id)
    except Exception as e:
        print("Kick error:", e)


# =========================
# EXPIRE CHECK LOOP
# =========================

async def scheduler_loop(bot):
    while True:
        now = datetime.now()

        for user_id, expire_time in list(ACTIVE_USERS.items()):
            if expire_time and now >= expire_time:

                # 1. KICK USER
                await kick_user(bot, user_id)

                # 2. NOTIF USER
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text="""
⛔ MASA AKTIF KAMU SUDAH HABIS

Akses Signal AI kamu telah dihentikan.

💡 Silakan lakukan perpanjangan untuk kembali menikmati signal 24 jam.
"""
                    )
                except:
                    pass

                # 3. REMOVE FROM ACTIVE
                del ACTIVE_USERS[user_id]

        await asyncio.sleep(60)  # cek tiap 1 menit
