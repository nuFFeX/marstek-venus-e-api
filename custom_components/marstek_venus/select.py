"""Support for Marstek Venus select entities."""
from __future__ import annotations

import logging
from typing import Any

import asyncio

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_AI, MODE_AUTO, MODE_MANUAL, MODE_PASSIVE, MODES
from .coordinator import MarstekVenusCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus select based on a config entry."""
    coordinator: MarstekVenusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([MarstekVenusModeSelect(coordinator)])


class MarstekVenusModeSelect(CoordinatorEntity[MarstekVenusCoordinator], SelectEntity):
    """Representation of a Marstek Venus operating mode selector."""

    _attr_has_entity_name = True
    _attr_translation_key = "operating_mode"
    _attr_options = MODES

    def __init__(self, coordinator: MarstekVenusCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode_select"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "Marstek Venus",
            "manufacturer": "Marstek",
            "model": "Venus C/E",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current selected mode."""
        if self.coordinator.data and "mode" in self.coordinator.data:
            mode_data = self.coordinator.data["mode"]
            if mode_data:
                return mode_data.get("mode")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected mode."""
        _LOGGER.debug("Changing mode to: %s", option)
        
        try:
            if option == MODE_AUTO:
                result = await self.coordinator.api.set_es_mode_auto()
            elif option == MODE_AI:
                result = await self.coordinator.api.set_es_mode_ai()
            elif option == MODE_PASSIVE:
                # Default passive mode with 100W for 5 minutes
                result = await self.coordinator.api.set_es_mode_passive(power=100, cd_time=300)
            elif option == MODE_MANUAL:
                # Default manual mode - can be extended with service calls
                result = await self.coordinator.api.set_es_mode_manual(
                    time_num=0,
                    start_time="00:00",
                    end_time="23:59",
                    week_set=127,  # All days
                    power=100,
                )
            else:
                _LOGGER.error("Unknown mode: %s", option)
                return
            
            if result is not None:
                _LOGGER.info("Successfully changed mode to: %s", option)
                # Wait for the device to process the mode change before querying status
                await asyncio.sleep(2.0)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to change mode to: %s (no response)", option)
                
        except Exception as err:
            _LOGGER.error("Error changing mode to %s: %s", option, err)
