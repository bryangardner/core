"""Platform for IEX integration."""
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_ID
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType

from .const import ATTRIBUTION, DOMAIN, IEX_ENTITY_LIST

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up IEX Cloud quote sensor based on a config entry."""
    iex_data = hass.data[DOMAIN][entry.entry_id]
    unique_id = entry.data[CONF_ID]

    try:
        await iex_data.async_update()
    except Exception:  # pylint: disable=broad-except
        _LOGGER.error("Unknown error occurred during IEX update.")

    entities = []
    for (
        sensor_type,
        (name, icon, device_class, enabled_by_default),
    ) in IEX_ENTITY_LIST.items():

        _LOGGER.debug(
            "Registering entity: %s, %s, %s, %s, %s",
            sensor_type,
            name,
            icon,
            device_class,
            enabled_by_default,
        )

        entities.append(
            IexCloudQuoteSensor(
                iex_data,
                unique_id,
                sensor_type,
                name,
                icon,
                device_class,
                enabled_by_default,
            )
        )

    async_add_entities(entities, True)


class IexCloudQuoteSensor(Entity):
    """Representation of IEX Cloud Quote sensor."""

    def __init__(
        self,
        data,
        unique_id,
        sensor_type,
        name,
        icon,
        device_class,
        enabled_default: bool = True,
    ):
        """Initialize."""
        self._data = data
        self._unique_id = unique_id
        self._type = sensor_type
        self._name = name
        self._icon = icon
        self._device_class = device_class
        self._enabled_default = enabled_default
        self._available = True
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._data.get_ticker().upper()} {self._name}"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
        return f"{self._unique_id}_{self._type}"

    # @property
    # def unit_of_measurement(self):
    #     """Return the unit of measurement."""
    #     return self._unit

    @property
    def device_state_attributes(self):
        """Return attributes for sensor."""
        attributes = {
            "source": "IEX Cloud",
            "last_update": self._data.get_last_update(),
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }
        return attributes

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": "IEX Cloud Quote",
            "manufacturer": "IEX Cloud",
        }

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enabled_default

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    async def async_update(self):
        """Update the data from IEX Cloud."""
        if not self.enabled:
            return

        await self._data.async_update()
        data = self._data.get_data()
        if not data:
            _LOGGER.error("Didn't receive data from IEX Cloud")
            return
        if data.get(self._type) is None:
            _LOGGER.debug("Entity type %s not set in fetched data", self._type)
            self._available = False
            return
        self._state = data[self._type]
        self._available = True

        _LOGGER.debug("Entity %s set to state %s", self._type, self._state)
