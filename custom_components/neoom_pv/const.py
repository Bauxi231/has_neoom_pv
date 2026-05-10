"""Constants for the Neoom PV integration."""
from typing import Final

# Domain-Name (muss mit manifest.json übereinstimmen)
DOMAIN: Final = "neoom_pv"

# Plattformen, die wir unterstützen
PLATFORMS: Final[list[str]] = ["sensor"]

# API-Konfiguration
CONF_BEAM_IP: Final = "beaam_ip"
CONF_BEAM_TOKEN: Final = "beaam_token"
CONF_SITE_ID: Final = "site_id"

# Neue Konfigurations-Keys für Schritt 2
CONF_BATTERY_CAPACITY: Final = "battery_capacity"
CONF_MIN_SOC_RESERVE: Final = "min_soc_reserve"
CONF_MAX_CHARGE_POWER: Final = "max_charge_power"
CONF_MAX_DISCHARGE_POWER: Final = "max_discharge_power"
CONF_MAX_PV_POWER: Final = "max_pv_power"
CONF_MAX_GRID_FEED_IN: Final = "max_grid_feed_in"
CONF_MAX_GRID_SUPPLY: Final = "max_grid_supply"
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_ENABLE_CALCULATED_SENSORS: Final = "enable_calculated_sensors"

# Update-Intervall (Default: 30 Sekunden)
DEFAULT_UPDATE_INTERVAL: Final[int] = 30
DEFAULT_MIN_SOC_RESERVE: Final[int] = 10
DEFAULT_ENABLE_CALCULATED: Final[bool] = True

# API-Endpunkte
API_ENDPOINT_STATE: Final = "/api/v1/site/state"
API_ENDPOINT_CONFIG: Final = "/api/v1/site/configuration"

# Sensor-Keys aus der API
SENSOR_KEYS = {
    # Leistung (W)
    "POWER_PRODUCTION": "pv_leistung",
    "POWER_CONSUMPTION_CALC": "verbrauch",
    "POWER_STORAGE": "batterie_leistung",
    "POWER_GRID": "netzleistung",
    "POWER_CHARGING_STATIONS": "wallbox_leistung",
    "POWER_HEATING": "heizung_leistung",
    "POWER_APPLIANCES": "geraete_leistung",
    
    # Energie-Fraktionen (%)
    "SELF_SUFFICIENCY": "autarkiegrad",
    "FRACTION_PV_TO_CONSUMPTION": "pv_zu_verbrauch",
    "FRACTION_PV_TO_STORAGE": "pv_zu_batterie",
    "FRACTION_PV_TO_GRID": "pv_zu_netz",
    "FRACTION_GRID_TO_CONSUMPTION": "netz_zu_verbrauch",
    "FRACTION_GRID_TO_STORAGE": "netz_zu_batterie",
    "FRACTION_STORAGE_TO_CONSUMPTION": "batterie_zu_verbrauch",
    "FRACTION_STORAGE_TO_GRID": "batterie_zu_netz",
    
    # Energie (Wh)
    "ENERGY_PRODUCED": "produzierte_energie",
    "ENERGY_CONSUMED": "verbrauchte_energie",
    "ENERGY_CONSUMED_CALC": "verbrauchte_energie_berechnet",
    "ENERGY_CHARGED": "geladene_energie",
    "ENERGY_DISCHARGED": "entladene_energie",
    "ENERGY_IMPORTED": "netzbezug",
    "ENERGY_EXPORTED": "einspeisung",
    
    # Status
    "STATE_OF_CHARGE": "batterie_ladestand",
}

# Statische Konfigurations-Keys (werden jetzt aus Config Flow geladen)
CONFIG_KEYS = {
    "total_storage_capacity": "batteriekapazaet",
    "producers_max_power": "max_pv_leistung",
    "storages_max_power": "max_batterie_leistung",
    "grids_max_feed_in_power": "max_einspeiseleistung",
    "max_network_utilization": "max_netzanschluss",
}
