"""Data coordinator for Marstek Venus integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MarstekVenusAPI
from .const import (
    ADAPTIVE_INTERVAL_LADDER,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SLOW_TIER_EVERY,
)

_LOGGER = logging.getLogger(__name__)

FAST_KEYS = ("battery", "es")
SLOW_KEYS = ("wifi", "ble", "em")
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

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    def request_mode_refresh(self) -> None:
        """Mark ES.GetMode for inclusion on the next refresh (used after SetMode)."""
        self._force_mode_refresh = True

    def _apply_adaptive_interval(self, success: bool) -> None:
        """Backoff on consecutive failures, reset to default on success."""
        if success:
            if self._consecutive_failures:
                _LOGGER.debug("Resetting poll interval to %ss", DEFAULT_SCAN_INTERVAL)
            self._consecutive_failures = 0
            target = DEFAULT_SCAN_INTERVAL
        else:
            self._consecutive_failures += 1
            idx = min(self._consecutive_failures - 1, len(ADAPTIVE_INTERVAL_LADDER) - 1)
            target = ADAPTIVE_INTERVAL_LADDER[idx]
            _LOGGER.warning(
                "Update failure #%s — backing off poll interval to %ss",
                self._consecutive_failures, target,
            )

        new_interval = timedelta(seconds=target)
        if self.update_interval != new_interval:
            self.update_interval = new_interval

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

        self._apply_adaptive_interval(success=fast_ok)
        return merged


def _derive_pv(es: Any) -> dict[str, Any] | None:
    if not isinstance(es, dict):
        return None
    return {
        "pv_power": es.get("pv_power"),
        "pv_voltage": es.get("pv_voltage"),
        "pv_current": es.get("pv_current"),
    }
