"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import TIME_HOURS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([BoekhoudingSensor()])


class BoekhoudingSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Hours"
    _attr_native_unit_of_measurement = TIME_HOURS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT

    def update(self) -> None:
        """Fetch new state data for the sensor.

        Update the data from the portal."""
        dataurl = "https://boekhouding.wappz.nl/api/ha/hours"
        self.data = ET.parse(urlopen(dataurl)).getroot()
        _LOGGER.debug("Data = %s", self.data)

        """This is the only method that should fetch new data for Home Assistant."""
        self._attr_native_value = 23
