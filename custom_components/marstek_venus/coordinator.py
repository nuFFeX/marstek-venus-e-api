"""Data coordinator for Marstek Venus integration."""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DeviceBusy, MarstekVenusAPI
from .const import (
    CONF_HOST,
    CONF_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    IDLE_INTERVAL_FACTOR,
    IDLE_POWER_THRESHOLD_W,
    IDLE_SOC_THRESHOLD,
    REFRESH_DEBOUNCE_COOLDOWN,
    REPAIR_FAILURE_THRESHOLD,
    SLOW_TIER_EVERY,
    SLOWDOWN_FACTOR,
)

_REPAIR_ISSUE_ID = "device_unreachable"

_LOGGER = logging.getLogger(__name__)

FAST_KEYS = ("battery", "es")
SLOW_KEYS = ("wifi", "ble")
MODE_KEY = "mode"


class MarstekVenusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Marstek Venus data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.api = MarstekVenusAPI(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, 30000),
        )
        self._tick = 0
        self._force_mode_refresh = False
        self._consecutive_failures = 0
        self._last_total_charge: float | None = None
        self._last_total_discharge: float | None = None
        self._is_idle = False
        self._last_success_method: str | None = None
        self._last_success_at: float | None = None
        self._last_battery_snapshot: str | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            # Don't push entity state if data is byte-identical to last cycle.
            always_update=False,
            # Coalesce rapid async_request_refresh() calls (e.g. from service
            # invocations or HA's "Update entity" button) into one request.
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=REFRESH_DEBOUNCE_COOLDOWN,
                immediate=False,
            ),
        )

    def request_mode_refresh(self) -> None:
        """Mark ES.GetMode for inclusion on the next refresh (used after SetMode)."""
        self._force_mode_refresh = True

    def _base_interval(self) -> int:
        """Base poll interval honoring idle-state backoff."""
        if self._is_idle:
            return DEFAULT_SCAN_INTERVAL * IDLE_INTERVAL_FACTOR
        return DEFAULT_SCAN_INTERVAL

    def _apply_adaptive_interval(self, success: bool) -> None:
        """SolaX-style slowdown: any failure → SLOWDOWN_FACTOR× interval; recovery → 1×.

        Idle-state backoff is layered on top: when the battery is idle the
        base interval is already multiplied by IDLE_INTERVAL_FACTOR.
        """
        if success:
            if self._consecutive_failures:
                _LOGGER.debug(
                    "Recovered after %s failure(s) — resetting poll interval",
                    self._consecutive_failures,
                )
            self._consecutive_failures = 0
            target = self._base_interval()
            ir.async_delete_issue(self.hass, DOMAIN, _REPAIR_ISSUE_ID)
        else:
            self._consecutive_failures += 1
            target = self._base_interval() * SLOWDOWN_FACTOR
            gap = (
                f"{time.monotonic() - self._last_success_at:.0f}s"
                if self._last_success_at is not None
                else "n/a"
            )
            _LOGGER.warning(
                "Update failure #%s — slowing poll interval to %ss; "
                "last good response %s ago; last snapshot: %s",
                self._consecutive_failures,
                target,
                gap,
                self._last_battery_snapshot or "n/a",
            )
            if self._consecutive_failures == REPAIR_FAILURE_THRESHOLD:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    _REPAIR_ISSUE_ID,
                    is_fixable=False,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key=_REPAIR_ISSUE_ID,
                )

        new_interval = timedelta(seconds=target)
        if self.update_interval != new_interval:
            self.update_interval = new_interval

    def _update_idle_state(self, data: dict[str, Any]) -> None:
        """Refresh idle flag from latest battery/ES data and adjust interval if it flipped."""
        battery = data.get("battery") if isinstance(data, dict) else None
        es = data.get("es") if isinstance(data, dict) else None

        soc = None
        if isinstance(battery, dict):
            soc = battery.get("soc")
        if soc is None and isinstance(es, dict):
            soc = es.get("bat_soc")

        bat_power = es.get("bat_power") if isinstance(es, dict) else None

        if soc is None or bat_power is None:
            return

        try:
            is_idle = (
                soc >= IDLE_SOC_THRESHOLD and abs(bat_power) < IDLE_POWER_THRESHOLD_W
            )
        except TypeError:
            return

        if is_idle != self._is_idle:
            _LOGGER.info(
                "Battery idle state changed: %s -> %s (soc=%s, bat_power=%s) — poll interval now %ss",
                self._is_idle,
                is_idle,
                soc,
                bat_power,
                (DEFAULT_SCAN_INTERVAL * IDLE_INTERVAL_FACTOR)
                if is_idle
                else DEFAULT_SCAN_INTERVAL,
            )
            self._is_idle = is_idle
            # Re-apply interval with the new base; preserves any active slowdown.
            self._apply_adaptive_interval(success=self._consecutive_failures == 0)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        self._tick += 1
        include_slow = self._tick == 1 or self._tick % SLOW_TIER_EVERY == 0
        include_mode = self._force_mode_refresh
        self._force_mode_refresh = False

        try:
            new_data = await self.api.get_all_status(
                include_slow=include_slow,
                include_mode=include_mode,
            )
        except DeviceBusy:
            # Lock collision — a previous request is still in flight (e.g.
            # SetMode write or a slow poll). Skip this cycle silently and
            # return whatever we already have. Do NOT advance the failure
            # counter; the device is responsive, just busy.
            _LOGGER.debug("Skipping poll — previous request still in flight")
            if self.data is None:
                raise UpdateFailed("Device busy on first poll") from None
            return self.data
        except Exception as err:
            self._apply_adaptive_interval(success=False)
            raise UpdateFailed(f"Error communicating with device: {err}") from err

        # Fast-tier success criterion: at least one fast-tier value populated.
        fast_ok = any(new_data.get(k) is not None for k in FAST_KEYS)

        if self.data is None:
            if not fast_ok:
                self._apply_adaptive_interval(success=False)
                raise UpdateFailed("No data received from device")
            # Compute pv from es and seed remaining keys as None where missing.
            seeded = {
                "battery": new_data.get("battery"),
                "es": new_data.get("es"),
                "mode": new_data.get("mode"),
                "wifi": new_data.get("wifi"),
                "ble": new_data.get("ble"),
                "em": new_data.get("em"),
                "pv": _derive_pv(new_data.get("es")),
            }
            self._apply_adaptive_interval(success=True)
            return seeded

        merged = dict(self.data)
        for key in (*FAST_KEYS, *SLOW_KEYS, MODE_KEY):
            if new_data.get(key) is not None:
                merged[key] = new_data[key]
        if new_data.get("es") is not None:
            merged["pv"] = _derive_pv(new_data["es"])

        if fast_ok:
            self._record_success_snapshot(merged)
        self._apply_adaptive_interval(success=fast_ok)
        self._update_idle_state(merged)
        self._detect_device_reset(merged)
        return merged

    def _record_success_snapshot(self, data: dict[str, Any]) -> None:
        """Track the last good response — used to enrich timeout diagnostics."""
        self._last_success_at = time.monotonic()
        battery = data.get("battery") or {}
        es = data.get("es") or {}
        soc = battery.get("soc")
        if soc is None:
            soc = es.get("bat_soc")
        self._last_battery_snapshot = (
            f"soc={soc} bat_power={es.get('bat_power')} "
            f"ongrid={es.get('ongrid_power')} mode={(data.get('mode') or {}).get('mode')}"
        )

    def _detect_device_reset(self, data: dict[str, Any]) -> None:
        """Warn when cumulative energy counters jump backwards — sign of a device reboot."""
        es = data.get("es")
        if not isinstance(es, dict):
            return
        charge = es.get("total_charge_energy")
        discharge = es.get("total_discharge_energy")

        if charge is not None and self._last_total_charge is not None:
            if charge < self._last_total_charge:
                _LOGGER.warning(
                    "Device reset detected: total_charge_energy dropped from %.1f to %.1f — "
                    "the device may have rebooted or been factory-reset.",
                    self._last_total_charge,
                    charge,
                )
        if discharge is not None and self._last_total_discharge is not None:
            if discharge < self._last_total_discharge:
                _LOGGER.warning(
                    "Device reset detected: total_discharge_energy dropped from %.1f to %.1f — "
                    "the device may have rebooted or been factory-reset.",
                    self._last_total_discharge,
                    discharge,
                )

        if charge is not None:
            self._last_total_charge = charge
        if discharge is not None:
            self._last_total_discharge = discharge


def _derive_pv(es: Any) -> dict[str, Any] | None:
    if not isinstance(es, dict):
        return None
    return {
        "pv_power": es.get("pv_power"),
        "pv_voltage": es.get("pv_voltage"),
        "pv_current": es.get("pv_current"),
    }
