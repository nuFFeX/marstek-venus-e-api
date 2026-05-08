"""Constants for the Marstek Venus integration."""

DOMAIN = "marstek_venus"

# Configuration
CONF_HOST = "host"
CONF_PORT = "port"
CONF_DEVICE_ID = "device_id"
CONF_BLE_MAC = "ble_mac"

# Default values
DEFAULT_PORT = 30000
DEFAULT_SCAN_INTERVAL = 120

# Tiered polling: slow-tier methods only run every Nth update cycle.
SLOW_TIER_EVERY = 10

# Adaptive polling: on any failed update the interval is multiplied by this
# factor (SolaX-style "slowdown"). Reset to 1× on the first successful poll.
SLOWDOWN_FACTOR = 5

# After this many consecutive failures we surface a Repair issue instead of
# spamming the log on every cycle.
REPAIR_FAILURE_THRESHOLD = 5

# Debounce cooldown (s) for coordinator refresh requests so rapid service
# calls / entity-update triggers cannot burst the device.
REFRESH_DEBOUNCE_COOLDOWN = 2.0

# Idle backoff: when the battery sits at full SOC with ~no power flow the
# device's idle/standby firmware path appears especially fragile to UDP
# polling — observed resets correlate with this state. Multiply the poll
# interval by IDLE_FACTOR while the battery is idle to shrink the trigger
# window. Detection thresholds are intentionally loose.
IDLE_SOC_THRESHOLD = 99
IDLE_POWER_THRESHOLD_W = 50
IDLE_INTERVAL_FACTOR = 3

# Device modes
MODE_AUTO = "Auto"
MODE_AI = "AI"
MODE_MANUAL = "Manual"
MODE_PASSIVE = "Passive"
MODE_UPS = "UPS"

MODES = [MODE_AUTO, MODE_AI, MODE_MANUAL, MODE_PASSIVE, MODE_UPS]

# API Methods
METHOD_GET_DEVICE = "Marstek.GetDevice"
METHOD_WIFI_STATUS = "Wifi.GetStatus"
METHOD_BLE_STATUS = "BLE.GetStatus"
METHOD_BAT_STATUS = "Bat.GetStatus"
METHOD_PV_STATUS = "PV.GetStatus"
METHOD_ES_STATUS = "ES.GetStatus"
METHOD_ES_GET_MODE = "ES.GetMode"
METHOD_ES_SET_MODE = "ES.SetMode"
METHOD_EM_STATUS = "EM.GetStatus"

# Energy Meter / CT
CT_STATE_DISCONNECTED = 0
CT_STATE_CONNECTED = 1

# Attributes
ATTR_DEVICE = "device"
ATTR_VERSION = "ver"
ATTR_BLE_MAC = "ble_mac"
ATTR_WIFI_MAC = "wifi_mac"
ATTR_WIFI_NAME = "wifi_name"
ATTR_IP = "ip"
ATTR_SOC = "soc"
ATTR_BATTERY_TEMP = "bat_temp"
ATTR_BATTERY_CAPACITY = "bat_capacity"
ATTR_RATED_CAPACITY = "rated_capacity"
ATTR_PV_POWER = "pv_power"
ATTR_PV_VOLTAGE = "pv_voltage"
ATTR_PV_CURRENT = "pv_current"
ATTR_ONGRID_POWER = "ongrid_power"
ATTR_OFFGRID_POWER = "offgrid_power"
ATTR_BAT_POWER = "bat_power"
ATTR_TOTAL_PV_ENERGY = "total_pv_energy"
ATTR_TOTAL_GRID_OUTPUT = "total_grid_output_energy"
ATTR_TOTAL_GRID_INPUT = "total_grid_input_energy"
ATTR_TOTAL_LOAD_ENERGY = "total_load_energy"
