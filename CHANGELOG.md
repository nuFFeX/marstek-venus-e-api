# Changelog

All notable changes to this project are documented in this file.

## [0.1.2] - 2026-03-28

### Fixed

- WiFi status: use API method `Wifi.GetStatus` (not `WiFi.GetStatus`) so Venus E returns data instead of “Method not found”.
- Removed `PV.GetStatus` from the polling loop on Venus E (frequent timeouts / unsupported); PV values are derived from `ES.GetStatus` (`pv_power`, etc.).
- UDP receive loop: ignore stray packets until the JSON-RPC `id` matches the request (reduces parse errors and wrong replies).
- Increased request spacing (`INTER_REQUEST_DELAY_SEC`) and UDP timeout for more stable communication.
- Coordinator merges new data with the previous snapshot so sensors do not drop to unavailable on partial API failures.

## [0.1.1] - 2026-03-28

### Fixed

- Replaced parallel `asyncio.gather` status polls with sequential UDP calls; Venus firmware does not reliably answer concurrent requests.
- Added an asyncio lock so Marstek UDP traffic does not overlap within the integration.
- Log device JSON-RPC `error` responses instead of treating them as success.
- PV fallback from `ES.GetStatus` when `PV.GetStatus` is missing or fails.

## [0.1.0]

### Added

- Initial Home Assistant custom integration.
- Sensors: battery, PV, energy system (ES), mode, WiFi, BLE.
- Operating mode control (Auto / AI / Manual / Passive).
- Config flow, EN/DE translations, HACS metadata.
