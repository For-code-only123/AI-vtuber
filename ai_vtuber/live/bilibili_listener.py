import asyncio
import aiohttp
import blivedm
import blivedm.models.web as web_models

ROOM_ID = 3247435

# 填入你的SESSDATA
SESSDATA = "cf21cbfd%2C1789287455%2C91211%2A32CjD_LtcxOBytkf20dpFrg6fvNkqaT3swt3vCSGmSJXK-jQrzZxkhtG0QEG6Wb2x7b3YSVnh5OEJCYzRHZnJ0TE50NHVCcjJEWjJXejkyUDdXMjRhZk8zTkw3d3VVZDRWWXRIV01RWkFiay1DZzdXRW5BWk5MVlZBZ2lGSlJtSW5WeDlMVDVsV1lnIIEC"

class DanmuHandler(blivedm.BaseHandler):
    def __init__(self, callback):
        self.callback = callback

    def _on_danmaku(self, client, message: web_models.DanmakuMessage):
        self.callback({
            "type": "danmu",
            "user_id": str(message.uid),
            "username": message.uname,
            "content": message.msg
        })

    def _on_gift(self, client, message: web_models.GiftMessage):
        self.callback({
            "type": "gift",
            "user_id": str(message.uid),
            "username": message.uname,
            "gift_name": message.gift_name,
            "count": message.num
        })

async def start_listening(callback):
    cookies = aiohttp.CookieJar()
    cookies.update_cookies({"SESSDATA": SESSDATA})
    session = aiohttp.ClientSession(cookie_jar=cookies)

    client = blivedm.BLiveClient(ROOM_ID, session=session)
    handler = DanmuHandler(callback)
    client.set_handler(handler)
    client.start()
    try:
        await asyncio.sleep(999999)
    finally:
        await client.stop_and_close()
        await session.close()