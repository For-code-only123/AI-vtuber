from aiohttp import web
from music.song_queue import get_queue, get_not_found
import json

_now_playing = None

def set_now_playing(song: dict | None):
    global _now_playing
    _now_playing = song

async def handle_status(request):
    data = {
        "now_playing": _now_playing,
        "queue": get_queue(),
        "not_found": get_not_found()
    }
    return web.Response(
        text=json.dumps(data, ensure_ascii=False),
        content_type='application/json',
        headers={"Access-Control-Allow-Origin": "*"}
    )

async def start_server():
    app = web.Application()
    app.router.add_get('/status', handle_status)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8889)
    await site.start()
    print("[歌单服务] 启动在 http://localhost:8889")