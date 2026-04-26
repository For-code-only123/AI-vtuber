import re
from collections import deque

# 记录格式改成 {user_id: deque}，按用户分别记录
_user_recent = {}

SPAM_KEYWORDS = [
    "关注", "点赞", "私信", "加微信", "加QQ", "推广", "引流",
    "领取", "福利", "免费", "赚钱", "兼职"
]

def is_spam(message: str, user_id: str = "") -> tuple[bool, str]:
    msg = message.strip()

    # 1. 太短
    if len(msg) < 2:
        return True, "太短"

    # 2. 纯标点或表情
    cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', msg)
    if len(cleaned) < 2:
        return True, "纯符号"

    # 3. 大量重复字符
    if re.search(r'(.)\1{4,}', msg):
        return True, "重复字符"

    # 4. 同一用户复读检测
    if user_id:
        user_history = _user_recent.get(user_id, deque(maxlen=5))
        if msg in user_history:
            return True, "同用户复读"

    # 5. 广告关键词
    for kw in SPAM_KEYWORDS:
        if kw in msg:
            return True, f"广告关键词:{kw}"

    return False, ""
def detect_song_request(message: str) -> str | None:
    """
    识别点歌弹幕，返回歌曲名，没有则返回None
    支持格式：《xxx》、「xxx」、【xxx】、点歌xxx
    """
    # 书名号格式
    match = re.search(r'[《「【](.+?)[》」】]', message)
    if match:
        return match.group(1).strip()

    # 点歌格式
    match = re.search(r'点歌\s*(.+)', message)
    if match:
        return match.group(1).strip()

    return None

def record_danmu(message: str, user_id: str = ""):
    if user_id:
        if user_id not in _user_recent:
            _user_recent[user_id] = deque(maxlen=5)
        _user_recent[user_id].append(message.strip())