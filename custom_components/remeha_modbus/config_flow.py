"""Config flow for Remeha Modbus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.util import slugify

from remeha_modbus import RemehaModbusClient

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE_ID,
    CONF_NAME,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
)

_LOGGER = logging.getLogger(__name__)


@callback
def remeha_modbus_entries(hass: HomeAssistant):
    """Return existing configured hosts."""
    return {
        entry.data[CONF_HOST]
        for entry in hass.config_entries.async_entries(DOMAIN)
    }


class RemehaModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Remeha Modbus."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors: dict[str, str] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RemehaModbusOptionsFlowHandler(config_entry)

    def _host_in_configuration_exists(self, host: str) -> bool:
        """Return True if host already configured."""
        return host in remeha_modbus_entries(self.hass)

    async def _test_connection(self, host: str, port: int, slave_id: int) -> bool:
        """Test if we can connect to the Modbus gateway."""
        client = RemehaModbusClient(host=host, port=port, slave_id=slave_id)
        try:
            connected = await client.connect()
            if not connected:
                self._errors[CONF_HOST] = "cannot_connect"
                return False
            await client.disconnect()
            return True
        except Exception:
            self._errors[CONF_HOST] = "cannot_connect"
            return False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            name = slugify(user_input.get(CONF_NAME, ""))
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            slave_id = user_input.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

            if self._host_in_configuration_exists(host):
                self._errors[CONF_HOST] = "already_configured"
            else:
                can_connect = await self._test_connection(host, port, slave_id)
                if can_connect:
                    return self.async_create_entry(
                        title=name,
                        data={
                            CONF_NAME: name,
                            CONF_HOST: host,
                            CONF_PORT: port,
                            CONF_SLAVE_ID: slave_id,
                        },
                    )
        else:
            user_input = {
                CONF_NAME: "Remeha Quinta Ace",
                CONF_HOST: "",
                CONF_PORT: DEFAULT_PORT,
                CONF_SLAVE_ID: DEFAULT_SLAVE_ID,
            }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=user_input.get(CONF_NAME)): str,
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST)): str,
                    vol.Optional(CONF_PORT, default=user_input.get(CONF_PORT)): int,
                    vol.Optional(CONF_SLAVE_ID, default=user_input.get(CONF_SLAVE_ID)): int,
                }
            ),
            errors=self._errors,
        )


class RemehaModbusOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Remeha Modbus."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            new_data = {**self._config_entry.data, **user_input}
            self.hass.config_entries.async_update_entry(
                self._config_entry, data=new_data
            )
            await self.hass.config_entries.async_reload(self._config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=self._config_entry.data.get(CONF_HOST, ""),
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=self._config_entry.data.get(CONF_PORT, DEFAULT_PORT),
                    ): int,
                    vol.Required(
                        CONF_SLAVE_ID,
                        default=self._config_entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID),
                    ): int,
                }
            ),
        )
