"""Climate platform for UIOT integration."""

import json
import logging

from homeassistant.components.climate import (
    FAN_OFF,
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .uiot_api.const import COMPANY, DOMAIN
from .uiot_api.uiot_device import UIOTDevice, is_entity_exist

_LOGGER = logging.getLogger(__name__)


def judge_thermostatMode(thermostatMode: str) -> str:
    """Judge thermostatMode."""
    match thermostatMode:
        case "cool":
            cur_value = HVACMode.COOL
        case "heat":
            cur_value = HVACMode.HEAT
        case "fan":
            cur_value = HVACMode.FAN_ONLY
        case "dehumidification":
            cur_value = HVACMode.DRY
        case "auto":
            cur_value = HVACMode.AUTO
        case _:
            cur_value = HVACMode.AUTO
    return cur_value


def judge_fanMode(fan_mode: str) -> str:
    """Judge fanMode."""
    match fan_mode:
        case "low":
            cur_value = FAN_LOW
        case "mid":
            cur_value = FAN_MEDIUM
        case "high":
            cur_value = FAN_HIGH
        case "auto":
            cur_value = FAN_AUTO
        case "off":
            cur_value = FAN_OFF
        case _:
            cur_value = FAN_AUTO
    return cur_value


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the climate platform from a config entry."""
    _LOGGER.debug("async_setup_entry climate")

    devices_data = hass.data[DOMAIN].get("devices", [])

    device_data = []
    for device in devices_data:
        if device.get("type") == "climate":
            _LOGGER.debug("climate")
            device_data.append(device)

    entities = []
    for c_data in device_data:
        name = c_data.get("deviceName", "")
        deviceId = c_data.get("deviceId", "")
        channelNum = c_data.get("channelNum", "")
        _LOGGER.debug("name:%s", name)
        _LOGGER.debug("deviceId:%d", deviceId)
        _LOGGER.debug("channelNum:%d", channelNum)
        if not channelNum:
            _LOGGER.debug("跳过父设备")
            continue
        uiot_dev: UIOTDevice = hass.data[DOMAIN].get("uiot_dev")
        entities.append(Climate(c_data, uiot_dev, hass))

    async_add_entities(entities)

    @callback
    def handle_config_update(msg):
        if hass is None:
            return
        try:
            devices_data = msg
            device_data = []
            for device in devices_data:
                if device.get("type") == "climate":
                    _LOGGER.debug("climate")
                    _LOGGER.debug("devices_data %s", devices_data)
                    device_data.append(device)

            new_entities = []

            for s_data in device_data:
                name = s_data.get("deviceName", "")
                deviceId = s_data.get("deviceId", "")
                channelNum = s_data.get("channel", "")
                _LOGGER.debug("name:%s", name)
                _LOGGER.debug("deviceId:%d", deviceId)
                _LOGGER.debug("channelNum:%d", channelNum)
                if not channelNum:
                    _LOGGER.debug("跳过父设备！")
                    continue
                uiot_dev: UIOTDevice = hass.data[DOMAIN].get("uiot_dev")
                if not is_entity_exist(hass, deviceId):
                    new_entities.append(Climate(s_data, uiot_dev, hass))

            if new_entities:
                async_add_entities(new_entities)

        except Exception as e:
            _LOGGER.error("Error processing config update: %s", e)
            raise

    signal = "mqtt_message_network_report"
    async_dispatcher_connect(hass, signal, handle_config_update)


class Climate(ClimateEntity):
    """Representation of a UIOT home Climate."""

    def __init__(self, c_data, uiot_dev, hass: HomeAssistant) -> None:
        """Initialize the Climate."""
        self.hass = hass
        self._attr_name = c_data.get("deviceName", "")
        self._attr_unique_id = str(c_data.get("deviceId", ""))
        self.mac = self._attr_unique_id
        self._uiot_dev: UIOTDevice = uiot_dev
        properties_data = c_data.get("properties", "")
        power_switch = properties_data.get("powerSwitch", "")
        temperature_high = properties_data.get("temperature_max", 0)
        temperature_low = properties_data.get("temperature_min", 0)
        self._attr_target_temperature_high = temperature_high
        self._attr_target_temperature_low = temperature_low
        self._attr_max_temp = temperature_high
        self._attr_min_temp = temperature_low
        self._attr_temperature_unit = "°C"
        self._attr_target_temperature_step = 1
        self._attr_hvac_modes = properties_data.get("hvac_modes", "")
        self._attr_fan_modes = properties_data.get("fan_modes", "")
        if "thermostatMode" in properties_data:
            thermostatMode = properties_data.get("thermostatMode", "auto")
            self._workMode = "thermostatMode"
        else:
            thermostatMode = properties_data.get("workMode", "auto")
            self._workMode = "workMode"
        self._cur_hvac_modes = judge_thermostatMode(thermostatMode)
        self._cur_target_temperature = float(
            properties_data.get("targetTemperature", "20.0")
        )
        self._cur_current_temperature = 0
        if "currentTemperature" in properties_data:
            cTemperature = properties_data.get("currentTemperature", "")
            if cTemperature == "":
                self._cur_current_temperature = 0
            else:
                self._cur_current_temperature = float(cTemperature)

        windSpeed = properties_data.get("windSpeed", "low")
        self._fan_mode = judge_fanMode(windSpeed)
        _LOGGER.debug("hvac_modes=%s", self._attr_hvac_modes)
        _LOGGER.debug("fan_modes=%s", self._attr_fan_modes)
        if power_switch == "off":
            self._cur_hvac_modes = HVACMode.OFF

        deviceOnlineState = c_data.get("deviceOnlineState", "")
        if deviceOnlineState == 0:
            self._attr_available = False
        else:
            self._attr_available = True
        _LOGGER.debug("_attr_available=%d", self._attr_available)

        deviceName = self._attr_name
        self._attr_device_info = {
            "identifiers": {(f"{DOMAIN}", f"{self.mac}")},
            "name": f"{deviceName}",
            "manufacturer": f"{COMPANY}",
            "suggested_area": f"{c_data.get('roomName', '')}",
            "model": f"{c_data.get('model', '')}",
            "sw_version": f"{c_data.get('softwareVersion', '')}",
            "hw_version": f"{c_data.get('hardwareVersion', '')}",
        }
        _LOGGER.debug("初始化设备: %s", self._attr_name)
        _LOGGER.debug("deviceId=%s", self._attr_unique_id)
        _LOGGER.debug("mac=%s", self.mac)

        # 订阅状态主题以监听本地控制的变化
        signal = "mqtt_message_received_state_report"
        async_dispatcher_connect(hass, signal, self._handle_mqtt_message)

    @callback
    def _handle_mqtt_message(self, msg):
        """Handle incoming MQTT messages for state updates."""
        # _LOGGER.debug(f"mqtt_message的数据:{msg.payload}")
        if self.hass is None:
            return
        msg_data = json.loads(msg.payload)

        if "online_report" in msg.topic:
            data = msg_data.get("data")
            devices_data = data.get("deviceList")
            if devices_data is not None:
                for d in devices_data:
                    deviceId = d.get("deviceId", "")
                    netState = d.get("netState", "")
                    if str(deviceId) == self._attr_unique_id:
                        _LOGGER.debug(
                            "设备在线状态变化 deviceId: %d,netState:%d",
                            deviceId,
                            netState,
                        )
                        if netState == 0:
                            self._attr_available = False
                        else:
                            self._attr_available = True
                        self.async_write_ha_state()
            else:
                _LOGGER.debug("devices_data is None, skipping loop")
            return

        try:
            data = msg_data.get("data", "")
            if self._attr_unique_id == str(data.get("deviceId", "")):
                payload_str = data.get("properties", "")
            else:
                return
        except UnicodeDecodeError as e:
            _LOGGER.error("Failed to decode message payload: %s", e)
            return

        if not payload_str:
            _LOGGER.warning("Received empty payload")
            return

        _LOGGER.debug("收到设备状态更新: %s", payload_str)

        if payload_str.get("powerSwitch", ""):
            power_switch = payload_str.get("powerSwitch", "")
            if power_switch == "off":
                self._cur_hvac_modes = HVACMode.OFF
            else:
                if "thermostatMode" in payload_str:
                    thermostatMode = payload_str.get("thermostatMode", "")
                else:
                    thermostatMode = payload_str.get("workMode", "")
                self._cur_hvac_modes = judge_thermostatMode(thermostatMode)
                if "currentTemperature" in payload_str:
                    cTemperature = payload_str.get("currentTemperature", "")
                    if cTemperature == "":
                        self._cur_current_temperature = 0
                    else:
                        self._cur_current_temperature = float(cTemperature)
                if "targetTemperature" in payload_str:
                    tTemperature = payload_str.get("targetTemperature", "")
                    self._cur_target_temperature = float(tTemperature)
        if "windSpeed" in payload_str:
            windSpeed = payload_str.get("windSpeed", "")
            self._fan_mode = judge_fanMode(windSpeed)
        deviceOnlineState = data.get("deviceOnlineState", "")
        if deviceOnlineState == 0:
            self._attr_available = False
        else:
            self._attr_available = True

        self.async_write_ha_state()

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Climate supported features."""
        return (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )

    @property
    def fan_mode(self) -> str:
        """Climate fan mode."""
        return str(self._fan_mode)

    @property
    def hvac_mode(self) -> HVACMode:
        """Climate hvac mode."""
        return self._cur_hvac_modes

    @property
    def target_temperature(self) -> float:
        """Climate target temperature."""
        return self._cur_target_temperature

    @property
    def current_temperature(self) -> float | None:
        """Climate current temperature."""
        if self._cur_current_temperature > 0:
            return self._cur_current_temperature
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Climate turn on."""
        msg_data = {}
        msg_data["powerSwitch"] = "on"
        _LOGGER.debug("msg_data:%s", msg_data)
        await self._uiot_dev.dev_control_real(self._attr_unique_id, msg_data)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Climate turn off."""
        msg_data = {}
        msg_data["powerSwitch"] = "off"
        self._cur_hvac_modes = HVACMode.OFF
        _LOGGER.debug("msg_data:%s", msg_data)
        await self._uiot_dev.dev_control_real(self._attr_unique_id, msg_data)
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs) -> None:
        """Climate set temperature."""
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(((float(kwargs[ATTR_TEMPERATURE]) * 2) + 0.5) / 2)
        if self._cur_hvac_modes == HVACMode.OFF:
            await self.async_turn_on()
        msg_data = {}
        msg_data["targetTemperature"] = str(temperature)
        _LOGGER.debug("msg_data:%s", msg_data)
        await self._uiot_dev.dev_control_real(self._attr_unique_id, msg_data)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Climate set hvac mode."""
        _LOGGER.debug("hvac_mode:%s", hvac_mode)
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
            self._cur_hvac_modes = HVACMode.OFF
        else:
            if self._cur_hvac_modes == HVACMode.OFF:
                await self.async_turn_on()
            msg_data = {}
            if hvac_mode == HVACMode.COOL:
                thermostatMode = "cool"
            elif hvac_mode == HVACMode.HEAT:
                thermostatMode = "heat"
            elif hvac_mode == HVACMode.FAN_ONLY:
                thermostatMode = "fan"
            elif hvac_mode == HVACMode.DRY:
                thermostatMode = "dehumidification"
            else:
                thermostatMode = "auto"
            msg_data[self._workMode] = thermostatMode
            _LOGGER.debug("msg_data:%s", msg_data)
            uid = self._attr_unique_id
            await self._uiot_dev.dev_control_real(uid, msg_data)
            self._cur_hvac_modes = hvac_mode

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        _LOGGER.debug("fan_mode:%s", fan_mode)
        if fan_mode == FAN_LOW:
            windSpeed = "low"
        elif fan_mode == FAN_MEDIUM:
            windSpeed = "mid"
        elif fan_mode == FAN_HIGH:
            windSpeed = "high"
        elif fan_mode == FAN_AUTO:
            windSpeed = "auto"
        elif fan_mode == FAN_OFF:
            windSpeed = "off"
        else:
            windSpeed = "auto"
        msg_data = {}
        msg_data["windSpeed"] = windSpeed
        _LOGGER.debug("msg_data:%s", msg_data)
        uid = self._attr_unique_id
        await self._uiot_dev.dev_control_real(uid, msg_data)
