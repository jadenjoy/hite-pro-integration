"""Class used to communicate with xComfort bridge."""

from __future__ import annotations

import asyncio
import logging
from typing import List

from xcomfort.bridge import State
from xcomfort.devices import Light, LightState

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERBOSE
from .bridge import Bridge

_LOGGER = logging.getLogger(__name__)

"""Logging function."""
def log(msg: str):
    if VERBOSE:
        _LOGGER.info(msg)


"""Wrapper class over bridge library to emulate hub."""
class HiteProHub:
    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
    ):
        """Initialize underlying bridge"""
        bridge = Bridge(host, username, password)
        self.bridge = bridge
        self.identifier = host
        if self.identifier is None:
            self.identifier = host
        self._id = host
        self.devices = list()
        log("getting event loop")
        self._loop = asyncio.get_event_loop()

    def start(self):
        """Starts the event loop running the bridge."""
        asyncio.create_task(self.bridge.run())

    async def stop(self):
        """Stops the bridge event loop.
        Will also shut down websocket, if open."""
        await self.bridge.close()

    async def load_devices(self):
        """Loads devices from bridge."""
        log("loading devices")
        devs = await self.bridge.get_devices()
        self.devices = devs.values()
        log(f"loaded {len(self.devices)} devices")

    @property
    def hub_id(self) -> str:
        return self._id

    async def test_connection(self) -> bool:
        await asyncio.sleep(1)
        return True

    @staticmethod
    def get_hub(hass: HomeAssistant, entry: ConfigEntry) -> HiteProHub:
        return hass.data[DOMAIN][entry.entry_id]
