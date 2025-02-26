import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Deque


class RateLimitManager:
    def __init__(self) -> None:
        self.short_window: Deque[datetime] = deque(maxlen=20)
        self.short_window = deque(maxlen=20)

        self.long_window: Deque[datetime] = deque(maxlen=100)
        self.long_window = deque(maxlen=100)

    async def wait_if_needed(self) -> None:
        current_time = datetime.now()

        while len(self.short_window) == 20:
            if current_time - self.short_window[0] > timedelta(seconds=1):
                self.short_window.popleft()
            else:
                await asyncio.sleep(0.05)
                current_time = datetime.now()

        while len(self.long_window) == 100:
            if current_time - self.long_window[0] > timedelta(minutes=2):
                self.long_window.popleft()
            else:
                await asyncio.sleep(0.05)
                current_time = datetime.now()

        self.short_window.append(current_time)
        self.long_window.append(current_time)
