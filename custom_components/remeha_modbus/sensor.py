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

from remeha_modbus import NOT_SUPPORTED
from remeha_modbus.registers import (
    ALL_REGISTERS,
    DataType,
    RegisterDefinition,
    get_zone_registers,
)

from .const import DOMAIN, CONF_NAME, CONF_HOST, CONF_PORT, CONF_SLAVE_ID

_LOGGER = logging.getLogger(__name__)


# Mapping from library unit strings to HA unit constants
_UNIT_MAP = {
    "°C": UnitOfTemperature.CELSIUS,
    "bar": UnitOfPressure.BAR,
    "h": UnitOfTime.HOURS,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "%": PERCENTAGE,
}

# Registers that represent total counters (state_class = TOTAL_INCREASING)
_TOTAL_INCREASING_KEYS = {
    "burner_starts", "burner_hours",
    "ch_energy_consumption", "dhw_energy_consumption", "cooling_energy_consumption",
}


def _derive_sensor_attrs(register: RegisterDefinition) -> dict:
    """Derive HA sensor attributes from a register definition."""
    unit = _UNIT_MAP.get(register.unit, register.unit or None)
    device_class = None
    state_class = None
    entity_category = None

    # Determine device_class from unit
    if register.unit == "°C":
        device_class = SensorDeviceClass.TEMPERATURE
        state_class = SensorStateClass.MEASUREMENT
    elif register.unit == "bar":
        device_class = SensorDeviceClass.PRESSURE
        state_class = SensorStateClass.MEASUREMENT
    elif register.unit == "kWh":
        device_class = SensorDeviceClass.ENERGY
        state_class = SensorStateClass.TOTAL_INCREASING
    elif register.unit == "h":
        device_class = SensorDeviceClass.DURATION
        state_class = SensorStateClass.MEASUREMENT
    elif register.unit == "%":
        device_class = SensorDeviceClass.POWER_FACTOR
        state_class = SensorStateClass.MEASUREMENT
    elif register.unit == "l/min":
        state_class = SensorStateClass.MEASUREMENT

    # Override for known counters
    if register.name in _TOTAL_INCREASING_KEYS:
        state_class = SensorStateClass.TOTAL_INCREASING

    # === STAMMDATEN (Diagnostic) ===
    # Technical info that rarely changes
    stammdaten_keywords = [
        "firmware", "serial", "model", "number_of_", "device_id",
        "product_", "version", "configuration"
    ]
    
    # === STATISTIKEN (Diagnostic) ===
    # Counters and historical data
    statistik_keywords = [
        "burner_starts", "burner_hours", "pump_starts", "pump_hours",
        "energy_consumption", "operating_hours", "total_", "counter"
    ]
    
    # Enum, status, and error registers are diagnostics
    if register.data_type in (DataType.ENUM8, DataType.BOOL8):
        entity_category = EntityCategory.DIAGNOSTIC
        state_class = None
        device_class = None
    elif "error" in register.name or "status" in register.name or "state" in register.name:
        entity_category = EntityCategory.DIAGNOSTIC
    # Stammdaten
    elif any(keyword in register.name for keyword in stammdaten_keywords):
        entity_category = EntityCategory.DIAGNOSTIC
    # Statistiken (Zähler als Diagnostic, aber behalten state_class für Energy Dashboard)
    elif any(keyword in register.name for keyword in statistik_keywords):
        entity_category = EntityCategory.DIAGNOSTIC

    # Pretty name from register name
    name = register.name.replace("_", " ").title()

    return {
        "key": register.name,
        "name": name,
        "unit": unit,
        "state_class": state_class,
        "device_class": device_class,
        "entity_category": entity_category,
    }


def _build_sensor_definitions() -> list[dict]:
    """Build sensor definitions from the library's ALL_REGISTERS."""
    definitions = []
    for register in ALL_REGISTERS:
        definitions.append(_derive_sensor_attrs(register))
    return definitions


SENSOR_DEFINITIONS = _build_sensor_definitions()


def _build_zone_sensor_definitions(zone_number: int) -> list[dict]:
    """Build sensor definitions for a specific zone."""
    definitions = []
    for register in get_zone_registers(zone_number):
        definitions.append(_derive_sensor_attrs(register))
    return definitions


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
    slave_id = config.get(CONF_SLAVE_ID, 100)

    coordinator = hass.data[DOMAIN]["coordinator"]
    model = hass.data[DOMAIN].get("model")

    # Create main sensors from ALL_REGISTERS
    entities = []
    for sensor_def in SENSOR_DEFINITIONS:
        entities.append(
            RemehaModbusSensor(
                coordinator=coordinator,
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
                model=model,
            )
        )

    # Create zone sensors if zones were discovered
    data = coordinator.data or {}
    device_data = data.get(device_name, {})
    num_zones = device_data.get("number_of_zones") or 0
    if isinstance(num_zones, int) and num_zones > 0:
        for zone_num in range(1, min(num_zones, 12) + 1):
            zone_defs = _build_zone_sensor_definitions(zone_num)
            for sensor_def in zone_defs:
                entities.append(
                    RemehaModbusSensor(
                        coordinator=coordinator,
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
                        model=model,
                    )
                )

    async_add_entities(entities)


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
        model: str | None = None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_name = device_name
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._sensor_key = sensor_key
        self._model = model
        self._attr_translation_key = sensor_key
        # Don't set _attr_name - let translation_key handle the name
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
            "model": self._model or "Unknown",
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
        value = device_data.get(self._sensor_key)
        if isinstance(value, type(NOT_SUPPORTED)):
            return None
        return value
