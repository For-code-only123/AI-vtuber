import ollama
import yaml
import re


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_persona():
    with open("persona/persona.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_system_prompt(persona: dict) -> str:
    p = persona
    name = p.get("name", "星奈")
    age = p.get("identity", {}).get("age_style", "温柔亲切的少女感")
    role = p.get("identity", {}).get("role", "AI直播助手")
    background = p.get("identity", {}).get("background", "")
    philosophy = p.get("core_philosophy", "")
    tone = p.get("speech_style", {}).get("tone", "")
    max_length = p.get("speech_style", {}).get("max_length", "2-3句话")

    core_traits = "\n".join([
        f"- {t}" for t in p.get("personality", {}).get("core_traits", [])
    ])
    forbidden_traits = "\n".join([
        f"- {t}" for t in p.get("personality", {}).get("forbidden_traits", [])
    ])
    avoid_patterns = "\n".join([
        f"- {t}" for t in p.get("speech_style", {}).get("avoid_patterns", [])
    ])

    return f"""你是{name}，{age}的{role}。

【背景】
{background}

【核心气质】
{core_traits}

【说话方式】
- 语气：{tone}
- 长度：{max_length}
- 句子自然亲切，真诚不做作
- 认真对待每一个问题，给出有用的回答
- 不在括号里写动作描述

【绝对禁止】
{forbidden_traits}
{avoid_patterns}
- markdown格式

【核心理念】
{philosophy}

用中文回复。"""


def generate_reply_stream(user_message: str, memory_context: str = "", username: str = "观众"):
    config = load_config()
    persona = load_persona()
    system_prompt = build_system_prompt(persona)

    if memory_context:
        system_prompt += f"\n\n[关于这位观众你记得的信息]\n{memory_context}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{username}说：{user_message}"}
    ]

    stream = ollama.chat(
        model=config["ollama"]["model"],
        messages=messages,
        options={
            "temperature": config["ollama"]["temperature"],
            "num_predict": config["ollama"]["max_tokens"],
            "num_ctx": config["ollama"].get("num_ctx", 20480),
            "think": True
        },
        stream=True
    )

    buffer = ""
    thinking_buffer = ""

    for chunk in stream:
        thinking = chunk.get("message", {}).get("thinking", "")
        if thinking:
            thinking_buffer += thinking
            continue
        token = chunk["message"]["content"]
        if not token:
            continue
        buffer += token

        while True:
            match = re.search(r'[，,。！？!?…\n]', buffer)
            if not match:
                break
            end = match.end()
            sentence = buffer[:end].strip()
            buffer = buffer[end:]
            sentence = re.sub(r'[（(][^）)]*[）)]', '', sentence).strip()
            if sentence:
                yield sentence

    if not buffer and not thinking_buffer:
        return

    buffer = re.sub(r'[（(][^）)]*[）)]', '', buffer).strip()
    if buffer:
        yield buffer