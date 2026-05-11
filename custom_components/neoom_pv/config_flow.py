"""Config flow for Neoom PV Integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_BEAM_IP,
    CONF_BEAM_TOKEN,
    CONF_ENABLE_CALCULATED_SENSORS,
    CONF_MAX_CHARGE_POWER,
    CONF_MAX_DISCHARGE_POWER,
    CONF_MAX_GRID_FEED_IN,
    CONF_MAX_GRID_SUPPLY,
    CONF_MAX_PV_POWER,
    CONF_MIN_SOC_RESERVE,
    CONF_SITE_ID,
    CONF_UPDATE_INTERVAL,
    DEFAULT_ENABLE_CALCULATED,
    DEFAULT_MIN_SOC_RESERVE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Schritt 1: Verbindung
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BEAM_IP): str,
        vol.Required(CONF_BEAM_TOKEN): str,
        vol.Required(CONF_SITE_ID): str,
    }
)

# Schritt 2: Konfiguration
STEP_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BATTERY_CAPACITY, default=0): int,
        vol.Required(CONF_MIN_SOC_RESERVE, default=DEFAULT_MIN_SOC_RESERVE): int,
        vol.Optional(CONF_MAX_CHARGE_POWER, default=0): int,
        vol.Optional(CONF_MAX_DISCHARGE_POWER, default=0): int,
        vol.Optional(CONF_MAX_PV_POWER, default=0): int,
        vol.Optional(CONF_MAX_GRID_FEED_IN, default=0): int,
        vol.Optional(CONF_MAX_GRID_SUPPLY, default=0): int,
        vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=300)
        ),
        vol.Required(
            CONF_ENABLE_CALCULATED_SENSORS,
            default=DEFAULT_ENABLE_CALCULATED,
        ): bool,
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid authentication."""


async def validate_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    session = async_get_clientsession(hass)
    beam_ip = data[CONF_BEAM_IP]
    beam_token = data[CONF_BEAM_TOKEN]

    url = f"http://{beam_ip}/api/v1/site/state"
    headers = {
        "Authorization": f"Bearer {beam_token}",
        "accept": "application/json",
    }

    try:
        async with session.get(url, headers=headers, timeout=10) as resp:
            if resp.status != 200:
                raise InvalidAuth(f"API returned status {resp.status}")

            json_data = await resp.json()
            if "energyFlow" not in json_data:
                raise InvalidData("Antwort enthält keine energyFlow Daten")

            return {"title": f"Neoom PV ({beam_ip})"}

    except Exception as err:
        _LOGGER.error("Validation failed: %s", err)
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neoom PV."""

    VERSION = 1
    user_input_step1: dict[str, Any]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step (Step 1: Connection)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_connection(self.hass, user_input)
                self.user_input_step1 = user_input
                return await self.async_step_config()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the second step (Step 2: Configuration)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Alle Daten zusammenführen
            all_data = {**self.user_input_step1, **user_input}

            # Unique ID setzen (Site ID)
            await self.async_set_unique_id(all_data[CONF_SITE_ID])
            self._abort_if_unique_id_configured()

            _LOGGER.info(
                "Creating config entry for Neoom PV site %s with battery "
                "capacity %s Wh",
                all_data[CONF_SITE_ID],
                all_data[CONF_BATTERY_CAPACITY],
            )

            return self.async_create_entry(
                title=all_data[CONF_BEAM_IP],
                data=all_data,
            )

        # Formular für Schritt 2 anzeigen
        return self.async_show_form(
            step_id="config",
            data_schema=STEP_CONFIG_SCHEMA,
            errors=errors,
        )


class InvalidData(HomeAssistantError):
    """Error to indicate invalid data structure."""
