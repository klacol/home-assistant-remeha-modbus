"""Remeha Modbus integration for Home Assistant."""
import logging
from datetime import timedelta

from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from remeha_modbus import RemehaModbusClient

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE_ID,
    CONF_NAME,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up remeha_modbus platform."""
    hass.data.setdefault(DOMAIN, {"api": {}, "coordinator": None})
    return True


async def async_setup_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Remeha Modbus from a config entry."""
    _LOGGER.info("Setting up Remeha Modbus entry: %s", entry.data[CONF_NAME])

    hass.data.setdefault(DOMAIN, {"api": {}})

    name = entry.data[CONF_NAME]
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

    client = RemehaModbusClient(host=host, port=port, slave_id=slave_id)
    hass.data[DOMAIN]["api"][name] = client

    async def _async_update_data():
        """Fetch data from Remeha via Modbus."""
        data = {}
        clients = hass.data[DOMAIN]["api"]
        for client_name, client_instance in clients.items():
            if not client_instance.connected:
                await client_instance.connect()
            try:
                fetched = await client_instance.read_all_sensors()
                data[client_name] = fetched
            except Exception as err:
                _LOGGER.error("Error fetching data from %s: %s", client_name, err)
                data[client_name] = {}
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=_async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    hass.data[DOMAIN]["coordinator"] = coordinator

    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def update_listener(hass: core.HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    name = entry.data[CONF_NAME]
    _LOGGER.info("Unloading Remeha Modbus: %s", name)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        client = hass.data[DOMAIN]["api"].pop(name, None)
        if client and client.connected:
            await client.disconnect()
    return unload_ok
