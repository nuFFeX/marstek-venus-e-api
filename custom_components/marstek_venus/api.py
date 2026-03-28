"""API client for Marstek Venus devices."""
from __future__ import annotations

import asyncio
import json
import logging
import socket
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Venus-Geräte verarbeiten UDP-Anfragen praktisch seriell; parallele Sockets führen zu Timeouts.
INTER_REQUEST_DELAY_SEC = 0.2


class MarstekVenusAPI:
    """API client for Marstek Venus devices."""

    def __init__(self, host: str, port: int = 30000) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.timeout = 5
        self._request_id = 0
        self._comm_lock = asyncio.Lock()

    def _get_next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    async def _send_command(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Send a command to the device and return the response."""
        if params is None:
            params = {"id": 0}

        req_id = self._get_next_id()
        command = {"id": req_id, "method": method, "params": params}

        _LOGGER.debug("Sending command to %s:%s: %s", self.host, self.port, command)

        async with self._comm_lock:
            try:
                loop = asyncio.get_running_loop()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)

                message = json.dumps(command).encode("utf-8")
                await loop.run_in_executor(
                    None, sock.sendto, message, (self.host, self.port)
                )

                data, _ = await loop.run_in_executor(None, sock.recvfrom, 4096)
                sock.close()

                response = json.loads(data.decode("utf-8"))
                _LOGGER.debug("Received response: %s", response)

                if response.get("id") != req_id:
                    _LOGGER.warning(
                        "Unexpected response id %s (expected %s) for %s",
                        response.get("id"),
                        req_id,
                        method,
                    )

                if err := response.get("error"):
                    _LOGGER.warning(
                        "Device reported error for %s: %s", method, err
                    )
                    return None

                return response.get("result")

            except socket.timeout:
                _LOGGER.error(
                    "Timeout waiting for response from %s:%s (%s)",
                    self.host,
                    self.port,
                    method,
                )
                return None
            except json.JSONDecodeError as err:
                _LOGGER.error("Invalid JSON response: %s", err)
                return None
            except Exception as err:
                _LOGGER.error("Error communicating with device: %s", err)
                return None

    async def discover_device(self, ble_mac: str = "0") -> dict[str, Any] | None:
        """Discover Marstek device on the network."""
        return await self._send_command("Marstek.GetDevice", {"ble_mac": ble_mac})

    async def get_wifi_status(self) -> dict[str, Any] | None:
        """Get WiFi status."""
        return await self._send_command("WiFi.GetStatus", {"id": 0})

    async def get_ble_status(self) -> dict[str, Any] | None:
        """Get Bluetooth status."""
        return await self._send_command("BLE.GetStatus", {"id": 0})

    async def get_battery_status(self) -> dict[str, Any] | None:
        """Get battery status."""
        return await self._send_command("Bat.GetStatus", {"id": 0})

    async def get_pv_status(self) -> dict[str, Any] | None:
        """Get photovoltaic status."""
        return await self._send_command("PV.GetStatus", {"id": 0})

    async def get_es_status(self) -> dict[str, Any] | None:
        """Get energy system status."""
        return await self._send_command("ES.GetStatus", {"id": 0})

    async def get_es_mode(self) -> dict[str, Any] | None:
        """Get energy system mode."""
        return await self._send_command("ES.GetMode", {"id": 0})

    async def set_es_mode_auto(self) -> dict[str, Any] | None:
        """Set energy system to Auto mode."""
        params = {
            "id": 1,
            "config": {
                "mode": "Auto",
                "auto_cfg": {"enable": 1}
            }
        }
        return await self._send_command("ES.SetMode", params)

    async def set_es_mode_ai(self) -> dict[str, Any] | None:
        """Set energy system to AI mode."""
        params = {
            "id": 1,
            "config": {
                "mode": "AI",
                "ai_cfg": {"enable": 1}
            }
        }
        return await self._send_command("ES.SetMode", params)

    async def set_es_mode_manual(
        self,
        time_num: int,
        start_time: str,
        end_time: str,
        week_set: int = 127,
        power: int = 100,
    ) -> dict[str, Any] | None:
        """Set energy system to Manual mode."""
        params = {
            "id": 1,
            "config": {
                "mode": "Manual",
                "manual_cfg": {
                    "time_num": time_num,
                    "start_time": start_time,
                    "end_time": end_time,
                    "week_set": week_set,
                    "power": power,
                    "enable": 1,
                }
            }
        }
        return await self._send_command("ES.SetMode", params)

    async def set_es_mode_passive(
        self, power: int, cd_time: int = 300
    ) -> dict[str, Any] | None:
        """Set energy system to Passive mode."""
        params = {
            "id": 1,
            "config": {
                "mode": "Passive",
                "passive_cfg": {
                    "power": power,
                    "cd_time": cd_time
                }
            }
        }
        return await self._send_command("ES.SetMode", params)

    async def set_es_mode(self, mode: str, **kwargs) -> dict[str, Any] | None:
        """Set energy system mode."""
        if mode == "Auto":
            return await self.set_es_mode_auto()
        elif mode == "AI":
            return await self.set_es_mode_ai()
        elif mode == "Manual":
            return await self.set_es_mode_manual(**kwargs)
        elif mode == "Passive":
            return await self.set_es_mode_passive(**kwargs)
        else:
            _LOGGER.error("Unknown mode: %s", mode)
            return None

    async def get_all_status(self) -> dict[str, Any]:
        """Get all status information from the device.

        Requests run one after another. The Venus firmware does not reliably
        answer multiple concurrent UDP queries; parallel calls caused timeouts.
        """
        results: dict[str, Any] = {}
        steps: tuple[tuple[str, Any], ...] = (
            ("battery", self.get_battery_status()),
            ("pv", self.get_pv_status()),
            ("es", self.get_es_status()),
            ("mode", self.get_es_mode()),
            ("wifi", self.get_wifi_status()),
            ("ble", self.get_ble_status()),
        )

        for index, (key, coro) in enumerate(steps):
            if index:
                await asyncio.sleep(INTER_REQUEST_DELAY_SEC)
            try:
                results[key] = await coro
            except Exception as err:
                _LOGGER.error("Error fetching %s: %s", key, err)
                results[key] = None

        # Venus E liefert teils kein PV.GetStatus; PV-Leistung steckt in ES.GetStatus
        es = results.get("es")
        if results.get("pv") is None and isinstance(es, dict):
            results["pv"] = {
                "pv_power": es.get("pv_power"),
                "pv_voltage": es.get("pv_voltage"),
                "pv_current": es.get("pv_current"),
            }

        return results
