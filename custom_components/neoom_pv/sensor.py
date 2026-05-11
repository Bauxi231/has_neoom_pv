"""Sensors for Neoom PV Integration."""

import logging
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_DEFINITIONS = {
    "POWER_PRODUCTION": {
        "name": "PV Leistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:solar-power",
    },
    "POWER_CONSUMPTION_CALC": {
        "name": "Verbrauch",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:power-plug",
    },
    "POWER_STORAGE": {
        "name": "Batterie Leistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:battery-charging",
    },
    "POWER_GRID": {
        "name": "Netzleistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:transmission-tower",
    },
    "POWER_CHARGING_STATIONS": {
        "name": "Wallbox Leistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:ev-station",
    },
    "POWER_HEATING": {
        "name": "Heizung Leistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:radiator",
    },
    "POWER_APPLIANCES": {
        "name": "Geräte Leistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:blender",
    },
    "SELF_SUFFICIENCY": {
        "name": "Autarkiegrad",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:leaf-circle",
    },
    "FRACTION_PV_TO_CONSUMPTION": {
        "name": "PV zu Verbrauch",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:solar-power-variant",
    },
    "FRACTION_PV_TO_STORAGE": {
        "name": "PV zu Batterie",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:battery-arrow-up",
    },
    "FRACTION_PV_TO_GRID": {
        "name": "PV zu Netz",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:transmission-tower-export",
    },
    "FRACTION_GRID_TO_CONSUMPTION": {
        "name": "Netz zu Verbrauch",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:transmission-tower-import",
    },
    "FRACTION_GRID_TO_STORAGE": {
        "name": "Netz zu Batterie",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:battery-charging-high",
    },
    "FRACTION_STORAGE_TO_CONSUMPTION": {
        "name": "Batterie zu Verbrauch",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:battery-arrow-down",
    },
    "FRACTION_STORAGE_TO_GRID": {
        "name": "Batterie zu Netz",
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:transmission-tower-export",
    },
    "STATE_OF_CHARGE": {
        "name": "Batterie Ladestand",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "%",
        "icon": "mdi:battery",
    },
    "ENERGY_PRODUCED": {
        "name": "Produzierte Energie",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:solar-power-variant",
    },
    "ENERGY_CONSUMED": {
        "name": "Verbrauchte Energie",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:lightning-bolt",
    },
    "ENERGY_CONSUMED_CALC": {
        "name": "Verbrauchte Energie (Berechnet)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:calculator",
    },
    "ENERGY_CHARGED": {
        "name": "Geladene Energie",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:battery-arrow-up",
    },
    "ENERGY_DISCHARGED": {
        "name": "Entladene Energie",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:battery-arrow-down",
    },
    "ENERGY_IMPORTED": {
        "name": "Netzbezug",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:transmission-tower-import",
    },
    "ENERGY_EXPORTED": {
        "name": "Einspeisung",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:transmission-tower-export",
    },
    "TOTAL_STORAGE_CAPACITY": {
        "name": "Batteriekapazität",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "native_unit_of_measurement": "Wh",
        "icon": "mdi:battery-heart",
        "source": "secrets",
        "secret_key": "neoom_battery_capacity",
    },
    "PRODUCERS_MAX_POWER": {
        "name": "Max. PV-Leistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:solar-power",
        "source": "secrets",
        "secret_key": "neoom_pv_max_power",
    },
    "STORAGES_MAX_POWER": {
        "name": "Max. Batterieleistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:battery-charging",
        "source": "secrets",
        "secret_key": "neoom_battery_max_power",
    },
    "GRIDS_MAX_FEED_IN_POWER": {
        "name": "Max. Einspeiseleistung",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:transmission-tower-export",
        "source": "secrets",
        "secret_key": "neoom_grid_max_feed_in",
    },
    "MAX_NETWORK_UTILIZATION": {
        "name": "Max. Netzanschluss",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit_of_measurement": "W",
        "icon": "mdi:network-pos",
        "source": "secrets",
        "secret_key": "neoom_max_network_utilization",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Neoom PV sensors."""
    data = hass.data["neoom_pv"][entry.entry_id]
    beaam_ip = data["beaam_ip"]
    beaam_token = data["beaam_token"]
    session = data["session"]
    secrets = data.get("secrets", {})

    coordinator = NeoomCoordinator(hass, session, beaam_ip, beaam_token)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for key, config in SENSOR_DEFINITIONS.items():
        sensors.append(NeoomSensor(coordinator, key, config, secrets))

    async_add_entities(sensors, True)


class NeoomCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from Neoom API."""

    def __init__(self, hass, session, beaam_ip, beaam_token):
        """Initialize coordinator."""
        self.session = session
        self.beaam_ip = beaam_ip
        self.beaam_token = beaam_token
        super().__init__(
            hass,
            _LOGGER,
            name="Neoom PV",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        """Fetch data from Neoom API (state only)."""
        state_url = f"http://{self.beaam_ip}/api/v1/site/state"
        headers = {
            "Authorization": f"Bearer {self.beaam_token}",
            "accept": "application/json",
        }
        try:
            async with self.session.get(state_url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    raise Exception(f"State API returned status {resp.status}")
                state_data = await resp.json()
            return {"state": state_data}
        except Exception as err:
            _LOGGER.error("Error fetching Neoom data: %s", err)
            raise err


class NeoomSensor(SensorEntity):
    """Representation of a Neoom Sensor."""

    def __init__(self, coordinator, key, config, secrets):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.key = key
        self._config = config
        self._secrets = secrets
        self._attr_unique_id = f"neoom_{key}"
        self._attr_name = config["name"]
        self._attr_device_class = config["device_class"]
        self._attr_state_class = config["state_class"]
        self._attr_native_unit_of_measurement = config["native_unit_of_measurement"]
        self._attr_icon = config["icon"]
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {("neoom_pv", "beaam")},
            "name": "Neoom BEAAM",
            "manufacturer": "Neoom",
            "model": "BEAAM",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None

        # Statische Werte aus secrets laden
        if self._config.get("source") == "secrets":
            secret_key = self._config.get("secret_key")
            if secret_key in self._secrets:
                val = self._secrets[secret_key]
                try:
                    return float(val) if "." in str(val) else int(float(val))
                except (ValueError, TypeError):
                    return None
            else:
                _LOGGER.warning("Secret %s not found in secrets.yaml", secret_key)
                return None

        # Dynamische Werte aus energyFlow/states laden
        state_data = data.get("state", {})
        if "energyFlow" not in state_data:
            return None

        states = state_data["energyFlow"].get("states", [])
        for state in states:
            if state.get("key") == self.key:
                return state.get("value")

        return None

    @property
    def available(self):
        """Return if sensor is available."""
        return self.coordinator.last_update_success
