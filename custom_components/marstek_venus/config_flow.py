"""Config flow for Marstek Venus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api import MarstekVenusAPI
from .const import CONF_BLE_MAC, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_BLE_MAC, default="0"): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = MarstekVenusAPI(data[CONF_HOST], data.get(CONF_PORT, DEFAULT_PORT))
    
    # Try to discover device
    device_info = await api.discover_device(data.get(CONF_BLE_MAC, "0"))
    
    if not device_info:
        raise CannotConnect("Could not connect to device")
    
    # Return info that you want to store in the config entry.
    return {
        "title": f"{device_info.get('device', 'Marstek Venus')} ({data[CONF_HOST]})",
        "device_info": device_info,
    }


class MarstekVenusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Marstek Venus."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create unique ID from BLE MAC if available
                if device_info := info.get("device_info"):
                    if ble_mac := device_info.get("ble_mac"):
                        await self.async_set_unique_id(ble_mac)
                        self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
