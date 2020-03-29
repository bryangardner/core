"""Config flow for IEX Quote integration."""
import logging

import requests
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_CLIENT_SECRET, CONF_ID, CONF_URL

from .const import DOMAIN, TICKER  # pylint:disable=unused-import
from .iex_client import IexClient, IexUnauthorizedException, TickerNotFound

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL, default="https://cloud.iexapis.com/stable"): str,
        vol.Required(CONF_CLIENT_SECRET): str,
        vol.Required(TICKER): str,
    }
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    def validate(url_root, api_secret, ticker):
        iex_client = IexClient(url_root, api_secret)
        try:
            quote = iex_client.get_quote(ticker)
            _LOGGER.debug("VALIDATION: %s", quote)
            if quote is not None and quote is not {}:
                return "iex-quote-{ticker}".format(ticker=ticker)
            raise CannotConnect()
        except requests.exceptions.RequestException:
            raise CannotConnect()

    return await hass.async_add_executor_job(
        validate, data[CONF_URL], data[CONF_CLIENT_SECRET], data[TICKER]
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IEX Quote."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                unique_id = await validate_input(self.hass, user_input)
                user_input[CONF_ID] = unique_id

                return self.async_create_entry(title=unique_id, data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except IexUnauthorizedException:
                errors["base"] = "invalid_auth"
            except TickerNotFound:
                errors["base"] = "ticker_not_found"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
