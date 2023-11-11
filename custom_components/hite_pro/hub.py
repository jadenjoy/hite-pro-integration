"""Class used to communicate with xComfort bridge."""

from __future__ import annotations
import httpx
import asyncio
import logging
from typing import List
from homeassistant.components.hite_pro.state import State

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

    async def change_device_state(self, identifier: int, state: bool):
        log("Changing state on HUB: " + str(identifier))
        state_value = "1" if state else "2"  # 1 если state true, иначе 2
        url = f"http://{self.host}/rest/devices/{str(identifier)}/{state_value}"
        auth = httpx.BasicAuth(self.username, self.password)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, auth=auth)

                if response.status_code == 200:
                    # Парсинг данных устройств из ответа и возврат их
                    devices_data = response.json()
                    return devices_data
                else:
                    log(f"Failed to change device state. Status code: {response.status_code}")
                    return []  # Вернуть пустой список в случае ошибки
            except Exception as e:
                log(f"Error while changing device state: {str(e)}")
                return []
                # Вернуть пустой список в случае ошибки


    async def load_devices(self):
        """Loads devices from bridge."""
        log("loading devices")
        devices_data = await self.api_get_devices()
        for device_info in devices_data:
            if device_info["type"] == "switch":
                device = Light(
                    self,
                    device_info["id"],
                    device_info["name"],
                    device_info["status"]
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
                return []
                # Вернуть пустой список в случае ошибки

    @property
    def hub_id(self) -> str:
        return self._id

    @staticmethod
    def get_hub(hass: HomeAssistant, entry: ConfigEntry) -> HiteProHub:
        return hass.data[DOMAIN][entry.entry_id]


class Light:
    def __init__(self, hub: HiteProHub, identifier: int, name: str, state: bool) -> None:
        self._switch = False
        self._hub = hub
        self.id = identifier
        self.name = name
        self.state = None
        # self.state.switch = state
        log("New device in class")

    async def switch(self, value):
        if isinstance(value, bool):
            self._switch = value
            await self._hub.change_device_state(self.id, value)
            # Здесь может быть ваш асинхронный код
            return self._switch
        else:
            print("Неверное значение. Пожалуйста, используйте True или False.")
            return None
