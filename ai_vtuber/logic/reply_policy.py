def infer_emotion(reply: str, original_message: str) -> str:
    """
    根据回复内容简单推断情绪
    """
    reply_lower = reply.lower()

    happy_signals = ["哈哈", "嘿嘿", "好耶", "不错", "谢谢", "开心", "棒"]
    shy_signals = ["才、才不是", "哼", "别这样", "你干嘛", "……"]
    angry_signals = ["过分", "算了", "不理你", "哼！", "烦"]

    for s in happy_signals:
        if s in reply:
            return "happy"
    for s in shy_signals:
        if s in reply:
            return "shy"
    for s in angry_signals:
        if s in reply:
            return "angry"

    return "normal"