"""Support for Xiaomi Mi Air Purifier and Xiaomi Mi Air Humidifier."""
from dataclasses import dataclass
from enum import Enum
import logging

from miio.airfresh import LedBrightness as AirfreshLedBrightness
from miio.airhumidifier import LedBrightness as AirhumidifierLedBrightness
from miio.airhumidifier_miot import (
    LedBrightness as AirhumidifierMiotLedBrightness,
    PressedButton as AirhumidifierPressedButton,
)
from miio.airpurifier import LedBrightness as AirpurifierLedBrightness
from miio.airpurifier_miot import LedBrightness as AirpurifierMiotLedBrightness
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import ATTR_ENTITY_ID, ATTR_MODE, ATTR_TEMPERATURE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import BooleanSelector, NumberSelector, Selector

from .const import (  # MODEL_AIRPURIFIER_2H,; MODEL_AIRPURIFIER_2S,; MODEL_AIRPURIFIER_PRO,; MODEL_AIRPURIFIER_PRO_V7,; MODEL_AIRPURIFIER_V3,; MODELS_FAN,; MODELS_HUMIDIFIER_MIOT,; MODELS_PURIFIER_MIOT,
    CONF_DEVICE,
    CONF_FLOW_TYPE,
    DOMAIN,
    KEY_COORDINATOR,
    KEY_DEVICE,
    MODEL_AIRHUMIDIFIER_CA1,
    MODEL_AIRHUMIDIFIER_CA4,
    MODEL_AIRHUMIDIFIER_CB1,
    SERVICE_RESET_FILTER,
    SERVICE_SET_AUTO_DETECT_OFF,
    SERVICE_SET_AUTO_DETECT_ON,
    SERVICE_SET_BUZZER_OFF,
    SERVICE_SET_BUZZER_ON,
    SERVICE_SET_CHILD_LOCK_OFF,
    SERVICE_SET_CHILD_LOCK_ON,
    SERVICE_SET_DRY_OFF,
    SERVICE_SET_DRY_ON,
    SERVICE_SET_EXTRA_FEATURES,
    SERVICE_SET_FAN_LED_OFF,
    SERVICE_SET_FAN_LED_ON,
    SERVICE_SET_FAN_LEVEL,
    SERVICE_SET_FAVORITE_LEVEL,
    SERVICE_SET_LEARN_MODE_OFF,
    SERVICE_SET_LEARN_MODE_ON,
    SERVICE_SET_LED_BRIGHTNESS,
    SERVICE_SET_MOTOR_SPEED,
    SERVICE_SET_TARGET_HUMIDITY,
    SERVICE_SET_VOLUME,
)
from .device import XiaomiCoordinatedMiioEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Xiaomi Miio Device"
DATA_KEY = "fan.xiaomi_miio"

CONF_MODEL = "model"

ATTR_MODEL = "model"

# Air Purifier
ATTR_HUMIDITY = "humidity"
ATTR_AIR_QUALITY_INDEX = "aqi"
ATTR_FILTER_HOURS_USED = "filter_hours_used"
ATTR_FILTER_LIFE = "filter_life_remaining"
ATTR_FAVORITE_LEVEL = "favorite_level"
ATTR_BUZZER = "buzzer"
ATTR_CHILD_LOCK = "child_lock"
ATTR_LED = "led"
ATTR_LED_BRIGHTNESS = "led_brightness"
ATTR_MOTOR_SPEED = "motor_speed"
ATTR_AVERAGE_AIR_QUALITY_INDEX = "average_aqi"
ATTR_PURIFY_VOLUME = "purify_volume"
ATTR_BRIGHTNESS = "brightness"
ATTR_LEVEL = "level"
ATTR_FAN_LEVEL = "fan_level"
ATTR_MOTOR2_SPEED = "motor2_speed"
ATTR_ILLUMINANCE = "illuminance"
ATTR_FILTER_RFID_PRODUCT_ID = "filter_rfid_product_id"
ATTR_FILTER_RFID_TAG = "filter_rfid_tag"
ATTR_FILTER_TYPE = "filter_type"
ATTR_LEARN_MODE = "learn_mode"
ATTR_SLEEP_TIME = "sleep_time"
ATTR_SLEEP_LEARN_COUNT = "sleep_mode_learn_count"
ATTR_EXTRA_FEATURES = "extra_features"
ATTR_FEATURES = "features"
ATTR_TURBO_MODE_SUPPORTED = "turbo_mode_supported"
ATTR_AUTO_DETECT = "auto_detect"
ATTR_SLEEP_MODE = "sleep_mode"
ATTR_VOLUME = "volume"
ATTR_USE_TIME = "use_time"
ATTR_BUTTON_PRESSED = "button_pressed"

# Air Humidifier
ATTR_TARGET_HUMIDITY = "target_humidity"
ATTR_TRANS_LEVEL = "trans_level"
ATTR_HARDWARE_VERSION = "hardware_version"

# Air Humidifier CA
# ATTR_MOTOR_SPEED = "motor_speed"
ATTR_DEPTH = "depth"
ATTR_DRY = "dry"

# Air Humidifier CA4
ATTR_ACTUAL_MOTOR_SPEED = "actual_speed"
ATTR_FAHRENHEIT = "fahrenheit"

# Air Fresh
ATTR_CO2 = "co2"

# Map attributes to properties of the state object
AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_TURBO_MODE_SUPPORTED: "turbo_mode_supported",
    ATTR_BUTTON_PRESSED: "button_pressed",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_USE_TIME: "use_time",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_SLEEP_MODE: "sleep_mode",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_USE_TIME: "use_time",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_VOLUME: "volume",
    # perhaps supported but unconfirmed
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO_V7 = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_VOLUME: "volume",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_2S = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_BUZZER: "buzzer",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_3 = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_USE_TIME: "use_time",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_FAN_LEVEL: "fan_level",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_V3 = {
    # Common set isn't used here. It's a very basic version of the device.
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_LED: "led",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_MOTOR_SPEED: "motor_speed",
    # perhaps supported but unconfirmed
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_VOLUME: "volume",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_USE_TIME: "use_time",
    ATTR_BUTTON_PRESSED: "button_pressed",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_MODE: "mode",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_TRANS_LEVEL: "trans_level",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_HARDWARE_VERSION: "hardware_version",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_DEPTH: "depth",
    ATTR_DRY: "dry",
    ATTR_HARDWARE_VERSION: "hardware_version",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4 = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_ACTUAL_MOTOR_SPEED: "actual_speed",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_DRY: "dry",
    ATTR_FAHRENHEIT: "fahrenheit",
    ATTR_MOTOR_SPEED: "motor_speed",
}

AVAILABLE_ATTRIBUTES_AIRFRESH = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_CO2: "co2",
    ATTR_HUMIDITY: "humidity",
    ATTR_MODE: "mode",
    ATTR_LED: "led",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_USE_TIME: "use_time",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_EXTRA_FEATURES: "extra_features",
}

OPERATION_MODES_AIRPURIFIER = ["Auto", "Silent", "Favorite", "Idle"]
PRESET_MODES_AIRPURIFIER = ["Auto", "Silent", "Favorite", "Idle"]
OPERATION_MODES_AIRPURIFIER_PRO = ["Auto", "Silent", "Favorite"]
PRESET_MODES_AIRPURIFIER_PRO = ["Auto", "Silent", "Favorite"]
OPERATION_MODES_AIRPURIFIER_PRO_V7 = OPERATION_MODES_AIRPURIFIER_PRO
PRESET_MODES_AIRPURIFIER_PRO_V7 = PRESET_MODES_AIRPURIFIER_PRO
OPERATION_MODES_AIRPURIFIER_2S = ["Auto", "Silent", "Favorite"]
PRESET_MODES_AIRPURIFIER_2S = ["Auto", "Silent", "Favorite"]
OPERATION_MODES_AIRPURIFIER_3 = ["Auto", "Silent", "Favorite", "Fan"]
PRESET_MODES_AIRPURIFIER_3 = ["Auto", "Silent", "Favorite", "Fan"]
OPERATION_MODES_AIRPURIFIER_V3 = [
    "Auto",
    "Silent",
    "Favorite",
    "Idle",
    "Medium",
    "High",
    "Strong",
]
PRESET_MODES_AIRPURIFIER_V3 = [
    "Auto",
    "Silent",
    "Favorite",
    "Idle",
    "Medium",
    "High",
    "Strong",
]
OPERATION_MODES_AIRFRESH = ["Auto", "Silent", "Interval", "Low", "Middle", "Strong"]
PRESET_MODES_AIRFRESH = ["Auto", "Interval"]
PRESET_MODES_AIRHUMIDIFIER = ["Auto"]
PRESET_MODES_AIRHUMIDIFIER_CA4 = ["Auto"]

SUCCESS = ["ok"]

FEATURE_SET_BUZZER = 1
FEATURE_SET_LED = 2
FEATURE_SET_CHILD_LOCK = 4
FEATURE_SET_LED_BRIGHTNESS = 8
FEATURE_SET_FAVORITE_LEVEL = 16
FEATURE_SET_AUTO_DETECT = 32
FEATURE_SET_LEARN_MODE = 64
FEATURE_SET_VOLUME = 128
FEATURE_RESET_FILTER = 256
FEATURE_SET_EXTRA_FEATURES = 512
FEATURE_SET_TARGET_HUMIDITY = 1024
FEATURE_SET_DRY = 2048
FEATURE_SET_FAN_LEVEL = 4096
FEATURE_SET_MOTOR_SPEED = 8192

FEATURE_FLAGS_AIRPURIFIER = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_LEARN_MODE
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
)

FEATURE_FLAGS_AIRPURIFIER_PRO = (
    FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_AUTO_DETECT
    | FEATURE_SET_VOLUME
)

FEATURE_FLAGS_AIRPURIFIER_PRO_V7 = (
    FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_VOLUME
)

FEATURE_FLAGS_AIRPURIFIER_2S = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
)

FEATURE_FLAGS_AIRPURIFIER_3 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_FAN_LEVEL
    | FEATURE_SET_LED_BRIGHTNESS
)

FEATURE_FLAGS_AIRPURIFIER_V3 = (
    FEATURE_SET_BUZZER | FEATURE_SET_CHILD_LOCK | FEATURE_SET_LED
)

FEATURE_FLAGS_AIRHUMIDIFIER = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB = FEATURE_FLAGS_AIRHUMIDIFIER | FEATURE_SET_DRY

FEATURE_FLAGS_AIRHUMIDIFIER_CA4 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_TARGET_HUMIDITY
    | FEATURE_SET_DRY
    | FEATURE_SET_MOTOR_SPEED
)

FEATURE_FLAGS_AIRFRESH = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
)

AIRPURIFIER_SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTITY_ID): cv.entity_ids})

SERVICE_SCHEMA_LED_BRIGHTNESS = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_BRIGHTNESS): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=2))}
)

SERVICE_SCHEMA_FAVORITE_LEVEL = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_LEVEL): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=17))}
)

SERVICE_SCHEMA_FAN_LEVEL = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_LEVEL): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=3))}
)

SERVICE_SCHEMA_VOLUME = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_VOLUME): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=100))}
)

SERVICE_SCHEMA_EXTRA_FEATURES = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_FEATURES): cv.positive_int}
)

SERVICE_SCHEMA_TARGET_HUMIDITY = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_HUMIDITY): vol.All(
            vol.Coerce(int), vol.In([30, 40, 50, 60, 70, 80])
        )
    }
)

SERVICE_SCHEMA_MOTOR_SPEED = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_MOTOR_SPEED): vol.All(
            vol.Coerce(int), vol.Clamp(min=200, max=2000)
        )
    }
)

SERVICE_TO_METHOD = {
    SERVICE_SET_BUZZER_ON: {"method": "async_set_buzzer_on"},
    SERVICE_SET_BUZZER_OFF: {"method": "async_set_buzzer_off"},
    SERVICE_SET_FAN_LED_ON: {"method": "async_set_led_on"},
    SERVICE_SET_FAN_LED_OFF: {"method": "async_set_led_off"},
    SERVICE_SET_CHILD_LOCK_ON: {"method": "async_set_child_lock_on"},
    SERVICE_SET_CHILD_LOCK_OFF: {"method": "async_set_child_lock_off"},
    SERVICE_SET_AUTO_DETECT_ON: {"method": "async_set_auto_detect_on"},
    SERVICE_SET_AUTO_DETECT_OFF: {"method": "async_set_auto_detect_off"},
    SERVICE_SET_LEARN_MODE_ON: {"method": "async_set_learn_mode_on"},
    SERVICE_SET_LEARN_MODE_OFF: {"method": "async_set_learn_mode_off"},
    SERVICE_RESET_FILTER: {"method": "async_reset_filter"},
    SERVICE_SET_LED_BRIGHTNESS: {
        "method": "async_set_led_brightness",
        "schema": SERVICE_SCHEMA_LED_BRIGHTNESS,
    },
    SERVICE_SET_FAVORITE_LEVEL: {
        "method": "async_set_favorite_level",
        "schema": SERVICE_SCHEMA_FAVORITE_LEVEL,
    },
    SERVICE_SET_FAN_LEVEL: {
        "method": "async_set_fan_level",
        "schema": SERVICE_SCHEMA_FAN_LEVEL,
    },
    SERVICE_SET_VOLUME: {"method": "async_set_volume", "schema": SERVICE_SCHEMA_VOLUME},
    SERVICE_SET_EXTRA_FEATURES: {
        "method": "async_set_extra_features",
        "schema": SERVICE_SCHEMA_EXTRA_FEATURES,
    },
    SERVICE_SET_TARGET_HUMIDITY: {
        "method": "async_set_target_humidity",
        "schema": SERVICE_SCHEMA_TARGET_HUMIDITY,
    },
    SERVICE_SET_DRY_ON: {"method": "async_set_dry_on"},
    SERVICE_SET_DRY_OFF: {"method": "async_set_dry_off"},
    SERVICE_SET_MOTOR_SPEED: {
        "method": "async_set_motor_speed",
        "schema": SERVICE_SCHEMA_MOTOR_SPEED,
    },
}


@dataclass
class SelectorType:
    """Class that holds device specific info for a xiaomi aqara or humidifier selectors."""

    unit_of_measurement: str = None
    icon: str = None
    device_class: str = None
    min: float = None
    max: float = None
    mode: str = None
    options: list = None
    step: float = None
    selector_class: Selector = None


SELECTOR_TYPES = {
    "motor_speed": SelectorType(
        unit_of_measurement="rpm",
        min=200,
        max=2000,
        step=10,
        selector_class=NumberSelector,
    ),
    "dry_mode": SelectorType(
        selector_class=BooleanSelector,
    ),
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import Miio configuration from YAML."""
    _LOGGER.warning(
        "Loading Xiaomi Miio Fan via platform setup is deprecated. "
        "Please remove it from your configuration"
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=config,
        )
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Selectors from a config entry."""
    entities = []
    if config_entry.data[CONF_FLOW_TYPE] == CONF_DEVICE:
        # host = config_entry.data[CONF_HOST]
        # token = config_entry.data[CONF_TOKEN]
        # model = config_entry.data[CONF_MODEL]
        device = hass.data[DOMAIN][config_entry.entry_id][KEY_DEVICE]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][KEY_COORDINATOR]
        selectors = []

        for selector in selectors:
            entities.append(
                XiaomiSelector(
                    f"{config_entry.title}_{selector}",
                    device,
                    config_entry,
                    f"{selector}_{config_entry.unique_id}",
                    selector,
                    coordinator,
                )
            )

    async_add_entities(entities, update_before_add=True)


class XiaomiSelector(XiaomiCoordinatedMiioEntity, Selector):
    """Representation of a generic Xiaomi attribute selector."""

    def __init__(self, name, device, entry, unique_id, coordinator):
        """Initialize the generic Xiaomi attribute selector."""
        super().__init__(name, device, entry, unique_id, coordinator=coordinator)
        self._state = None
        self._supported_features = 0
        self._device_features = 0
        self._state_attrs = {}

    @property
    def supported_features(self):
        """Flag supported features."""
        return self._supported_features

    @property
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def is_on(self):
        """Return true if attribute is on."""
        return self._state

    @staticmethod
    def _extract_value_from_attribute(state, attribute):
        value = getattr(state, attribute)
        if isinstance(value, Enum):
            return value.value

        return value

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the device off."""
        result = await self._try_command(
            "Turning the miio device off failed.", self._device.off
        )

        if result:
            self._state = False
            self._skip_update = True

    async def async_set_buzzer_on(self):
        """Turn the buzzer on."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return

        await self._try_command(
            "Turning the buzzer of the miio device on failed.",
            self._device.set_buzzer,
            True,
        )

    async def async_set_buzzer_off(self):
        """Turn the buzzer off."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return

        await self._try_command(
            "Turning the buzzer of the miio device off failed.",
            self._device.set_buzzer,
            False,
        )

    async def async_set_child_lock_on(self):
        """Turn the child lock on."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return

        await self._try_command(
            "Turning the child lock of the miio device on failed.",
            self._device.set_child_lock,
            True,
        )

    async def async_set_child_lock_off(self):
        """Turn the child lock off."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return

        await self._try_command(
            "Turning the child lock of the miio device off failed.",
            self._device.set_child_lock,
            False,
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.", self._device.set_led, True
        )

    async def async_set_led_off(self):
        """Turn the led off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_led,
            False,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirpurifierLedBrightness(brightness),
        )

    async def async_set_favorite_level(self, level: int = 1):
        """Set the favorite level."""
        if self._device_features & FEATURE_SET_FAVORITE_LEVEL == 0:
            return

        await self._try_command(
            "Setting the favorite level of the miio device failed.",
            self._device.set_favorite_level,
            level,
        )

    async def async_set_fan_level(self, level: int = 1):
        """Set the favorite level."""
        if self._device_features & FEATURE_SET_FAN_LEVEL == 0:
            return

        await self._try_command(
            "Setting the fan level of the miio device failed.",
            self._device.set_fan_level,
            level,
        )

    async def async_set_auto_detect_on(self):
        """Turn the auto detect on."""
        if self._device_features & FEATURE_SET_AUTO_DETECT == 0:
            return

        await self._try_command(
            "Turning the auto detect of the miio device on failed.",
            self._device.set_auto_detect,
            True,
        )

    async def async_set_auto_detect_off(self):
        """Turn the auto detect off."""
        if self._device_features & FEATURE_SET_AUTO_DETECT == 0:
            return

        await self._try_command(
            "Turning the auto detect of the miio device off failed.",
            self._device.set_auto_detect,
            False,
        )

    async def async_set_learn_mode_on(self):
        """Turn the learn mode on."""
        if self._device_features & FEATURE_SET_LEARN_MODE == 0:
            return

        await self._try_command(
            "Turning the learn mode of the miio device on failed.",
            self._device.set_learn_mode,
            True,
        )

    async def async_set_learn_mode_off(self):
        """Turn the learn mode off."""
        if self._device_features & FEATURE_SET_LEARN_MODE == 0:
            return

        await self._try_command(
            "Turning the learn mode of the miio device off failed.",
            self._device.set_learn_mode,
            False,
        )

    async def async_set_volume(self, volume: int = 50):
        """Set the sound volume."""
        if self._device_features & FEATURE_SET_VOLUME == 0:
            return

        await self._try_command(
            "Setting the sound volume of the miio device failed.",
            self._device.set_volume,
            volume,
        )

    async def async_set_extra_features(self, features: int = 1):
        """Set the extra features."""
        if self._device_features & FEATURE_SET_EXTRA_FEATURES == 0:
            return

        await self._try_command(
            "Setting the extra features of the miio device failed.",
            self._device.set_extra_features,
            features,
        )

    async def async_reset_filter(self):
        """Reset the filter lifetime and usage."""
        if self._device_features & FEATURE_RESET_FILTER == 0:
            return

        await self._try_command(
            "Resetting the filter lifetime of the miio device failed.",
            self._device.reset_filter,
        )


class XiaomiAirPurifierMiotSelector(XiaomiSelector):
    """Representation of a Xiaomi Air Purifier (MiOT protocol) selector."""

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirpurifierMiotLedBrightness(brightness),
        )


class XiaomiAirHumidifierSelector(XiaomiSelector):
    """Representation of a Xiaomi Air Humidifier selector."""

    def __init__(self, name, device, entry, unique_id, coordinator):
        """Initialize the plug switch."""
        super().__init__(name, device, entry, unique_id, coordinator)
        if self._model in [MODEL_AIRHUMIDIFIER_CA1, MODEL_AIRHUMIDIFIER_CB1]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB
        elif self._model in [MODEL_AIRHUMIDIFIER_CA4]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirhumidifierLedBrightness(brightness),
        )

    async def async_set_dry_on(self):
        """Turn the dry mode on."""
        if self._device_features & FEATURE_SET_DRY == 0:
            return

        await self._try_command(
            "Turning the dry mode of the miio device off failed.",
            self._device.set_dry,
            True,
        )

    async def async_set_dry_off(self):
        """Turn the dry mode off."""
        if self._device_features & FEATURE_SET_DRY == 0:
            return

        await self._try_command(
            "Turning the dry mode of the miio device off failed.",
            self._device.set_dry,
            False,
        )


class XiaomiAirHumidifierMiotSelector(XiaomiAirHumidifierSelector):
    """Representation of a Xiaomi Air Humidifier (MiOT protocol) selector."""

    @property
    def button_pressed(self):
        """Return the last button pressed."""
        if self._state:
            return AirhumidifierPressedButton(
                self._state_attrs[ATTR_BUTTON_PRESSED]
            ).name

        return None

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirhumidifierMiotLedBrightness(brightness),
        )

    async def async_set_motor_speed(self, motor_speed: int = 400):
        """Set the target motor speed."""
        if self._device_features & FEATURE_SET_MOTOR_SPEED == 0:
            return

        await self._try_command(
            "Setting the target motor speed of the miio device failed.",
            self._device.set_speed,
            motor_speed,
        )


class XiaomiAirFreshSelector(XiaomiSelector):
    """Representation of a Xiaomi Air Fresh selector."""

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.", self._device.set_led, True
        )

    async def async_set_led_off(self):
        """Turn the led off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_led,
            False,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirfreshLedBrightness(brightness),
        )

    async def async_set_extra_features(self, features: int = 1):
        """Set the extra features."""
        if self._device_features & FEATURE_SET_EXTRA_FEATURES == 0:
            return

        await self._try_command(
            "Setting the extra features of the miio device failed.",
            self._device.set_extra_features,
            features,
        )

    async def async_reset_filter(self):
        """Reset the filter lifetime and usage."""
        if self._device_features & FEATURE_RESET_FILTER == 0:
            return

        await self._try_command(
            "Resetting the filter lifetime of the miio device failed.",
            self._device.reset_filter,
        )
