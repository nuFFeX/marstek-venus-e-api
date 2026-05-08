"""Binary sensors for Marstek Venus integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CT_STATE_CONNECTED, DOMAIN
from .coordinator import MarstekVenusCoordinator

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus binary sensors."""
    coordinator: MarstekVenusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarstekVenusCTConnectedBinarySensor(coordinator)])


class MarstekVenusCTConnectedBinarySensor(
    CoordinatorEntity[MarstekVenusCoordinator], BinarySensorEntity
):
    """Reports whether the CT clamp / energy meter is connected to the device."""

    _attr_has_entity_name = True
    _attr_translation_key = "ct_connected"
    _attr_name = "CT Connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:current-ac"

    def __init__(self, coordinator: MarstekVenusCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_ct_connected"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "Marstek Venus",
            "manufacturer": "Marstek",
            "model": "Venus C/E",
        }

    @property
    def is_on(self) -> bool | None:
        em: Any = self.coordinator.data.get("em") if self.coordinator.data else None
        if not isinstance(em, dict):
            return None
        state = em.get("ct_state")
        if state is None:
            return None
        return state == CT_STATE_CONNECTED
