import yaml

def load_safety_rules():
    with open("persona/safety.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def is_safe_input(message: str) -> bool:
    rules = load_safety_rules()
    for topic in rules.get("banned_topics", []):
        if topic in message:
            return False
    for word in rules.get("banned_words", []):
        if word and word in message:
            return False
    return True

def filter_output(reply: str) -> str:
    rules = load_safety_rules()
    for topic in rules.get("banned_topics", []):
        if topic in reply:
            return rules.get("response_on_banned", "这个话题星奈不太懂呢~")
    return reply