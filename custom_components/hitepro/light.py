import asyncio
import logging
from math import ceil

from homeassistant.components.hitepro.state import State

from .hub import Light, HiteProHub

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, VERBOSE

_LOGGER = logging.getLogger(__name__)


def log(msg: str):
    if VERBOSE:
        _LOGGER.info(msg)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hub = HiteProHub.get_hub(hass, entry)

    devices = hub.devices

    _LOGGER.info(f"Found {len(devices)} hitepro devices")

    lights = list()
    for device in devices:
        if isinstance(device, Light):
            _LOGGER.info(f"Adding {device}")
            light = HASSXComfortLight(hass, hub, device)
            lights.append(light)

    _LOGGER.info(f"Added {len(lights)} lights")
    async_add_entities(lights)


class HASSXComfortLight(LightEntity):
    def __init__(self, hass: HomeAssistant, hub: HiteProHub, device: Light) -> None:
        self.hass = hass
        self.hub = hub

        self._device = device
        self._name = device.name
        self._state = State()
        self.device_id = self._device.id
        self._unique_id = f"light_{DOMAIN}_{hub.identifier}-{self._device.id}"

    async def async_added_to_hass(self):
        log(f"Added to hass {self._name} ")
        if self._device.state is None:
            log(f"State is null for {self._name}")
        else:
            self._device.state.subscribe(lambda state: self._state_change(state))

    def _state_change(self, state):
        log("_state_change for {self._name}")
        self._state = state
        should_update = self._state is not None

        log(f"State changed {self._name} : {state}")

        if should_update:
            self.schedule_update_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self._device.name,
            "manufacturer": "HitePro",
            "model": "Relay module",
            "sw_version": "Unknown",
            "via_device": self.hub.hub_id,
        }

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._unique_id

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state.switch;

    def update(self):
        log("UPDATE")
        pass

    def turn_off(self, **kwargs):
        """Turn the device off."""
        log("TURN OFF")

    async def async_turn_off(self, **kwargs):
        log(f"async_turn_off {self._name} : {kwargs}")
        switch_task = self._device.switch(False)
        # switch_task = self.hub.bridge.switch_device(self.device_id,True)
        await switch_task

        self._state.switch = False
        self.schedule_update_ha_state()

    def turn_on(self, **kwargs):
        """Turn the device on."""
        log("TURN ON")

    async def async_turn_on(self, **kwargs):
        log(f"async_turn_off {self._name} : {kwargs}")
        switch_task = self._device.switch(True)
        # switch_task = self.hub.bridge.switch_device(self.device_id,True)
        await switch_task

        self._state.switch = True
        self.schedule_update_ha_state()
