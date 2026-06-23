import requests
from datetime import datetime

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw-Fy1k3GjX7fYTTAfgcDNs2FWlWeCZxW60zCsYXsjJlZHnAkgGuoVfS0fN1Ms14x1eqA/exec"


async def expiry_worker(bot, group_id):
    while True:
        try:
            r = requests.get(WEB_APP_URL, params={"action": "get_all_users"})
            users = r.json().get("users", [])

            now = datetime.utcnow()

            for u in users:
                user_id = int(u[0])
                expire = u[5]

                if not expire:
                    continue

                exp = datetime.strptime(expire, "%Y-%m-%d %H:%M:%S")

                if now > exp:
                    try:
                        await bot.ban_chat_member(group_id, user_id)
                        await bot.unban_chat_member(group_id, user_id)
                    except:
                        pass

        except Exception as e:
            print("worker error:", e)

        await asyncio.sleep(60)
