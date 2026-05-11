"""Coordinator for Neoom PV Integration."""
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_ENDPOINT_CONFIG,
    API_ENDPOINT_STATE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class NeoomCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Neoom data."""

    def __init__(
        self,
        hass: HomeAssistant,
        beaam_ip: str,
        beaam_token: str,
        update_interval: int = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize global data updater."""
        self.beaam_ip = beaam_ip
        self.beaam_token = beaam_token
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Neoom API."""
        state_url = f"http://{self.beaam_ip}{API_ENDPOINT_STATE}"
        config_url = f"http://{self.beaam_ip}{API_ENDPOINT_CONFIG}"

        headers = {
            "Authorization": f"Bearer {self.beaam_token}",
            "accept": "application/json",
        }

        try:
            # State-Daten abrufen (Echtzeit)
            async with self.session.get(
                state_url, headers=headers, timeout=10
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(
                        f"State API returned status {resp.status}"
                    )
                state_data = await resp.json()

            # Config-Daten abrufen (statisch, seltener)
            config_data = {}
            async with self.session.get(
                config_url, headers=headers, timeout=10
            ) as resp:
                if resp.status == 200:
                    config_data = await resp.json()
                else:
                    _LOGGER.warning(
                        "Config API returned status %s", resp.status
                    )

            return {
                "state": state_data,
                "configuration": config_data,
            }

        except Exception as err:
            _LOGGER.error("Error fetching Neoom data: %s", err)
            raise UpdateFailed(
                f"Error communicating with API: {err}"
            ) from err
