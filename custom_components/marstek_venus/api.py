"""API client for Marstek Venus devices."""
from __future__ import annotations

import asyncio
import json
import logging
import socket
import time
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Venus-Geräte verarbeiten UDP-Anfragen seriell; Abstand + längeres Timeout reduzieren Flaps.
INTER_REQUEST_DELAY_SEC = 2.0


class DeviceBusy(Exception):
    """Raised when a poll is skipped because another request is in flight.

    The coordinator treats this as a benign skip, not a failure — it should
    not advance the failure counter or trigger a slowdown.
    """


def _sync_udp_request(
    host: str,
    port: int,
    payload: bytes,
    expect_id: int,
    total_timeout: float,
) -> dict[str, Any] | None:
    """Send one JSON-RPC UDP request; discard stray packets until id matches or timeout."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    deadline = time.monotonic() + total_timeout
    try:
        sock.sendto(payload, (host, port))
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            sock.settimeout(min(remaining, max(0.2, total_timeout * 0.25)))
            try:
                data, _ = sock.recvfrom(8192)
            except socket.timeout:
                continue
            try:
                response: Any = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(response, dict):
                continue
            if response.get("id") != expect_id:
                _LOGGER.debug(
                    "Ignoring stray UDP response id %s (expected %s)",
                    response.get("id"),
                    expect_id,
                )
                continue
            return response
    except OSError as err:
        _LOGGER.error("UDP error to %s:%s: %s", host, port, err)
        return None
    finally:
        sock.close()


class MarstekVenusAPI:
    """API client for Marstek Venus devices."""

    def __init__(self, host: str, port: int = 30000) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.timeout = 6
        # SolaX-Erfahrung: 1 Versuch pro Request — Retries belasten ein
        # bereits gestresstes Gerät zusätzlich. Verlorene Polls werden
        # vom nächsten Tier-Cycle abgefangen.
        self.max_attempts = 1
        self._request_id = 0
        self._comm_lock = asyncio.Lock()

    def _get_next_id(self) -> int:
        """Get next request ID, wrapping at 65535 to avoid overflow."""
        self._request_id = (self._request_id % 65535) + 1
        return self._request_id

    async def _send_command_unsafe(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Send a command WITHOUT acquiring _comm_lock. Caller must hold _comm_lock."""
        if params is None:
            params = {"id": 0}

        req_id = self._get_next_id()
        command = {"id": req_id, "method": method, "params": params}

        _LOGGER.debug("Sending command to %s:%s: %s", self.host, self.port, command)

        try:
            loop = asyncio.get_running_loop()
            message = json.dumps(command, separators=(",", ":")).encode("utf-8")
            response: dict[str, Any] | None = None

            for attempt in range(1, self.max_attempts + 1):
                response = await loop.run_in_executor(
                    None,
                    lambda: _sync_udp_request(
                        self.host,
                        self.port,
                        message,
                        req_id,
                        self.timeout,
                    ),
                )
                if response is not None:
                    if attempt > 1:
                        _LOGGER.debug(
                            "Recovered %s on attempt %s/%s",
                            method, attempt, self.max_attempts,
                        )
                    break
                if attempt < self.max_attempts:
                    _LOGGER.debug(
                        "Retrying %s on %s:%s (attempt %s/%s)",
                        method, self.host, self.port, attempt + 1, self.max_attempts,
                    )

            if response is None:
                _LOGGER.warning(
                    "Timeout waiting for response from %s:%s (%s) after %s attempts",
                    self.host, self.port, method, self.max_attempts,
                )
                return None

            _LOGGER.debug("Received response: %s", response)

            if err := response.get("error"):
                _LOGGER.warning(
                    "Device reported error for %s: %s", method, err
                )
                return None

            return response.get("result")

        except Exception as err:
            _LOGGER.error("Error communicating with device: %s", err)
            return None

    async def _send_command(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Send a command to the device, holding _comm_lock for the full operation."""
        async with self._comm_lock:
            return await self._send_command_unsafe(method, params)

    async def discover_device(self, ble_mac: str = "0") -> dict[str, Any] | None:
        """Discover Marstek device on the network."""
        return await self._send_command("Marstek.GetDevice", {"ble_mac": ble_mac})

    async def get_wifi_status(self) -> dict[str, Any] | None:
        """Get WiFi status (API method name is Wifi.GetStatus)."""
        return await self._send_command("Wifi.GetStatus", {"id": 0})

    async def get_ble_status(self) -> dict[str, Any] | None:
        """Get Bluetooth status."""
        return await self._send_command("BLE.GetStatus", {"id": 0})

    async def get_em_status(self) -> dict[str, Any] | None:
        """Get Energy Meter / CT status (ct_state, a_power, b_power, c_power, total_power)."""
        return await self._send_command("EM.GetStatus", {"id": 0})

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
            "id": 0,
            "config": {
                "mode": "Auto",
                "auto_cfg": {"enable": 1}
            }
        }
        return await self._send_command("ES.SetMode", params)

    async def set_es_mode_ai(self) -> dict[str, Any] | None:
        """Set energy system to AI mode."""
        params = {
            "id": 0,
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
            "id": 0,
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
            "id": 0,
            "config": {
                "mode": "Passive",
                "passive_cfg": {
                    "power": power,
                    "cd_time": cd_time
                }
            }
        }
        return await self._send_command("ES.SetMode", params)

    async def set_es_mode_ups(self) -> dict[str, Any] | None:
        """Set energy system to UPS mode."""
        params = {
            "id": 0,
            "config": {
                "mode": "UPS",
                "ups_cfg": {"enable": 1}
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

    async def get_all_status(
        self,
        include_slow: bool = False,
        include_mode: bool = False,
    ) -> dict[str, Any]:
        """Get status information from the device.

        Tiered polling:
        - Fast tier (always): Bat.GetStatus, ES.GetStatus
        - Slow tier (include_slow=True): Wifi.GetStatus, BLE.GetStatus
        - Mode-on-demand (include_mode=True): ES.GetMode regardless of slow tier

        EM.GetStatus is currently disabled — it correlates with device resets and
        is being isolated as a hypothesis. Re-enable once root cause is confirmed.

        Holds _comm_lock for the entire poll so a concurrent SetMode cannot be
        interleaved between individual requests. Uses _send_command_unsafe
        internally to avoid lock re-entry (asyncio.Lock is not reentrant).

        PV.GetStatus is omitted on Venus E (timeouts / Method not found);
        PV fields are derived from ES.GetStatus.
        """
        steps: list[tuple[str, str, dict]] = [
            ("battery", "Bat.GetStatus", {"id": 0}),
            ("es", "ES.GetStatus", {"id": 0}),
        ]
        if include_slow or include_mode:
            steps.append(("mode", "ES.GetMode", {"id": 0}))
        if include_slow:
            steps.append(("wifi", "Wifi.GetStatus", {"id": 0}))
            steps.append(("ble", "BLE.GetStatus", {"id": 0}))

        # Drop-on-collision: ist der Lock bereits gehalten (z.B. SetMode oder
        # ein vorheriger Poll dauert noch), überspringen wir diesen Cycle
        # statt zu queuen. Verhindert Backlog wenn das Gerät >SCAN_INTERVAL
        # zum Antworten braucht.
        if self._comm_lock.locked():
            raise DeviceBusy("Previous request still in flight; skipping poll")

        results: dict[str, Any] = {}
        async with self._comm_lock:
            for index, (key, method, params) in enumerate(steps):
                if index:
                    await asyncio.sleep(INTER_REQUEST_DELAY_SEC)
                try:
                    results[key] = await self._send_command_unsafe(method, params)
                except Exception as err:
                    _LOGGER.error("Error fetching %s: %s", key, err)
                    results[key] = None

        es = results.get("es")
        if isinstance(es, dict):
            results["pv"] = {
                "pv_power": es.get("pv_power"),
                "pv_voltage": es.get("pv_voltage"),
                "pv_current": es.get("pv_current"),
            }
        else:
            results["pv"] = None

        return results
