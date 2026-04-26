from collections import deque
from memory.qdrant_store import get_embedder
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=2)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

_queue = deque()
SIMILARITY_THRESHOLD = 0.6

def _encode_and_add(user_id: str, username: str, message: str):
    embedder = get_embedder()
    vector = embedder.encode(message)

    for item in _queue:
        sim = cosine_similarity(vector, item["vector"])
        if sim >= SIMILARITY_THRESHOLD:
            item["representative"] = message
            item["vector"] = vector
            item["count"] += 1
            print(f"[队列合并] 相似度{sim:.2f}，当前队列长度：{len(_queue)}")
            return

    _queue.append({
        "representative": message,
        "user_id": user_id,
        "username": username,
        "vector": vector,
        "count": 1
    })
    print(f"[队列] 新增槽位，当前队列长度：{len(_queue)}")

async def add_to_queue(user_id: str, username: str, message: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _encode_and_add, user_id, username, message)

def pop_next() -> dict | None:
    if _queue:
        return _queue.popleft()
    return None

def queue_size() -> int:
    return len(_queue)