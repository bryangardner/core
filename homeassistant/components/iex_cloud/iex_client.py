"""Client for making requests to IEX Cloud API."""

import logging

import requests

_LOGGER = logging.getLogger(__name__)


class IexUnauthorizedException(Exception):
    """Exception for unauthorized."""


class TickerNotFound(Exception):
    """Exception for invalid ticker."""


class IexClient:
    """Client for fetching IEX Cloud data."""

    def __init__(self, base_url, api_token):
        """Create a new IexClient."""
        self._base_url = base_url
        if not self._base_url.endswith("/"):
            self._base_url += "/"

        self._api_token = api_token

    def get_quote(self, symbol):
        """Fetch the quote info the specified symbol parameter."""
        response = self._do_get("stock/{symbol}/quote".format(symbol=symbol))

        if response.status_code == 404:
            raise TickerNotFound()

        return response.json()

    def _do_get(self, path, params=None):
        """Execute the GET request to IEX API."""
        if params is None:
            params = {}

        request_url = self._base_url + path
        _LOGGER.debug("Executing request to %s with params %s", request_url, params)

        # add auth token
        params["token"] = self._api_token

        response = requests.get(request_url, params=params)
        _LOGGER.debug(
            "Received response %s for request %s", response.status_code, request_url
        )

        if response.status_code in (401, 403):
            raise IexUnauthorizedException()

        return response
