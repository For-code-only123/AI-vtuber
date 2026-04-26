import asyncio
import websockets
import json

VTS_URL = "ws://localhost:8001"
VTS_TOKEN = "7a505be14aa02dad50b1db561ca612e6864bc2bd64f713f2605494b256d5eb15"

# EMOTION_HOTKEY_MAP = {
#     "happy":  "514363eff0a84f40b31b98cf5eba6522",
#     "shy":    "214d149213824bad8bb033859fc1d85a",
#     "angry":  "349facd75a1142aabf890c01cb71d9c3",
#     "normal": None
# }
EMOTION_HOTKEY_MAP = {
    "happy":  None,
    "shy":    None,
    "angry":  None,
    "normal": None
}

async def _trigger_hotkey(hotkey_id: str):
    try:
        async with websockets.connect(VTS_URL) as ws:

            # 先尝试直接认证（用已有token）
            await ws.send(json.dumps({
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "auth",
                "messageType": "AuthenticationRequest",
                "data": {
                    "pluginName": "HotkeyChecker",
                    "pluginDeveloper": "MyVtuberProject",
                    "authenticationToken": VTS_TOKEN
                }
            }))
            resp = json.loads(await ws.recv())
            authenticated = resp.get("data", {}).get("authenticated", False)

            if not authenticated:
                print(f"[VTS] 认证失败: {resp}")
                return

            # 触发热键
            await ws.send(json.dumps({
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "hotkey",
                "messageType": "HotkeyTriggerRequest",
                "data": {"hotkeyID": hotkey_id}
            }))
            resp = json.loads(await ws.recv())
            if resp["messageType"] == "HotkeyTriggerResponse":
                print(f"[VTS] 热键触发成功")
            else:
                print(f"[VTS] 热键触发失败: {resp}")

    except Exception as e:
        print(f"[VTS] 连接失败: {e}")

def trigger_emotion(emotion: str):
    hotkey_id = EMOTION_HOTKEY_MAP.get(emotion)
    if hotkey_id:
        asyncio.get_event_loop().create_task(_trigger_hotkey(hotkey_id))