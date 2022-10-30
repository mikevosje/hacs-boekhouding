"""The example sensor integration."""

from datetime import timedelta
import logging
import asyncio
import logging
import socket
import aiohttp
import async_timeout

from .api import BoekhoudingAPI
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Config entry example."""
    # assuming API object stored here by __init__.py
    session = async_get_clientsession(hass)
    coordinator = Boekhouding(hass, session)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        MyEntity(coordinator)
    )


class Boekhouding(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, session: aiohttp.ClientSession):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Boekhouding Hours",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._session = session

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):

                data = await self._session.async_get_data()
                _LOGGER.debug("Data = %s", data)
                return data
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class MyEntity(CoordinatorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = true;
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()