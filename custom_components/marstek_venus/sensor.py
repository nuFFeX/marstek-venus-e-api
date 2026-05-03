"""Support for Marstek Venus sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MarstekVenusCoordinator


@dataclass
class MarstekVenusSensorEntityDescription(SensorEntityDescription):
    """Describes Marstek Venus sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any | None] = lambda data: None


SENSOR_TYPES: tuple[MarstekVenusSensorEntityDescription, ...] = (
    # Battery sensors
    MarstekVenusSensorEntityDescription(
        key="battery_soc",
        translation_key="battery_soc",
        name="Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("soc") if data.get("battery") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="battery_temperature",
        translation_key="battery_temperature",
        name="Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("bat_temp") if data.get("battery") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="battery_capacity",
        translation_key="battery_capacity",
        name="Battery Capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("bat_capacity") if data.get("battery") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="rated_capacity",
        translation_key="rated_capacity",
        name="Rated Capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        value_fn=lambda data: data.get("battery", {}).get("rated_capacity") if data.get("battery") else None,
    ),
    # PV sensors
    MarstekVenusSensorEntityDescription(
        key="pv_power",
        translation_key="pv_power",
        name="Solar Power",
        icon="mdi:solar-power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("pv", {}).get("pv_power") if data.get("pv") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="pv_voltage",
        translation_key="pv_voltage",
        name="Solar Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("pv", {}).get("pv_voltage") if data.get("pv") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="pv_current",
        translation_key="pv_current",
        name="Solar Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("pv", {}).get("pv_current") if data.get("pv") else None,
    ),
    # Energy System sensors
    MarstekVenusSensorEntityDescription(
        key="es_battery_soc",
        translation_key="es_battery_soc",
        name="Total Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("es", {}).get("bat_soc") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="es_battery_capacity",
        translation_key="es_battery_capacity",
        name="Total Battery Capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("es", {}).get("bat_cap") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="ongrid_power",
        translation_key="ongrid_power",
        name="Grid Power",
        icon="mdi:transmission-tower",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("es", {}).get("ongrid_power") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="offgrid_power",
        translation_key="offgrid_power",
        name="Off-Grid Power",
        icon="mdi:home-lightning-bolt",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("es", {}).get("offgrid_power") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="battery_power",
        translation_key="battery_power",
        name="Battery Power",
        icon="mdi:battery-charging",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("es", {}).get("bat_power") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="total_pv_energy",
        translation_key="total_pv_energy",
        name="Total Solar Energy",
        icon="mdi:solar-power",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("es", {}).get("total_pv_energy") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="total_grid_output_energy",
        translation_key="total_grid_output_energy",
        name="Total Grid Output Energy",
        icon="mdi:transmission-tower-export",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("es", {}).get("total_grid_output_energy") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="total_grid_input_energy",
        translation_key="total_grid_input_energy",
        name="Total Grid Input Energy",
        icon="mdi:transmission-tower-import",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("es", {}).get("total_grid_input_energy") if data.get("es") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="total_load_energy",
        translation_key="total_load_energy",
        name="Total Load Energy",
        icon="mdi:home-lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("es", {}).get("total_load_energy") if data.get("es") else None,
    ),
    # Mode sensor
    MarstekVenusSensorEntityDescription(
        key="operating_mode",
        translation_key="operating_mode",
        name="Operating Mode",
        icon="mdi:cog-play",
        value_fn=lambda data: data.get("mode", {}).get("mode") if data.get("mode") else None,
    ),
    # CT / Energy Meter sensors
    MarstekVenusSensorEntityDescription(
        key="ct_total_power",
        translation_key="ct_total_power",
        name="CT Total Power",
        icon="mdi:gauge",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("em", {}).get("total_power") if data.get("em") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="ct_phase_a_power",
        translation_key="ct_phase_a_power",
        name="CT Phase A Power",
        icon="mdi:alpha-a-circle",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("em", {}).get("a_power") if data.get("em") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="ct_phase_b_power",
        translation_key="ct_phase_b_power",
        name="CT Phase B Power",
        icon="mdi:alpha-b-circle",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("em", {}).get("b_power") if data.get("em") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="ct_phase_c_power",
        translation_key="ct_phase_c_power",
        name="CT Phase C Power",
        icon="mdi:alpha-c-circle",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("em", {}).get("c_power") if data.get("em") else None,
    ),
    # WiFi sensors
    MarstekVenusSensorEntityDescription(
        key="wifi_ssid",
        translation_key="wifi_ssid",
        name="WiFi SSID",
        icon="mdi:wifi",
        value_fn=lambda data: data.get("wifi", {}).get("ssid") if data.get("wifi") else None,
    ),
    MarstekVenusSensorEntityDescription(
        key="wifi_rssi",
        translation_key="wifi_rssi",
        name="WiFi Signal Strength",
        native_unit_of_measurement="dBm",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("wifi", {}).get("rssi") if data.get("wifi") else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus sensor based on a config entry."""
    coordinator: MarstekVenusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        MarstekVenusSensor(coordinator, description)
        for description in SENSOR_TYPES
    )


class MarstekVenusSensor(CoordinatorEntity[MarstekVenusCoordinator], SensorEntity):
    """Representation of a Marstek Venus sensor."""

    entity_description: MarstekVenusSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MarstekVenusCoordinator,
        description: MarstekVenusSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "Marstek Venus",
            "manufacturer": "Marstek",
            "model": "Venus C/E",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
