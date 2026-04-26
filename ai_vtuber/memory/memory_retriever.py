from memory.sqlite_store import get_user_facts, get_user_profile
from memory.qdrant_store import search_memory

def build_memory_context(user_id: str, current_message: str) -> str:
    """
    根据用户ID和当前消息，拼出一段简洁的记忆上下文
    """
    lines = []

    # 1. 用户基本信息
    profile = get_user_profile(user_id)
    if profile:
        name = profile.get("display_name", user_id)
        affinity = profile.get("affinity_score", 0)
        if affinity > 5:
            lines.append(f"- {name} 是常来的观众，你们比较熟")
        elif affinity > 0:
            lines.append(f"- {name} 来过几次")
        else:
            lines.append(f"- {name} 是新观众")

    # 2. 结构化事实
    facts = get_user_facts(user_id, limit=3)
    for fact, category in facts:
        lines.append(f"- 你记得：{fact}")

    # 3. 语义检索
    semantic_results = search_memory(current_message, top_k=2)
    for r in semantic_results:
        if r.get("user_id") == user_id:
            lines.append(f"- 相关记忆：{r.get('text', '')}")

    if not lines:
        return ""

    return "\n".join(lines)