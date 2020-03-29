"""The IEX Quote integration."""
import asyncio
from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_SECRET, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.util import Throttle

from .const import DOMAIN, TICKER
from .iex_client import IexClient

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS = ["sensor"]

MIN_SCAN_INTERVAL = timedelta(minutes=10)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the IEX Quote component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up IEX Quote from a config entry."""
    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
    hass.data[DOMAIN][entry.entry_id] = IexConnectData(
        hass,
        IexClient(entry.data[CONF_URL], entry.data[CONF_CLIENT_SECRET]),
        entry.data[TICKER],
    )

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class IexConnectData:
    """Define an object to hold sensor data."""

    def __init__(self, hass, client, ticker):
        """Initialize IexConnectData object."""
        self._client = client
        self._ticker = ticker
        self._data = None
        self._last_update = None

    @Throttle(MIN_SCAN_INTERVAL)
    async def async_update(self):
        """Update data via library."""

        try:
            self._data = self._client.get_quote(self._ticker)
            self._last_update = datetime.now()
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error(
                "Error occurred while getting IEX quote for %s",
                self._ticker,
                exc_info=exception,
            )

    def get_ticker(self):
        """Get the ticker."""
        return self._ticker

    def get_data(self):
        """Get the IEX quote data."""
        return self._data

    def get_last_update(self):
        """Get the last update time."""
        return self._last_update
