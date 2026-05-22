# Home Assistant Remeha Modbus Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom Home Assistant integration for **Remeha Quinta Ace** gas boilers via the **GTW-08 Modbus gateway**.

## Features

- Reads all relevant sensor data via Modbus TCP
- Flow/return temperature, outside temperature, flue gas temperature
- Water pressure, flow rate, actual power output
- Burner starts and burner hours
- Energy consumption (central heating, domestic hot water, cooling)
- Maintenance status and error codes
- Configuration via the Home Assistant UI (Config Flow)
- Bilingual UI: English and German translations included

## Requirements

- Remeha Quinta Ace gas boiler
- GTW-08 Modbus gateway (connected to the boiler)
- Network connection to the GTW-08 (Modbus TCP, port 502)

## Installation

### HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add repository URL: `https://github.com/klacol/home-assistant-remeha-modbus`
3. Category: Integration
4. Install the integration and restart Home Assistant

### Manual

1. Copy the `custom_components/remeha_modbus` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Settings → Devices & Services → Add Integration
2. Search for "Remeha Modbus"
3. Enter the IP address of the GTW-08 gateway
4. Configure port (default: 502) and slave ID (rotary switch on the GTW-08)

## Sensors

| Sensor | Unit | Description |
|--------|------|-------------|
| Flow Temperature | °C | Supply flow temperature |
| Return Temperature | °C | Return flow temperature |
| Outside Temperature | °C | Measured outside temperature |
| Flue Gas Temperature | °C | Exhaust gas temperature |
| Water Pressure | bar | Current system water pressure |
| Power Actual | % | Current relative power output |
| Burner Starts | - | Total burner start count |
| Burner Hours | h | Total burner operating hours |
| CH Energy Consumption | kWh | Total central heating energy |
| DHW Energy Consumption | kWh | Total domestic hot water energy |
| Service Required | - | Maintenance status |

## Based on

- [remeha-modbus](https://github.com/klacol/remeha-modbus) – Python library for Modbus communication with Remeha heating systems

## Disclaimer

Remeha® is a registered trademark of BDR Thermea Group. This project is not affiliated with, endorsed by, or connected to Remeha or BDR Thermea Group. All product names, trademarks, and registered trademarks are the property of their respective owners.

## License

MIT
