import asyncio
import time

class DanmuMerger:
    def __init__(self, wait_seconds=1.5):
        self.wait_seconds = wait_seconds
        self.pending = []
        self.callback = None
        self._task = None

    def set_callback(self, callback):
        self.callback = callback

    def add(self, event: dict):
        if event.get("type") != "danmu":
            if self.callback:
                asyncio.get_event_loop().create_task(self.callback(event))
            return

        self.pending.append(event)

        if self._task:
            self._task.cancel()
        self._task = asyncio.get_event_loop().create_task(self._flush())

    async def _flush(self):
        try:
            await asyncio.sleep(self.wait_seconds)
        except asyncio.CancelledError:
            return

        if not self.pending:
            return

        events = self.pending.copy()
        self.pending.clear()

        if len(events) == 1:
            if self.callback:
                await self.callback(events[0])
        else:
            merged_content = "，".join([e["content"] for e in events])
            merged_event = events[-1].copy()
            merged_event["content"] = merged_content
            print(f"[合并弹幕] {merged_content}")
            if self.callback:
                await self.callback(merged_event)