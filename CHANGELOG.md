# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Fixed

- Operating mode select: `set_result: 0` from the device firmware (C-style success code) was interpreted as Python falsy, causing the coordinator refresh to never fire after a mode change. Fixed by checking `result is not None` instead of `result and result.get("set_result")`.

## [0.1.3] - 2026-03-29

### Fixed

- UDP client: on `socket.timeout`, keep receiving until the full request deadline (previously the first recv slice ended the call early, e.g. ~3s with a 12s budget).
- Slightly increased spacing between status polls (`INTER_REQUEST_DELAY_SEC` = 1.0) to reduce device overload.

### Changed

- `hacs.json`: removed unsupported `domains` key so HACS manifest validation matches the official schema.

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
