import asyncio
import time
from llm.ollama_client import generate_reply_stream
from memory.memory_retriever import build_memory_context
from memory.memory_writer import process_danmu_for_memory
from logic.safety_filter import is_safe_input, filter_output
from logic.reply_policy import infer_emotion
from logic.danmu_filter import is_spam, record_danmu
from logic.danmu_queue import add_to_queue, pop_next, queue_size
from tts.tts_router import enqueue_speech, get_play_queue
from live.bilibili_listener import start_listening
from vtuber.vts_client import trigger_emotion
from concurrent.futures import ThreadPoolExecutor
_executor = ThreadPoolExecutor(max_workers=2)
COOLDOWN_SECONDS = 3
last_reply_time = None
is_generating = False  # 大模型是否在生成
is_speaking = False    # TTS是否在播放

async def process_next():
    global is_generating

    if is_generating:
        return

    item = pop_next()
    if not item:
        return

    user_id = item["user_id"]
    username = item["username"]
    message = item["representative"]

    print(f"[处理] {username}: {message}")
    is_generating = True

    try:
        process_danmu_for_memory(user_id, username, message)
        memory_ctx = build_memory_context(user_id, message)

        sentences_collected = []

        def collect_sentences():
            for sentence in generate_reply_stream(
                message,
                memory_context=memory_ctx,
                username=username
            ):
                s = filter_output(sentence)
                if s:
                    sentences_collected.append(s)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_executor, collect_sentences)

        if not sentences_collected:
            return

        full_reply = "".join(sentences_collected)
        for s in sentences_collected:
            print(f"[回复片段] {s}")

        emotion = infer_emotion(sentences_collected[0], message)
        print(f"[情绪] {emotion}")
        trigger_emotion(emotion)

        print(f"[完整回复] {full_reply}")

        # 如果歌曲在播，降低音量
        from music.spotify_client import is_playing, set_volume, get_current_volume
        music_was_playing = await loop.run_in_executor(None, is_playing)
        original_volume = 50
        if music_was_playing:
            original_volume = await loop.run_in_executor(None, get_current_volume)
            await loop.run_in_executor(None, set_volume, int(original_volume * 0.5))
            print(f"[音量] 降低到 {int(original_volume * 0.5)}%")

        await enqueue_speech(sentences_collected)

        # 恢复音量
        if music_was_playing:
            await loop.run_in_executor(None, set_volume, original_volume)
            print(f"[音量] 恢复到 {original_volume}%")

    finally:
        is_generating = False
        if queue_size() > 0:
            asyncio.get_event_loop().create_task(process_next())

def on_event(event: dict):
    asyncio.get_event_loop().create_task(_handle_incoming(event))

_music_playing = False

async def try_play_next():
    global _music_playing
    from music.spotify_client import play_song, is_playing
    from music.song_queue import pop_song
    from music.song_server import set_now_playing

    if _music_playing:
        return

    song = pop_song()
    if not song:
        return

    _music_playing = True
    set_now_playing(song)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, play_song, song["uri"])

    announcement = f"{song['requester']}点的{song['song_name']}，为您播放"
    await enqueue_speech([announcement])

    # 等待歌曲播放完后播下一首
    asyncio.get_event_loop().create_task(wait_for_song_end())

async def wait_for_song_end():
    global _music_playing
    from music.spotify_client import is_playing
    from music.song_server import set_now_playing
    from music.song_queue import queue_size

    await asyncio.sleep(5)  # 等5秒确保歌曲开始播了

    while True:
        loop = asyncio.get_event_loop()
        playing = await loop.run_in_executor(None, is_playing)
        if not playing:
            break
        await asyncio.sleep(3)

    _music_playing = False
    set_now_playing(None)

    # 播下一首
    if queue_size() > 0:
        asyncio.get_event_loop().create_task(try_play_next())

async def handle_song_request(username: str, song_name: str):
    from music.spotify_client import search_song
    from music.song_queue import add_song, set_not_found, clear_not_found

    print(f"[点歌] {username} 点了：{song_name}")

    loop = asyncio.get_event_loop()
    success, result = await loop.run_in_executor(
        None, search_song, song_name
    )

    if success:
        add_song(
            song_name=result["song_name"],
            artist=result["artist"],
            uri=result["uri"],
            requester=username
        )
        clear_not_found()
        print(f"[歌单] 已加入：{result['song_name']} - {result['artist']}")
        # 加入歌单不播报，只更新显示
        # 如果当前没有在播歌，自动开始播放
        asyncio.get_event_loop().create_task(try_play_next())
    else:
        set_not_found(result)
        print(f"[点歌] 未找到：{song_name}")
        await enqueue_speech([f"抱歉，没有找到{song_name}，换一首试试吧"])

async def _handle_incoming(event: dict):
    event_type = event.get("type")
    user_id = event.get("user_id", "unknown")
    username = event.get("username", "观众")

    if event_type == "danmu":
        message = event.get("content", "")

        # 先检测点歌，走独立通道不进队列
        from logic.danmu_filter import detect_song_request
        song_name = detect_song_request(message)
        if song_name:
            print(f"[点歌] {username} 点了：{song_name}")
            asyncio.get_event_loop().create_task(
                handle_song_request(username, song_name)
            )
            return  # 直接返回，不走普通弹幕流程

        # 普通弹幕流程
        spam, reason = is_spam(message, user_id)
        if spam:
            print(f"[垃圾过滤] 跳过：{message}，原因：{reason}")
            return

        if not is_safe_input(message):
            print(f"[安全过滤] 跳过：{message}")
            return

        record_danmu(message, user_id)
        await add_to_queue(user_id, username, message)

        if not is_generating:
            asyncio.get_event_loop().create_task(process_next())

async def main():
    print("AI虚拟主播启动中...")

    from memory.sqlite_store import init_db
    from memory.qdrant_store import init_collection, get_embedder
    init_db()
    init_collection()
    print("预热嵌入模型...")
    get_embedder()
    from music.song_server import start_server
    await start_server()
    print("记忆系统就绪")
    print("开始监听B站弹幕，Ctrl+C停止...")

    try:
        await start_listening(on_event)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n正在结束直播...")

        # 停止语音
        try:
            import pygame
            pygame.mixer.stop()
            pygame.mixer.quit()
        except:
            pass

        # 清空弹幕队列
        while queue_size() > 0:
            pop_next()

        # 清空歌单队列
        from music.song_queue import _song_queue
        _song_queue.clear()

        # 清空TTS播放队列
        play_queue = get_play_queue()
        if play_queue:
            while not play_queue.empty():
                try:
                    play_queue.get_nowait()
                    play_queue.task_done()
                except:
                    break

        # 停止Spotify播放
        try:
            from music.spotify_client import pause
            pause()
        except:
            pass

        print("系统已安全退出")

if __name__ == "__main__":
    asyncio.run(main())