"""Sensor platform for Remeha Modbus integration."""
import logging

from homeassistant import core, config_entries
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorStateClass,
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfTime,
    UnitOfEnergy,
    PERCENTAGE,
)

from .const import DOMAIN, CONF_NAME, CONF_HOST, CONF_PORT, CONF_SLAVE_ID

_LOGGER = logging.getLogger(__name__)


SENSOR_DEFINITIONS = [
    # Main Controller Monitoring
    {
        "key": "power_setpoint",
        "name": "Power Setpoint",
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "entity_category": None,
    },
    {
        "key": "temperature_setpoint",
        "name": "Temperature Setpoint",
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "entity_category": None,
    },
    {
        "key": "algorithm_type",
        "name": "Control Algorithm Type",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "heat_demand_type",
        "name": "Heat Demand Type",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "power_actual",
        "name": "Power Actual",
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.POWER_FACTOR,
        "entity_category": None,
    },
    {
        "key": "flow_temperature",
        "name": "Flow Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "entity_category": None,
    },
    {
        "key": "return_temperature",
        "name": "Return Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "entity_category": None,
    },
    {
        "key": "producer_status",
        "name": "Producer Status",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "appliance_error",
        "name": "Appliance Error Code",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "appliance_error_priority",
        "name": "Error Priority",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "burner_starts",
        "name": "Burner Starts",
        "unit": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "device_class": None,
        "entity_category": None,
    },
    {
        "key": "burner_hours",
        "name": "Burner Hours",
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "device_class": SensorDeviceClass.DURATION,
        "entity_category": None,
    },
    {
        "key": "service_burning_hours",
        "name": "Burning Hours Since Service",
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.DURATION,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # Appliance Registers
    {
        "key": "outside_temperature",
        "name": "Outside Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "entity_category": None,
    },
    {
        "key": "season_mode",
        "name": "Season Mode",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "flue_gas_temperature",
        "name": "Flue Gas Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "entity_category": None,
    },
    {
        "key": "internal_setpoint",
        "name": "DHW Setpoint",
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "entity_category": None,
    },
    {
        "key": "ch_setpoint",
        "name": "CH Setpoint",
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "entity_category": None,
    },
    {
        "key": "water_pressure",
        "name": "Water Pressure",
        "unit": UnitOfPressure.BAR,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.PRESSURE,
        "entity_category": None,
    },
    {
        "key": "flow_rate",
        "name": "Flow Rate",
        "unit": "l/min",
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": None,
        "entity_category": None,
    },
    {
        "key": "appliance_status",
        "name": "Appliance Status",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "appliance_sub_status",
        "name": "Appliance Sub-Status",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "ionisation_current",
        "name": "Ionisation Current",
        "unit": "µA",
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "ch_energy_consumption",
        "name": "CH Energy Consumption",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "device_class": SensorDeviceClass.ENERGY,
        "entity_category": None,
    },
    {
        "key": "dhw_energy_consumption",
        "name": "DHW Energy Consumption",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "device_class": SensorDeviceClass.ENERGY,
        "entity_category": None,
    },
    {
        "key": "cooling_energy_consumption",
        "name": "Cooling Energy Consumption",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "device_class": SensorDeviceClass.ENERGY,
        "entity_category": None,
    },
    {
        "key": "ch_enabled",
        "name": "Central Heating Enabled",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "dhw_enabled",
        "name": "Domestic Hot Water Enabled",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "cooling_enabled",
        "name": "Cooling Enabled",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # Maintenance Registers
    {
        "key": "service_required",
        "name": "Service Required",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "service_notification",
        "name": "Service Notification",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "service_operating_hours",
        "name": "Operating Hours Since Service",
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.DURATION,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "appliance_on_error",
        "name": "Appliance On Error",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "current_error_1",
        "name": "Error Code 1",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "error_priority_1",
        "name": "Error Priority 1",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    # System Discovery
    {
        "key": "number_of_devices",
        "name": "Number of Devices",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "number_of_zones",
        "name": "Number of Zones",
        "unit": None,
        "state_class": None,
        "device_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
]


def _create_sensors(device_name: str, host: str, port: int, slave_id: int, hass):
    """Create sensor entities for one Remeha device."""
    entities = []
    for sensor_def in SENSOR_DEFINITIONS:
        entities.append(
            RemehaModbusSensor(
                coordinator=hass.data[DOMAIN]["coordinator"],
                device_name=device_name,
                host=host,
                port=port,
                slave_id=slave_id,
                sensor_key=sensor_def["key"],
                sensor_name=sensor_def["name"],
                unit=sensor_def["unit"],
                state_class=sensor_def["state_class"],
                device_class=sensor_def["device_class"],
                entity_category=sensor_def["entity_category"],
            )
        )
    return entities


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up Remeha Modbus sensors from a config entry."""
    _LOGGER.debug("Setting up Remeha Modbus sensors")
    config = config_entry.data

    device_name = config[CONF_NAME]
    host = config[CONF_HOST]
    port = config.get(CONF_PORT, 502)
    slave_id = config.get(CONF_SLAVE_ID, 1)

    async_add_entities(
        _create_sensors(device_name, host, port, slave_id, hass)
    )


class RemehaModbusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Remeha Modbus sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        device_name: str,
        host: str,
        port: int,
        slave_id: int,
        sensor_key: str,
        sensor_name: str,
        unit: str | None,
        state_class: SensorStateClass | None,
        device_class: SensorDeviceClass | None,
        entity_category: EntityCategory | None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_name = device_name
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._sensor_key = sensor_key
        self._attr_translation_key = sensor_key
        self._attr_name = sensor_name
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_device_class = device_class
        if entity_category is not None:
            self._attr_entity_category = entity_category

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device_name)},
            "name": self._device_name,
            "manufacturer": "Remeha",
            "model": "Quinta Ace",
            "configuration_url": f"http://{self._host}",
        }

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._device_name}_{self._sensor_key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        device_data = self.coordinator.data.get(self._device_name)
        if device_data is None:
            return None
        return device_data.get(self._sensor_key)
