import asyncio
import edge_tts

TEST_TEXT = "你现在不是没想法，你只是情绪太吵了。别逞强了，你现在这个状态骗不过我。"

VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-liaoning-XiaobeiNeural",
    "zh-CN-shaanxi-XiaoniNeural",
]

async def main():
    for voice in VOICES:
        filename = f"tools/test_{voice}.mp3"
        communicate = edge_tts.Communicate(TEST_TEXT, voice)
        await communicate.save(filename)
        print(f"已生成：{filename}")
    print("全部生成完毕，去tools文件夹听")

asyncio.run(main())