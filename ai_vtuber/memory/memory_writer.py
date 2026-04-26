from memory.sqlite_store import add_user_fact, upsert_user
from memory.qdrant_store import add_memory
import sqlite3
import yaml
from datetime import datetime

# 触发写入记忆的关键词类型
PREFERENCE_KEYWORDS = ["喜欢", "最爱", "不喜欢", "讨厌", "爱看", "爱玩"]
IDENTITY_KEYWORDS = ["我是", "我在", "我正在", "我刚", "我考", "我工作"]
IMPORTANT_EVENTS = ["谢谢", "生日", "考完", "过了", "成功", "失败", "难过"]

def should_write_to_memory(message: str) -> tuple[bool, str]:
    """
    判断这条弹幕是否值得写入记忆
    返回 (是否写入, 分类)
    """
    for kw in PREFERENCE_KEYWORDS:
        if kw in message:
            return True, "preference"

    for kw in IDENTITY_KEYWORDS:
        if kw in message:
            return True, "biography"

    for kw in IMPORTANT_EVENTS:
        if kw in message:
            return True, "event"

    # 太短的弹幕不写入
    if len(message) < 5:
        return False, ""

    return False, ""

def process_danmu_for_memory(user_id: str, display_name: str, message: str):
    """
    处理一条弹幕，决定是否写入记忆
    """
    upsert_user(user_id, display_name)

    should_write, category = should_write_to_memory(message)

    if should_write:
        fact_text = f"{display_name}说：{message}"
        add_user_fact(
            user_id=user_id,
            fact=fact_text,
            category=category,
            confidence=0.7,
            importance=0.6,
            source="danmu"
        )
        # 同时写入向量库
        add_memory(fact_text, {
            "user_id": user_id,
            "type": "user_fact",
            "category": category
        })
        print(f"[记忆写入] {category}: {fact_text}")