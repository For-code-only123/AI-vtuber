from collections import deque

# 歌单队列，每首歌的格式：
# {
#   "song_name": 歌曲名
#   "artist": 歌手名
#   "uri": spotify uri
#   "requester": 点歌的用户名
# }
_song_queue = deque()
_not_found_message = ""  # 未找到时的提示

def add_song(song_name: str, artist: str, uri: str, requester: str):
    _song_queue.append({
        "song_name": song_name,
        "artist": artist,
        "uri": uri,
        "requester": requester
    })

def pop_song() -> dict | None:
    if _song_queue:
        return _song_queue.popleft()
    return None

def get_queue() -> list:
    return list(_song_queue)

def queue_size() -> int:
    return len(_song_queue)

def set_not_found(message: str):
    global _not_found_message
    _not_found_message = message

def clear_not_found():
    global _not_found_message
    _not_found_message = ""

def get_not_found() -> str:
    return _not_found_message