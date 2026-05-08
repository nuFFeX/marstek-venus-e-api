"""Support for Marstek Venus switch entities."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MarstekVenusCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus switches based on a config entry."""
    coordinator: MarstekVenusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            MarstekVenusChargeSwitch(coordinator),
            MarstekVenusDischargeSwitch(coordinator),
        ]
    )


class MarstekVenusChargeSwitch(
    CoordinatorEntity[MarstekVenusCoordinator], SwitchEntity
):
    """Representation of a Marstek Venus charge permission switch."""

    _attr_has_entity_name = True
    _attr_translation_key = "charge_permission"
    _attr_icon = "mdi:battery-plus-variant"

    def __init__(self, coordinator: MarstekVenusCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_charge_permission"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "Marstek Venus",
            "manufacturer": "Marstek",
            "model": "Venus C/E",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data and "battery" in self.coordinator.data:
            battery_data = self.coordinator.data["battery"]
            if battery_data:
                return battery_data.get("charg_flag")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and "battery" in self.coordinator.data
            and self.coordinator.data["battery"] is not None
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.info("Charge permission control not yet implemented in API")
        # Note: The API documentation doesn't specify how to control charge/discharge flags
        # This would need to be implemented when the API supports it

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.info("Charge permission control not yet implemented in API")


class MarstekVenusDischargeSwitch(
    CoordinatorEntity[MarstekVenusCoordinator], SwitchEntity
):
    """Representation of a Marstek Venus discharge permission switch."""

    _attr_has_entity_name = True
    _attr_translation_key = "discharge_permission"
    _attr_icon = "mdi:battery-minus-variant"

    def __init__(self, coordinator: MarstekVenusCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_discharge_permission"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "Marstek Venus",
            "manufacturer": "Marstek",
            "model": "Venus C/E",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data and "battery" in self.coordinator.data:
            battery_data = self.coordinator.data["battery"]
            if battery_data:
                return battery_data.get("dischrg_flag")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and "battery" in self.coordinator.data
            and self.coordinator.data["battery"] is not None
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.info("Discharge permission control not yet implemented in API")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.info("Discharge permission control not yet implemented in API")
