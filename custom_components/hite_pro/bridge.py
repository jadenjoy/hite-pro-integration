from enum import Enum
import asyncio
import httpx

class State(Enum):
    Uninitialized = 0
    Initializing = 1
    Ready = 2
    Closing = 10


class Bridge:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.state = State.Uninitialized
        self._devices = {}

    async def run(self):
        if self.state != State.Uninitialized:
            raise Exception("Run can only be called once at a time")

        await self._load_devices()
        self.state = State.Ready


    async def wait_for_initialization(self):
        if self.state == State.Uninitialized:
            await asyncio.sleep(0.1)

        while self.state == State.Initializing:
            await asyncio.sleep(0.1)

        return

    async def get_devices(self):
        await self.wait_for_initialization()
        return self._devices

    async def _load_devices(self):
        url = f"http://{self.host}/rest/devices"
        auth = httpx.BasicAuth(self.username, self.password)
