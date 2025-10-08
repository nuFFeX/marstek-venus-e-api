# Marstek Venus Integration

![Logo](https://brands.home-assistant.io/_/marstek_venus/logo.png)

Integrate your Marstek Venus C/E energy storage system with Home Assistant using the local UDP API.

## Features

✅ Real-time battery monitoring (SOC, temperature, capacity)
✅ Solar production tracking (power, voltage, current)
✅ Energy system statistics (grid, off-grid, battery power)
✅ Total energy counters for Energy Dashboard
✅ Operating mode control (Auto/AI/Manual/Passive)
✅ Network monitoring (WiFi status)
✅ Local control - no cloud dependency
✅ Multi-language support (English, German)

## Quick Start

1. Ensure your Marstek Venus device is connected to your network
2. Enable the Local API feature in the Marstek APP
3. Install this integration via HACS
4. Add the integration through Settings → Devices & Services
5. Enter your device's IP address and port (default: 30000)

## Entities Provided

- **20+ Sensors**: Battery, solar, energy, network
- **1 Select**: Operating mode control
- **2 Switches**: Charge/discharge permissions (monitoring)

## Energy Dashboard Compatible

Perfect for tracking:
- Solar production
- Grid consumption and return
- Battery state and power flow
- Total energy statistics

{% if installed %}
## Configuration

Configure the integration in **Settings → Devices & Services → Marstek Venus**

For detailed setup instructions and automation examples, see the [full documentation](https://github.com/yourusername/marstek-venus-hacs).
{% endif %}
