from enum import Enum
import asyncio
import httpx
from .devices import Light
import logging
from .const import DOMAIN, VERBOSE

_LOGGER = logging.getLogger(__name__)

"""Logging function."""
def log(msg: str):
    if VERBOSE:
        _LOGGER.info(msg)

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

        log("RUN!!!!!!")
        self.state = State.Initializing
        await self._load_devices()


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
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, auth=auth)

                if response.status_code == 200:
                    # Парсинг данных устройств из ответа и возврат их
                    devices_data = response.json()
                    log("Devices data loaded")
                    self._handle_devices_data(devices_data)
                else:
                     raise Exception(f"Failed to fetch devices. Status code: {response.status_code}")
            except Exception as e:
                 raise Exception(f"Error while fetching devices: {str(e)}")
                # Вернуть пустой список в случае ошибки


    def _handle_devices_data(self, devices):
        for device_info in devices:
           device = self._handle_device_payload(device_info)

        self.state = State.Ready


    def _handle_device_payload(self, payload):
        device_id = payload['id']
        device = self._devices.get(device_id)
        if device is None:
            device = self._create_device_from_payload(payload)
            if device is None:
                return
            self._add_device(device)

        device.handle_state(payload)

    def _add_device(self, device):
        self._devices[device.device_id] = device


    def _create_device_from_payload(self, payload):
        device_id = payload['id']
        name = payload['name']
        dev_type = payload["type"]
        if dev_type == "switch":
            dimmable = False
            return Light(self, device_id, name, dimmable)
