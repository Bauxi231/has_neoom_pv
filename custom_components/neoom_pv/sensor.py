"""Sensors for the Neoom PV integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_KEYS,
    CONFIG_KEYS,
    CONF_BATTERY_CAPACITY,
    CONF_MAX_PV_POWER,
    CONF_MAX_CHARGE_POWER,
    CONF_MAX_DISCHARGE_POWER,
    CONF_MAX_GRID_FEED_IN,
    CONF_MAX_GRID_SUPPLY,
)
from .coordinator import NeoomCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Neoom PV sensors."""
    coordinator: NeoomCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    config: dict[str, Any] = hass.data[DOMAIN][entry.entry_id]["config"]

    # Dynamische Sensoren aus State-Daten
    dynamic_sensors = []
    for api_key, entity_name in SENSOR_KEYS.items():
        dynamic_sensors.append(
            NeoomSensor(coordinator, api_key, entity_name, "dynamic", config)
        )

    # Statische Sensoren aus Config (nicht mehr aus secrets.yaml!)
    static_sensors = []
    for api_key, entity_name in CONFIG_KEYS.items():
        static_sensors.append(
            NeoomSensor(coordinator, api_key, entity_name, "static", config)
        )

    async_add_entities(dynamic_sensors + static_sensors, True)


class NeoomSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Neoom Sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: NeoomCoordinator,
        api_key: str,
        entity_name: str,
        data_source: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.api_key = api_key
        self.entity_name = entity_name
        self.data_source = data_source
        self.config = config

        # Unique ID und Name setzen
        self._attr_unique_id = f"{coordinator.beaam_ip}_{api_key}"
        self._attr_name = entity_name.replace("_", " ").title()
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.beaam_ip)},
            "name": f"Neoom BEAAM ({coordinator.beaam_ip})",
            "manufacturer": "Neoom",
            "model": "BEAAM",
        }

        # Device Class und Unit basierend auf dem Key setzen
        self._setup_sensor_properties(api_key)

    def _setup_sensor_properties(self, api_key: str) -> None:
        """Set device class and unit based on API key."""
        # Leistung (W)
        if api_key.startswith("POWER_"):
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = "W"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:flash"
        # Energie (Wh)
        elif api_key.startswith("ENERGY_"):
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = "Wh"
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_icon = "mdi:lightning-bolt"
        # Ladestand (%)
        elif api_key == "STATE_OF_CHARGE":
            self._attr_device_class = SensorDeviceClass.BATTERY
            self._attr_native_unit_of_measurement = "%"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:battery"
        # Fraktionen (%)
        elif api_key.startswith("FRACTION_") or api_key == "SELF_SUFFICIENCY":
            self._attr_device_class = SensorDeviceClass.POWER_FACTOR
            self._attr_native_unit_of_measurement = "%"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:chart-pie"
        # Statische Werte (Kapazität in Wh)
        elif api_key in ["total_storage_capacity"]:
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = "Wh"
            self._attr_state_class = SensorStateClass.TOTAL
            self._attr_icon = "mdi:battery-heart"
        # Statische Werte (Leistung in W)
        elif api_key in [
            "producers_max_power",
            "storages_max_power",
            "grids_max_feed_in_power",
            "max_network_utilization",
        ]:
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = "W"
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:gauge"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None

        if self.data_source == "static":
            # Statische Werte aus Config laden (NICHT mehr aus secrets.yaml!)
            config_mapping = {
                "total_storage_capacity": CONF_BATTERY_CAPACITY,
                "producers_max_power": CONF_MAX_PV_POWER,
                "storages_max_power": CONF_MAX_DISCHARGE_POWER,
                "grids_max_feed_in_power": CONF_MAX_GRID_FEED_IN,
                "max_network_utilization": CONF_MAX_GRID_SUPPLY,
            }

            config_key = config_mapping.get(self.api_key)
            if config_key and config_key in self.config:
                val = self.config[config_key]
                try:
                    return float(val) if '.' in str(val) else int(float(val))
                except (ValueError, TypeError):
                    return None
            return None

        else:
            # Dynamische Werte aus energyFlow/states laden
            state_data = data.get("state", {})
            if "energyFlow" not in state_data:
                return None

            states = state_data["energyFlow"].get("states", [])
            for state in states:
                if state.get("key") == self.api_key:
                    return state.get("value")

            return None
