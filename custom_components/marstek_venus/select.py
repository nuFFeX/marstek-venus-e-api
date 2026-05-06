"""Support for Marstek Venus select entities."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_AI, MODE_AUTO, MODE_MANUAL, MODE_PASSIVE, MODE_UPS, MODES
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
    _attr_icon = "mdi:cog-play"
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

    def _current_mode_cfg(self, cfg_key: str) -> dict:
        """Return the current sub-config block from the last known device mode data."""
        try:
            mode_data = self.coordinator.data.get("mode") or {}
            return mode_data.get(cfg_key) or {}
        except Exception:
            return {}

    async def async_select_option(self, option: str) -> None:
        """Change the selected mode."""
        _LOGGER.debug("Changing mode to: %s", option)

        try:
            if option == MODE_AUTO:
                result = await self.coordinator.api.set_es_mode_auto()
            elif option == MODE_AI:
                result = await self.coordinator.api.set_es_mode_ai()
            elif option == MODE_PASSIVE:
                cfg = self._current_mode_cfg("passive_cfg")
                result = await self.coordinator.api.set_es_mode_passive(
                    power=cfg.get("power", 100),
                    cd_time=cfg.get("cd_time", 300),
                )
            elif option == MODE_MANUAL:
                cfg = self._current_mode_cfg("manual_cfg")
                result = await self.coordinator.api.set_es_mode_manual(
                    time_num=cfg.get("time_num", 0),
                    start_time=cfg.get("start_time", "00:00"),
                    end_time=cfg.get("end_time", "23:59"),
                    week_set=cfg.get("week_set", 127),
                    power=cfg.get("power", 100),
                )
            elif option == MODE_UPS:
                result = await self.coordinator.api.set_es_mode_ups()
            else:
                _LOGGER.error("Unknown mode: %s", option)
                return

            if result is not None:
                _LOGGER.info("Successfully changed mode to: %s", option)
                # Flag the next scheduled poll to include ES.GetMode.
                # Do NOT trigger an extra immediate refresh — the device needs
                # time to process the SetMode command, and a burst of requests
                # right after a write is the primary cause of device resets.
                self.coordinator.request_mode_refresh()
            else:
                _LOGGER.error("Failed to change mode to: %s (no response)", option)

        except Exception as err:
            _LOGGER.error("Error changing mode to %s: %s", option, err)
