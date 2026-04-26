import asyncio
import websockets
import json

async def get_hotkeys():
    async with websockets.connect("ws://localhost:8001") as ws:
        # 第一步：申请token
        await ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "1",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": "HotkeyChecker",
                "pluginDeveloper": "MyVtuberProject",
                "pluginIcon": ""
            }
        }))
        resp = json.loads(await ws.recv())
        print("完整响应：", json.dumps(resp, ensure_ascii=False, indent=2))
        token = resp["data"].get("authenticationToken", "")
        if not token:
            print("未获取到token，请检查VTube Studio是否弹出了授权窗口并点击了允许")
            return

        print("Token获取成功:", token)

        # 第二步：认证
        await ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "2",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": "HotkeyChecker",
                "pluginDeveloper": "MyVtuberProject",
                "authenticationToken": token
            }
        }))
        resp = json.loads(await ws.recv())
        authenticated = resp["data"].get("authenticated", False)

        if not authenticated:
            print("认证失败:", resp["data"])
            return

        print("认证成功！")

        # 第三步：获取热键列表
        await ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "3",
            "messageType": "HotkeysInCurrentModelRequest",
            "data": {}
        }))
        resp = json.loads(await ws.recv())
        hotkeys = resp["data"].get("availableHotkeys", [])

        if not hotkeys:
            print("没有找到任何热键，请先在VTube Studio里设置热键")
            return

        print("\n可用热键列表：")
        for hk in hotkeys:
            print(f"  名称: {hk['name']}  ID: {hk['hotkeyID']}  类型: {hk['type']}")

asyncio.run(get_hotkeys())