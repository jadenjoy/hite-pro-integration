from enum import Enum
import asyncio
import httpx

from .messages import Messages, SwitchState
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


        self.message_handlers = {
            Messages.NACK: self._handle_dummy,
            Messages.ACK: self._handle_dummy,
            Messages.HEARTBEAT: self._handle_dummy,
            Messages.SET_DEVICE_STATE: self._handle_dummy,
            Messages.ACTION_SWITCH_DEVICE: self._handle_switch_device,
        }

    async def run(self):
        if self.state != State.Uninitialized:
            raise Exception("Run can only be called once at a time")
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
        devices_data = await self._request("GET", "/devices")
        self._handle_devices_data(devices_data)


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

    async def switch_device(self, device_id, message):
        payload = {"deviceId": device_id}
        payload.update(message)
        await self.send_message(Messages.ACTION_SWITCH_DEVICE, payload)


    async def _request(self, method: str ,path: str, payload = None):
        url = f"http://{self.host}/rest"+path
        auth = httpx.BasicAuth(self.username, self.password)

        async with httpx.AsyncClient() as client:
            try:
                if method == 'GET':
                    response = await client.get(url, auth=auth)
                elif method == 'POST':
                    response = await client.post(url, auth=auth, json=payload)
                elif method == 'PUT':
                    response = await client.put(url, auth=auth, json=payload)
                # Добавьте другие методы (PUT, DELETE) по необходимости

                if response.status_code == 200:
                    # Парсинг данных устройств из ответа и возврат их
                    data = response.json()
                    return data
                else:
                    raise Exception(f"Failed to fetch url {url}. Status code: {response.status_code}")
            except Exception as e:
                raise Exception(f"Error while fetching url {url}: {str(e)}")



    async def send_message(self, message_type: Messages, message):
        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            await handler(message)
        else:
            # Обработка случая, если тип сообщения не найден
            raise Exception("Unknown message type")
        # await self.connection.send_message(message_type, message)

    async def _handle_dummy(self, message):
        log(message)

    async def _handle_switch_device(self, message):
        state_value = SwitchState.ON if message["switch"] else SwitchState.OFF
        device_id = message["deviceId"]
        url = f"/devices/{device_id}/{state_value}"
        await self._request("PUT", url)



