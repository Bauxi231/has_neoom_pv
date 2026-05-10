"""Setup the Neoom PV integration."""
import logging
import yaml
from pathlib import Path
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "neoom_pv"
PLATFORMS = ["sensor"]

# Da wir nur Config Flow nutzen, definieren wir ein leeres Schema für YAML
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Neoom PV component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Neoom PV from a config entry."""
    
    # Daten aus der Konfiguration holen
    beaam_ip = entry.data.get("beaam_ip")
    beaam_token = entry.data.get("beaam_token")
    site_id = entry.data.get("site_id")

    if not all([beaam_ip, beaam_token, site_id]):
        _LOGGER.error("Missing configuration data for Neoom PV")
        return False

    # secrets.yaml laden für statische Werte
    secrets = {}
    secrets_path = Path("/config/secrets.yaml")
    if secrets_path.exists():
        try:
            with open(secrets_path, "r") as f:
                secrets = yaml.safe_load(f) or {}
            _LOGGER.info("Loaded %d secrets from secrets.yaml", len(secrets))
        except Exception as err:
            _LOGGER.error("Failed to load secrets.yaml: %s", err)
    else:
        _LOGGER.warning("secrets.yaml not found at /config/secrets.yaml")

    # Session für HTTP-Requests erstellen
    session = async_get_clientsession(hass)

    # Test: API erreichen
    try:
        url = f"http://{beaam_ip}/api/v1/site/state"
        headers = {
            "Authorization": f"Bearer {beaam_token}",
            "accept": "application/json"
        }
        
        async with session.get(url, headers=headers, timeout=10) as resp:
            if resp.status != 200:
                raise ConfigEntryNotReady(f"API returned status {resp.status}")
            
            data = await resp.json()
            _LOGGER.info("Successfully connected to Neoom BEAAM API. Data keys: %s", list(data.keys()))
            
    except Exception as err:
        _LOGGER.error("Failed to connect to Neoom BEAAM API: %s", err)
        raise ConfigEntryNotReady(err)

    # Konfiguration speichern, damit andere Module (sensors.py) darauf zugreifen können
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "beaam_ip": beaam_ip,
        "beaam_token": beaam_token,
        "site_id": site_id,
        "session": session,
        "data": data,
        "secrets": secrets,
    }

    # Sensoren laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
