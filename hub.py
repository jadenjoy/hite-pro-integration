"""Class used to communicate with xComfort bridge."""

from __future__ import annotations
import httpx
import asyncio
import logging
from typing import List
from homeassistant.components.hitepro.state import State

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERBOSE


_LOGGER = logging.getLogger(__name__)

"""Logging function."""


def log(msg: str):
    if VERBOSE:
        _LOGGER.info(msg)


class HiteProHub:
    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
    ):
        """Initialize underlying bridge"""
        self._id = host
        self.host = host
        self.identifier = host
        self.username = username
        self.password = password
        self.devices = list()
        log("getting event loop")
        self._loop = asyncio.get_event_loop()

    async def load_devices(self):
        """Loads devices from bridge."""
        log("loading devices")
        devices_data = await self.api_get_devices()
        for device_info in devices_data:
            if device_info["type"] == "switch":
                device = Light(
                    device_info["id"], device_info["name"], device_info["status"]
                )  # Замените Device на ваш класс устройства
                self.devices.append(device)
        log(f"loaded {len(self.devices)} devices")

    async def api_get_devices(self):
        """Fetch devices from the specified host using Basic Auth."""
        url = f"http://{self.host}/rest/devices"  # Предполагается, что self.host - это URL из настроек

        log(url)
        log(self.username)
        log(self.password)
        # Задайте имя пользователя и пароль для Basic Auth из настроек
        auth = httpx.BasicAuth(self.username, self.password)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, auth=auth)

                if response.status_code == 200:
                    # Парсинг данных устройств из ответа и возврат их
                    devices_data = response.json()
                    return devices_data
                else:
                    log(f"Failed to fetch devices. Status code: {response.status_code}")
                    return []  # Вернуть пустой список в случае ошибки
            except Exception as e:
                log(f"Error while fetching devices: {str(e)}")
                return [
                    {"id": 15, "name": "1-1", "type": "switch", "status": False},
                    {"id": 16, "name": "1-2", "type": "switch", "status": False},
                    {"id": 17, "name": "1-3", "type": "switch", "status": False},
                    {"id": 18, "name": "1-4", "type": "switch", "status": False},
                    {"id": 19, "name": "2-1", "type": "switch", "status": False},
                    {"id": 20, "name": "2-2", "type": "switch", "status": False},
                    {
                        "id": 21,
                        "name": "Коридор 1эт",
                        "type": "switch",
                        "status": False,
                    },
                    {"id": 22, "name": "2-4", "type": "switch", "status": False},
                    {"id": 23, "name": "3-1", "type": "switch", "status": False},
                    {
                        "id": 24,
                        "name": "Кабинет Отец",
                        "type": "switch",
                        "status": False,
                    },
                    {
                        "id": 25,
                        "name": "Кухня верхний",
                        "type": "switch",
                        "status": False,
                    },
                    {
                        "id": 26,
                        "name": "Кухня над столом",
                        "type": "switch",
                        "status": False,
                    },
                    {"id": 27, "name": "4-1", "type": "switch", "status": False},
                    {"id": 28, "name": "4-2", "type": "switch", "status": True},
                    {"id": 29, "name": "4-3", "type": "switch", "status": False},
                    {"id": 30, "name": "4-4", "type": "switch", "status": False},
                    {"id": 31, "name": "5-1", "type": "switch", "status": False},
                    {"id": 32, "name": "Туалет 1эт", "type": "switch", "status": False},
                    {"id": 33, "name": "5-3", "type": "switch", "status": False},
                    {"id": 34, "name": "Бойлерная", "type": "switch", "status": False},
                    {"id": 35, "name": "6-1", "type": "switch", "status": False},
                    {"id": 36, "name": "6-2", "type": "switch", "status": False},
                    {"id": 37, "name": "6-3", "type": "switch", "status": False},
                    {"id": 38, "name": "6-4", "type": "switch", "status": False},
                    {"id": 39, "name": "7-1", "type": "switch", "status": False},
                    {
                        "id": 40,
                        "name": "Кабинет Кости",
                        "type": "switch",
                        "status": True,
                    },
                    {"id": 41, "name": "7-3", "type": "switch", "status": False},
                    {"id": 42, "name": "7-4", "type": "switch", "status": False},
                    {"id": 43, "name": "8-1", "type": "switch", "status": False},
                    {"id": 44, "name": "8-2", "type": "switch", "status": False},
                    {"id": 45, "name": "8-3", "type": "switch", "status": False},
                    {"id": 46, "name": "8-4", "type": "switch", "status": False},
                    {"id": 47, "name": "9-1", "type": "switch", "status": False},
                    {
                        "id": 48,
                        "name": "Гардеробная",
                        "type": "switch",
                        "status": False,
                    },
                    {"id": 49, "name": "9-3", "type": "switch", "status": False},
                    {"id": 50, "name": "9-4", "type": "switch", "status": False},
                    {"id": 51, "name": "10-1", "type": "switch", "status": False},
                    {"id": 52, "name": "10-2", "type": "switch", "status": False},
                    {"id": 53, "name": "10-3", "type": "switch", "status": False},
                    {"id": 54, "name": "10-4", "type": "switch", "status": False},
                    {"id": 55, "name": "11-1", "type": "switch", "status": False},
                    {
                        "id": 56,
                        "name": "Комната кости верхний свет",
                        "type": "switch",
                        "status": False,
                    },
                    {"id": 57, "name": "11-3", "type": "switch", "status": False},
                    {"id": 58, "name": "11-4", "type": "switch", "status": False},
                    {"id": 59, "name": "12-1", "type": "switch", "status": False},
                    {"id": 60, "name": "12-2", "type": "switch", "status": False},
                    {"id": 61, "name": "12-3", "type": "switch", "status": False},
                    {"id": 62, "name": "12-4", "type": "switch", "status": False},
                    {"id": 63, "name": "Клавиша 1", "type": "transmitter"},
                    {"id": 64, "name": "Клавиша 2", "type": "transmitter"},
                    {"id": 65, "name": "Клавиша 3", "type": "transmitter"},
                    {"id": 66, "name": "Клавиша 4", "type": "transmitter"},
                    {"id": 68, "name": "Выключатель душевая", "type": "transmitter"},
                    {
                        "id": 69,
                        "name": "Выключатель спальня родителей 1",
                        "type": "transmitter",
                    },
                    {
                        "id": 70,
                        "name": "Выключатель спальня родителей 2",
                        "type": "transmitter",
                    },
                ]

                # Вернуть пустой список в случае ошибки

    @property
    def hub_id(self) -> str:
        return self._id

    @staticmethod
    def get_hub(hass: HomeAssistant, entry: ConfigEntry) -> HiteProHub:
        return hass.data[DOMAIN][entry.entry_id]


class Light:
    def __init__(self, identifier: int, name: str, state: bool) -> None:
        self._switch = False
        self.id = identifier
        self.name = name
        self.state = None
        # self.state.switch = state
        log("New device in class")

    async def switch(self, value):
        if isinstance(value, bool):
            self._switch = value
            # Здесь может быть ваш асинхронный код
            return self._switch
        else:
            print("Неверное значение. Пожалуйста, используйте True или False.")
            return None
