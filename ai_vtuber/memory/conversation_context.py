from collections import deque

# 全局对话窗口，保存最近5条
_context = deque(maxlen=5)

def add_turn(username: str, user_message: str, ai_reply: str):
    _context.append({
        "username": username,
        "user": user_message,
        "ai": ai_reply
    })

def get_context_prompt() -> str:
    if not _context:
        return ""
    lines = ["[最近对话记录]"]
    for turn in _context:
        lines.append(f"{turn['username']}：{turn['user']}")
        lines.append(f"星奈：{turn['ai']}")
    return "\n".join(lines)

def clear_context():
    _context.clear()