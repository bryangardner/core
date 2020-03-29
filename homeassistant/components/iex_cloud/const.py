"""Constants for the IEX Quote integration."""

DOMAIN = "iex_cloud"

TICKER = "iex_ticker"

ATTRIBUTION = "Data provided by IEX Cloud"

IEX_ENTITY_LIST = {
    "symbol": ["Symbol", "mdi:currency-usd", None, True],
    "open": ["Open", "mdi:currency-usd", None, True],
    "close": ["Close", "mdi:currency-usd", None, True],
    "high": ["High", "mdi:currency-usd", None, True],
    "low": ["Low", "mdi:currency-usd", None, True],
    "volume": ["Volume", "mdi:poll-box", None, True],
}
