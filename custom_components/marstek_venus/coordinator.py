"""Data coordinator for Marstek Venus integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MarstekVenusAPI
from .const import CONF_HOST, CONF_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MarstekVenusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Marstek Venus data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.api = MarstekVenusAPI(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, 30000),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            new_data = await self.api.get_all_status()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

        keys = ("battery", "pv", "es", "mode", "wifi", "ble")
        if self.data is None:
            if all(new_data.get(k) is None for k in keys):
                raise UpdateFailed("No data received from device")
            return new_data

        merged = dict(self.data)
        for key in keys:
            if new_data.get(key) is not None:
                merged[key] = new_data[key]
        return merged
