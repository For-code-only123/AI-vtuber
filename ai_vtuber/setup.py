import os

dirs = ['persona', 'memory', 'llm', 'tts', 'live', 'logic', 'vtuber', 'tools']
files = [
    'app.py',
    'config.yaml',
    'persona/persona.yaml',
    'persona/safety.yaml',
    'memory/sqlite_store.py',
    'memory/qdrant_store.py',
    'memory/memory_writer.py',
    'memory/memory_retriever.py',
    'llm/ollama_client.py',
    'tts/tts_router.py',
    'live/bilibili_listener.py',
    'logic/reply_policy.py',
    'logic/safety_filter.py',
    'vtuber/vts_client.py',
    'tools/stream_scheduler.py',
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

for f in files:
    if not os.path.exists(f):
        open(f, 'w').close()

print('项目结构创建完成')