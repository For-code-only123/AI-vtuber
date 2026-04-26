import edge_tts
import pygame
import tempfile
import os
import asyncio
import re

VOICE = "zh-CN-XiaoyiNeural"
_play_queue = None
_player_started = False


def get_play_queue():
    global _play_queue
    if _play_queue is None:
        _play_queue = asyncio.Queue()
    return _play_queue


async def generate_audio(text: str) -> str | None:
    cleaned = re.sub(r'[（(][^）)]*[）)]', '', text).strip()
    cleaned = re.sub(r'[，,。！？!?…\n、；:：""\'\']+', '', cleaned).strip()
    if not cleaned or len(cleaned) < 2:
        return None

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, VOICE, rate="+15%")
            await communicate.save(tmp_path)
            return tmp_path
        except Exception as e:
            if attempt == 2:
                print(f"[TTS] 生成失败：{e}")
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                return None
            await asyncio.sleep(0.5)
    return None


async def play_audio(tmp_path: str):
    os.environ['SDL_AUDIODRIVER'] = 'directsound'
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.05)

    pygame.mixer.music.stop()
    pygame.mixer.quit()
    await asyncio.sleep(0.05)

    try:
        os.unlink(tmp_path)
    except:
        pass


async def speak_stream(sentence_iterator):
    pending_path = None

    for sentence in sentence_iterator:
        current_task = asyncio.create_task(generate_audio(sentence))

        if pending_path:
            await play_audio(pending_path)
            pending_path = None

        current_path = await current_task
        pending_path = current_path

    if pending_path:
        await play_audio(pending_path)


async def _player_loop():
    queue = get_play_queue()
    while True:
        sentences = await queue.get()
        try:
            await speak_stream(iter(sentences))
        finally:
            queue.task_done()


async def enqueue_speech(sentences: list):
    global _player_started
    if not _player_started:
        _player_started = True
        asyncio.get_event_loop().create_task(_player_loop())
    await get_play_queue().put(sentences)


async def speak_sentence(text: str):
    tmp_path = await generate_audio(text)
    if tmp_path:
        await play_audio(tmp_path)