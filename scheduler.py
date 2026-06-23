from datetime import datetime

ACTIVE_USERS = {}


def activate_user(user_id, expire_at):
    ACTIVE_USERS[user_id] = expire_at


async def scheduler_loop(bot):
    while True:
        now = datetime.now()

        for user_id, exp in list(ACTIVE_USERS.items()):
            if exp and now >= exp:
                try:
                    await bot.ban_chat_member(chat_id=-1001234567890, user_id=user_id)
                    await bot.unban_chat_member(chat_id=-1001234567890, user_id=user_id)
                except:
                    pass

                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text="⛔ Akses kamu sudah habis. Silakan upgrade."
                    )
                except:
                    pass

                del ACTIVE_USERS[user_id]

        import asyncio
        await asyncio.sleep(60)
