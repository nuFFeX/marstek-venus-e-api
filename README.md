# Marstek Venus Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant custom integration for Marstek Venus C/E energy storage systems using the local UDP API.

## Features

- 🔋 **Battery Monitoring**: SOC, temperature, capacity
- ☀️ **Solar Monitoring**: Power, voltage, current
- ⚡ **Energy System**: Grid power, off-grid power, battery power
- 📊 **Energy Statistics**: Total solar, grid input/output, load consumption
- 🎛️ **Mode Control**: Auto, AI, Manual, and Passive operating modes
- 📡 **Network Info**: WiFi SSID and signal strength
- 🌍 **Multi-language**: English and German translations

## Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install" on the Marstek Venus integration
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/marstek_venus` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

### Prerequisites

Before configuring the integration, ensure:

1. Your Marstek Venus device is connected to your home network
2. The Local API feature is enabled in the Marstek APP
3. Note the device's IP address (you can find this in your router or the Marstek APP)
4. The UDP port is configured (default: 30000)

### Setup via UI

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for "Marstek Venus"
4. Enter your device details:
   - **IP Address**: The local IP address of your Marstek device
   - **UDP Port**: The UDP port (default: 30000)
   - **Bluetooth MAC**: Optional, use "0" for automatic discovery
5. Click **Submit**

## Entities

After successful configuration, the following entities will be created:

### Sensors

#### Battery
- `sensor.marstek_venus_battery_soc` - Battery state of charge (%)
- `sensor.marstek_venus_battery_temperature` - Battery temperature (°C)
- `sensor.marstek_venus_battery_capacity` - Current battery capacity (Wh)
- `sensor.marstek_venus_rated_capacity` - Rated battery capacity (Wh)

#### Solar (PV)
- `sensor.marstek_venus_solar_power` - Current solar power (W)
- `sensor.marstek_venus_solar_voltage` - Solar voltage (V)
- `sensor.marstek_venus_solar_current` - Solar current (A)

#### Energy System
- `sensor.marstek_venus_total_battery_soc` - Total battery SOC (%)
- `sensor.marstek_venus_total_battery_capacity` - Total battery capacity (Wh)
- `sensor.marstek_venus_grid_power` - Grid power (W)
- `sensor.marstek_venus_off_grid_power` - Off-grid power (W)
- `sensor.marstek_venus_battery_power` - Battery power (W)
- `sensor.marstek_venus_total_solar_energy` - Total solar energy generated (Wh)
- `sensor.marstek_venus_total_grid_output_energy` - Total energy sent to grid (Wh)
- `sensor.marstek_venus_total_grid_input_energy` - Total energy from grid (Wh)
- `sensor.marstek_venus_total_load_energy` - Total load consumption (Wh)
- `sensor.marstek_venus_operating_mode` - Current operating mode

#### Network
- `sensor.marstek_venus_wifi_ssid` - Connected WiFi network name
- `sensor.marstek_venus_wifi_signal_strength` - WiFi signal strength (dBm)

### Select
- `select.marstek_venus_operating_mode` - Control operating mode (Auto/AI/Manual/Passive)

### Switches
- `switch.marstek_venus_charge_permission` - Battery charge permission (read-only)
- `switch.marstek_venus_discharge_permission` - Battery discharge permission (read-only)

## Operating Modes

### Auto Mode
The device automatically manages energy flow based on solar availability and battery state.

### AI Mode
AI-powered optimization based on usage patterns and energy prices (if supported by device).

### Manual Mode
Manual control with time-based schedules. Default settings when activated:
- Time: 00:00 - 23:59
- Days: All week (127)
- Power: 100W

### Passive Mode
Passive power control with countdown timer. Default settings:
- Power: 100W
- Countdown: 300 seconds (5 minutes)

## Energy Dashboard Integration

This integration is compatible with Home Assistant's Energy Dashboard. Add the following sensors:

- **Solar Production**: `sensor.marstek_venus_total_solar_energy`
- **Grid Consumption**: `sensor.marstek_venus_total_grid_input_energy`
- **Grid Return**: `sensor.marstek_venus_total_grid_output_energy`
- **Battery Energy**: Use `sensor.marstek_venus_battery_power` for real-time monitoring

## Automation Examples

### Switch to Auto Mode at Sunrise
```yaml
automation:
  - alias: "Marstek Auto Mode at Sunrise"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: select.select_option
        target:
          entity_id: select.marstek_venus_operating_mode
        data:
          option: "Auto"
```

### Notify on Low Battery
```yaml
automation:
  - alias: "Marstek Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.marstek_venus_battery_soc
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "Low Battery Warning"
          message: "Marstek battery is at {{ states('sensor.marstek_venus_battery_soc') }}%"
```

### Switch to Passive Mode During Peak Hours
```yaml
automation:
  - alias: "Marstek Peak Hours Management"
    trigger:
      - platform: time
        at: "17:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.marstek_venus_operating_mode
        data:
          option: "Passive"
```

## Troubleshooting

### Connection Issues
- Verify the device IP address is correct
- Ensure the UDP port is open and matches the configuration
- Check that Local API is enabled in the Marstek APP
- Verify both devices are on the same network

### No Data Updates
- Check the device is powered on
- Verify network connectivity
- Review Home Assistant logs for error messages
- Try reloading the integration

### Entities Not Appearing
- Restart Home Assistant after installation
- Check that the integration loaded successfully in logs
- Verify the device supports the requested features

## Advanced Configuration

### Static IP Recommendation
For reliable operation, configure a static IP address for your Marstek device in your router's DHCP settings.

### Firewall Configuration
Ensure UDP port 30000 (or your configured port) is not blocked by firewalls.

## API Documentation

This integration implements the Marstek Device Open API (REV 0.5). For detailed API documentation, refer to the official Marstek API documentation.

## Support

For issues, feature requests, or questions:
- Open an issue on [GitHub](https://github.com/yourusername/marstek-venus-hacs/issues)
- Check existing issues for solutions

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by Marstek. Use at your own risk.

## Credits

Developed based on the Marstek Device Open API documentation (REV 0.5).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history.

### Version 0.1.3 (2026-03-29)
- UDP timeouts use the full configured wait; poll spacing 1.0s; HACS `hacs.json` schema-compliant (no `domains`)

### Version 0.1.2 (2026-03-28)
- Correct WiFi RPC method name (`Wifi.GetStatus`) for Venus E
- No `PV.GetStatus` in poll; PV from `ES.GetStatus`; UDP id-matching and longer timeouts
- Coordinator keeps last good values when a poll partially fails

### Version 0.1.1 (2026-03-28)
- Serial UDP status requests and comm lock (no parallel gather)
- Device error responses logged; PV fallback from ES

### Version 0.1.0 (Initial Release)
- Initial implementation
- Support for all major sensors (Battery, PV, ES)
- Operating mode control (Auto/AI/Manual/Passive)
- Network monitoring (WiFi)
- Multi-language support (EN/DE)
- HACS compatibility
