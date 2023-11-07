"""The Hite-Pro Bridge integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .hub import HiteProHub


import logging
from .const import DOMAIN, CONF_IDENTIFIER, CONF_HOST, CONF_USERNAME, CONF_PASSWORD

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.LIGHT]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Boilerplate."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hite-Pro Bridge from a config entry."""
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
    config = entry.data
    identifier = str(config.get(CONF_IDENTIFIER))
    host = str(config.get(CONF_HOST))
    username = str(config.get(CONF_USERNAME))
    password = str(config.get(CONF_PASSWORD))

    hub = HiteProHub(
        hass, host=host, username=username, password=password
    )

    hass.data[DOMAIN][entry.entry_id] = hub

    await hub.load_devices()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
