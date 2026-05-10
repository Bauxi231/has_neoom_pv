"""Setup the Neoom PV integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_BEAM_IP,
    CONF_BEAM_TOKEN,
    CONF_SITE_ID,
    CONF_BATTERY_CAPACITY,
    CONF_MIN_SOC_RESERVE,
    CONF_MAX_CHARGE_POWER,
    CONF_MAX_DISCHARGE_POWER,
    CONF_MAX_PV_POWER,
    CONF_MAX_GRID_FEED_IN,
    CONF_MAX_GRID_SUPPLY,
    CONF_UPDATE_INTERVAL,
    CONF_ENABLE_CALCULATED_SENSORS,
    DEFAULT_UPDATE_INTERVAL,
)
from .coordinator import NeoomCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Neoom PV component."""
    _LOGGER.debug("Setting up Neoom PV component")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Neoom PV from a config entry."""
    _LOGGER.debug("Setting up Neoom PV config entry")

    # Daten aus der Konfiguration holen
    beaam_ip = entry.data.get(CONF_BEAM_IP)
    beaam_token = entry.data.get(CONF_BEAM_TOKEN)
    site_id = entry.data.get(CONF_SITE_ID)
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    if not all([beaam_ip, beaam_token, site_id]):
        _LOGGER.error("Missing configuration data for Neoom PV")
        return False

    # Coordinator erstellen (mit konfigurierbarem Update-Intervall)
    coordinator = NeoomCoordinator(
        hass,
        beaam_ip,
        beaam_token,
        update_interval=update_interval,
    )

    # Ersten Datenabruf durchführen (prüft API-Konnektivität)
    await coordinator.async_config_entry_first_refresh()

    # Alle Konfigurationswerte in hass.data speichern
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "site_id": site_id,
        "config": {
            CONF_BATTERY_CAPACITY: entry.data.get(CONF_BATTERY_CAPACITY, 0),
            CONF_MIN_SOC_RESERVE: entry.data.get(CONF_MIN_SOC_RESERVE, 10),
            CONF_MAX_CHARGE_POWER: entry.data.get(CONF_MAX_CHARGE_POWER, 0),
            CONF_MAX_DISCHARGE_POWER: entry.data.get(CONF_MAX_DISCHARGE_POWER, 0),
            CONF_MAX_PV_POWER: entry.data.get(CONF_MAX_PV_POWER, 0),
            CONF_MAX_GRID_FEED_IN: entry.data.get(CONF_MAX_GRID_FEED_IN, 0),
            CONF_MAX_GRID_SUPPLY: entry.data.get(CONF_MAX_GRID_SUPPLY, 0),
            CONF_UPDATE_INTERVAL: update_interval,
            CONF_ENABLE_CALCULATED_SENSORS: entry.data.get(CONF_ENABLE_CALCULATED_SENSORS, True),
        },
    }

    _LOGGER.info(
        "Successfully set up Neoom PV integration for site %s (update interval: %ss, battery capacity: %sWh)",
        site_id,
        update_interval,
        entry.data.get(CONF_BATTERY_CAPACITY, 0),
    )

    # Sensoren laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Neoom PV config entry")

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info("Successfully unloaded Neoom PV integration")
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    _LOGGER.debug("Reloading Neoom PV config entry")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
