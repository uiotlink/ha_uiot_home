"""Sensor platform for UIOT integration."""

import json
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .uiot_api.const import COMPANY, DOMAIN
from .uiot_api.uiot_device import is_entity_exist

_LOGGER = logging.getLogger(__name__)


def senser_data_parse_list(senser_data, entities, hass: HomeAssistant) -> list:
    """senser_data_parse_list."""
    properties = senser_data.get("properties")
    deviceName = senser_data.get("deviceName")
    if properties.get("batteryPercentage"):
        senser_data["name"] = f"{deviceName}：电量"
        senser_data["sensor_type"] = "battery_level"
        senser_data["device_class"] = SensorDeviceClass.BATTERY
        senser_data["unit_of_measurement"] = PERCENTAGE
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["icon"] = "mdi:battery"
        senser_data["cur_value"] = properties.get("batteryPercentage")
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("illumination"):
        illumination = properties.get("illumination")
        senser_data["name"] = f"{deviceName}：光照"
        senser_data["sensor_type"] = "illuminance"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = "lux"
        senser_data["state_class"] = None
        senser_data["icon"] = "mdi:brightness-5"
        senser_data["cur_value"] = illumination
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("curtainAlarmState"):
        curtainAlarmState = properties.get("curtainAlarmState")
        senser_data["name"] = f"{deviceName}：报警状态"
        senser_data["sensor_type"] = "security_alarm_state"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        senser_data["icon"] = "mdi:alarm-light"
        senser_data["cur_value"] = curtainAlarmState
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("humanDetectedState"):
        humanDetectedState = properties.get("humanDetectedState")
        senser_data["name"] = f"{deviceName}：有人无人状态"
        senser_data["sensor_type"] = "human_detected_state"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        senser_data["icon"] = "mdi:account"
        if humanDetectedState == "havePerson":
            senser_data["cur_value"] = "有人"
        else:
            senser_data["cur_value"] = "无人"
        entities.append(GenericSensor(senser_data, hass))
    elif properties.get("someonePass"):
        humanDetectedState = properties.get("someonePass")
        senser_data["name"] = f"{deviceName}：有人无人状态"
        senser_data["sensor_type"] = "human_detected_state_1"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        senser_data["icon"] = "mdi:account"
        if humanDetectedState == "someone":
            senser_data["cur_value"] = "有人"
        else:
            senser_data["cur_value"] = "无人"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("humanDistanceState"):
        humanDistanceState = properties.get("humanDistanceState", "0.01")
        senser_data["name"] = f"{deviceName}：检测距离"
        senser_data["sensor_type"] = "human_distance_state"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = "m"
        senser_data["state_class"] = None
        senser_data["icon"] = "mdi:ruler"
        senser_data["cur_value"] = humanDistanceState
        entities.append(GenericSensor(senser_data, hass))
    elif properties.get("humanDistanceState_1"):
        humanDistanceState = properties.get("humanDistanceState_1", "0.01")
        senser_data["name"] = f"{deviceName}：检测距离"
        senser_data["sensor_type"] = "human_distance_state_1"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = "m"
        senser_data["state_class"] = None
        senser_data["icon"] = "mdi:ruler"
        senser_data["cur_value"] = humanDistanceState
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("humanActiveState"):
        humanActiveState = properties.get("humanActiveState")
        senser_data["name"] = f"{deviceName}：体动特征"
        senser_data["sensor_type"] = "human_active_state"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        senser_data["icon"] = "mdi:walk"
        if humanActiveState == "inactivity":
            senser_data["cur_value"] = "静止"
        elif humanActiveState == "noFeatures":
            senser_data["cur_value"] = "无特征"
        elif humanActiveState == "active":
            senser_data["cur_value"] = "活跃"
        else:
            senser_data["cur_value"] = "无特征"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("contactState"):
        contactState = properties.get("contactState")
        senser_data["name"] = f"{deviceName}：开合状态"
        senser_data["sensor_type"] = "contact"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        if contactState == "close":
            senser_data["cur_value"] = "关闭"
            senser_data["icon"] = "mdi:door-closed"
        else:
            senser_data["cur_value"] = "打开"
            senser_data["icon"] = "mdi:door-open"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("sensorWorkMode"):
        sensorWorkMode = properties.get("sensorWorkMode")
        senser_data["name"] = f"{deviceName}：工作模式"
        senser_data["sensor_type"] = "sensor_work_mode"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        if sensorWorkMode == "sensor":
            senser_data["cur_value"] = "传感设备"
            senser_data["icon"] = "mdi:gauge"
        else:
            senser_data["cur_value"] = "安防设备"
            senser_data["icon"] = "mdi:shield-home"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("temperature"):
        temperature = properties.get("temperature")
        senser_data["name"] = f"{deviceName}：温度"
        senser_data["sensor_type"] = "temperature"
        senser_data["device_class"] = SensorDeviceClass.TEMPERATURE
        senser_data["unit_of_measurement"] = UnitOfTemperature.CELSIUS
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["cur_value"] = temperature
        senser_data["icon"] = "mdi:thermometer"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("humidity"):
        humidity = properties.get("humidity")
        senser_data["name"] = f"{deviceName}：湿度"
        senser_data["sensor_type"] = "humidity"
        senser_data["device_class"] = SensorDeviceClass.HUMIDITY
        senser_data["unit_of_measurement"] = PERCENTAGE
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["cur_value"] = humidity
        senser_data["icon"] = "mdi:water-percent"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("pm25"):
        pm25 = properties.get("pm25")
        senser_data["name"] = f"{deviceName}：PM2.5"
        senser_data["sensor_type"] = "pm25"
        senser_data["device_class"] = None
        unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
        senser_data["unit_of_measurement"] = unit_of_measurement
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["cur_value"] = pm25
        senser_data["icon"] = "mdi:blur"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("noise"):
        noise = properties.get("noise")
        senser_data["name"] = f"{deviceName}：噪音"
        senser_data["sensor_type"] = "noise"
        senser_data["device_class"] = SensorDeviceClass.SOUND_PRESSURE
        senser_data["unit_of_measurement"] = SIGNAL_STRENGTH_DECIBELS
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["cur_value"] = noise
        senser_data["icon"] = "mdi:volume-high"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("co2"):
        co2 = properties.get("co2")
        senser_data["name"] = f"{deviceName}：CO2"
        senser_data["sensor_type"] = "co2"
        senser_data["device_class"] = SensorDeviceClass.CO2
        senser_data["unit_of_measurement"] = CONCENTRATION_PARTS_PER_MILLION
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["cur_value"] = co2
        senser_data["icon"] = "mdi:molecule-co2"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("tvoc"):
        tvoc = properties.get("tvoc")
        senser_data["name"] = f"{deviceName}：TVOC"
        senser_data["sensor_type"] = "tvoc"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = CONCENTRATION_PARTS_PER_BILLION
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["cur_value"] = tvoc
        senser_data["icon"] = "mdi:chemical-weapon"
        entities.append(GenericSensor(senser_data, hass))

    if properties.get("formaldehyde"):
        formaldehyde = properties.get("formaldehyde")
        senser_data["name"] = f"{deviceName}：甲醛"
        senser_data["sensor_type"] = "formaldehyde"
        senser_data["device_class"] = None
        unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
        senser_data["unit_of_measurement"] = unit_of_measurement
        senser_data["state_class"] = SensorStateClass.MEASUREMENT
        senser_data["cur_value"] = formaldehyde
        senser_data["icon"] = "mdi:chemical-weapon"
        entities.append(GenericSensor(senser_data, hass))

    if "alarmState" in properties:
        alarmState = properties.get("alarmState")
        senser_data["name"] = f"{deviceName}：报警状态"
        senser_data["sensor_type"] = "alarmState"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        if alarmState == "normal":
            senser_data["cur_value"] = "正常"
            senser_data["icon"] = "mdi:shield-alert"
        else:
            senser_data["cur_value"] = "报警"
            senser_data["icon"] = "mdi:shield-alert"
        entities.append(GenericSensor(senser_data, hass))
    elif "securityAlarm" in properties:
        alarmState = properties.get("securityAlarm")
        senser_data["name"] = f"{deviceName}：报警状态"
        senser_data["sensor_type"] = "securityAlarm"
        senser_data["device_class"] = None
        senser_data["unit_of_measurement"] = None
        senser_data["state_class"] = None
        if alarmState == "normal":
            senser_data["cur_value"] = "正常"
            senser_data["icon"] = "mdi:shield-alert"
        else:
            senser_data["cur_value"] = "报警"
            senser_data["icon"] = "mdi:shield-alert"
        entities.append(GenericSensor(senser_data, hass))

    return entities


def judge_humanActiveState(humanActiveState: str) -> str:
    """Judge humanActiveState."""
    if humanActiveState == "inactivity":
        cur_value = "静止"
    elif humanActiveState == "noFeatures":
        cur_value = "无特征"
    elif humanActiveState == "active":
        cur_value = "活跃"
    else:
        cur_value = "无特征"
    return cur_value


def judge_alarmState(alarmState: str) -> str:
    """Judge alarmState."""
    if alarmState == "normal":
        cur_value = "正常"
    else:
        cur_value = "报警"
    _LOGGER.debug("alarmState:%s,cur_value:%s", alarmState, cur_value)
    return cur_value


def judge_curtainAlarmState(curtainAlarmState: str) -> str:
    """Judge curtainAlarmState."""
    if curtainAlarmState == "out":
        cur_value = "外出"
    elif curtainAlarmState == "intrude":
        cur_value = "闯入"
    else:
        cur_value = "正常"
    return cur_value


def update_senser_status(self, payload_str):
    """update_senser_status."""
    if self._sensor_type == "battery_level":
        self._value = payload_str.get("batteryPercentage", "")
    elif self._sensor_type == "illuminance":
        self._value = payload_str.get("illumination", "")
    elif self._sensor_type == "human_distance_state":
        self._value = payload_str.get("humanDistanceState", "")
    elif self._sensor_type == "human_distance_state_1":
        self._value = payload_str.get("humanDistanceState_1", "")
    elif self._sensor_type == "security_alarm_state":
        curtainAlarmState = payload_str.get("curtainAlarmState")
        self._value = judge_curtainAlarmState(curtainAlarmState)
    elif self._sensor_type == "human_detected_state":
        humanDetectedState = payload_str.get("humanDetectedState")
        if humanDetectedState == "havePerson":
            self._value = "有人"
        else:
            self._value = "无人"
    elif self._sensor_type == "human_detected_state_1":
        humanDetectedState = payload_str.get("someonePass")
        if humanDetectedState == "someone":
            self._value = "有人"
        else:
            self._value = "无人"
    elif self._sensor_type == "human_active_state":
        humanActiveState = payload_str.get("humanActiveState")
        if payload_str.get("humanDetectedState") == "noPerson":
            humanActiveState = "noFeatures"
        self._value = judge_humanActiveState(humanActiveState)
    elif self._sensor_type == "contact":
        contactState = payload_str.get("contactState")
        if contactState:
            if contactState == "close":
                self._value = "关闭"
            else:
                self._value = "打开"
    elif self._sensor_type == "sensor_work_mode":
        sensorWorkMode = payload_str.get("sensorWorkMode")
        if sensorWorkMode:
            if sensorWorkMode == "sensor":
                self._value = "传感设备"
            else:
                self._value = "安防设备"
    elif self._sensor_type == "temperature":
        self._value = payload_str.get("temperature", "")
    elif self._sensor_type == "humidity":
        self._value = payload_str.get("humidity", "")
    elif self._sensor_type == "pm25":
        self._value = payload_str.get("pm25", "")
    elif self._sensor_type == "noise":
        self._value = payload_str.get("noise", "")
    elif self._sensor_type == "co2":
        self._value = payload_str.get("co2", "")
    elif self._sensor_type == "tvoc":
        self._value = payload_str.get("tvoc", "")
    elif self._sensor_type == "formaldehyde":
        self._value = payload_str.get("formaldehyde", "")
    elif self._sensor_type == "alarmState":
        if "alarmState" in payload_str:
            alarmState = payload_str.get("alarmState")
            _LOGGER.debug("alarmState:%s", alarmState)
            self._value = judge_alarmState(alarmState)
        else:
            _LOGGER.debug("alarmState属性不存在")
    elif self._sensor_type == "securityAlarm":
        if "securitySwitch" in payload_str:
            alarmState = payload_str.get("securitySwitch")
            _LOGGER.debug("securitySwitch:%s", alarmState)
            if alarmState == "armed":
                if "someonePass" in payload_str:
                    humanDetectedState = payload_str.get("someonePass")
                    if humanDetectedState == "someone":
                        self._value = "报警"
                    else:
                        self._value = "正常"
                elif "curtainAlarmState" in payload_str:
                    humanDetectedState = payload_str.get("curtainAlarmState")
                    if humanDetectedState == "intrude":
                        self._value = "报警"
                    else:
                        self._value = "正常"
                elif "humanDetectedState" in payload_str:
                    humanDetectedState = payload_str.get("humanDetectedState")
                    if humanDetectedState == "havePerson":
                        self._value = "报警"
                    else:
                        self._value = "正常"
                else:
                    self._value = "正常"
            else:
                self._value = "正常"
        else:
            self._value = "正常"
    if self._value == "":
        self._value = "0"


async def async_setup_entry(
    hass: HomeAssistant, config_entry, async_add_entities: AddEntitiesCallback
):
    """Set up the sensor from a config entry."""
    devices_data = hass.data[DOMAIN].get("devices", [])

    device_data = []
    for device in devices_data:
        if device.get("type") == "senser":
            _LOGGER.debug("senser")
            device_data.append(device)

    entities = []
    for senser_data in device_data:
        name = senser_data.get("deviceName")
        deviceId = senser_data.get("deviceId")
        _LOGGER.debug("name:%s", name)
        _LOGGER.debug("deviceId:%d", deviceId)
        entities = senser_data_parse_list(senser_data, entities, hass)
    if entities:
        async_add_entities(entities)

    @callback
    def handle_config_update(msg):
        _LOGGER.debug("devices_data %s", msg)
        try:
            devices_data = msg
            device_data = []
            for device in devices_data:
                if device.get("type") == "senser":
                    _LOGGER.debug("senser")
                    device_data.append(device)

            entities = []

            for data in device_data:
                name = data.get("deviceName", "")
                deviceId = data.get("deviceId", "")
                _LOGGER.debug("name:%s", name)
                _LOGGER.debug("deviceId:%d", deviceId)
                if not is_entity_exist(hass, deviceId):
                    entities = senser_data_parse_list(data, entities, hass)

            if entities:
                async_add_entities(entities)

        except Exception as e:
            _LOGGER.error("Error processing config update: %s", e)
            raise

    signal = "mqtt_message_network_report"
    async_dispatcher_connect(hass, signal, handle_config_update)


class GenericSensor(SensorEntity):
    """Generic Sensor Class."""

    def __init__(self, senser_data, hass: HomeAssistant) -> None:
        """Init Generic Sensor Class."""
        self._sensor_type = senser_data.get("sensor_type")
        self._unique_id = f"{self._sensor_type}_{senser_data.get('deviceId')}"
        self._attr_unique_id = str(senser_data.get("deviceId"))
        self._attr_name = senser_data.get("name")
        self._attr_device_class = senser_data.get("device_class")
        measurement = senser_data.get("unit_of_measurement")
        self._attr_native_unit_of_measurement = measurement
        self._attr_state_class = senser_data.get("state_class")
        self._attr_icon = senser_data.get("icon")
        self._value = senser_data.get("cur_value")

        deviceOnlineState = senser_data.get("deviceOnlineState", "")
        if deviceOnlineState == 0:
            self._attr_available = False
        else:
            self._attr_available = True
        _LOGGER.debug("_attr_available=%d", self._attr_available)

        self._attr_device_info = {
            "identifiers": {(f"{DOMAIN}", f"{self._attr_unique_id}")},
            "name": f"{senser_data.get('deviceName', '')}",
            "manufacturer": f"{COMPANY}",
            "suggested_area": f"{senser_data.get('roomName', '')}",
            "model": f"{senser_data.get('model', '')}",
            "sw_version": f"{senser_data.get('softwareVersion', '')}",
            "hw_version": f"{senser_data.get('hardwareVersion', '')}",
        }
        _LOGGER.debug("初始化设备: %s", self._attr_name)
        _LOGGER.debug("deviceId=%s", self._unique_id)
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

        _LOGGER.debug(
            "self._attr_unique_id=%s,收到设备状态更新: %s",
            self._attr_unique_id,
            payload_str,
        )
        update_senser_status(self, payload_str)

        _LOGGER.debug("self._value: %s", self._value)
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return self._unique_id

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._value

    @property
    def available(self):
        """Return available of the sensor."""
        return self._attr_available

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self._sensor_type == "contact":
            if self.native_value == "打开":
                return "mdi:door-open"
            return "mdi:door-closed"
        if self._sensor_type == "sensor_work_mode":
            if self.native_value == "传感设备":
                return "mdi:gauge"
            return "mdi:shield-home"
        if self._sensor_type == "battery_level":
            _value = int(self.native_value)
            if _value > 90:
                self._attr_icon = "mdi:battery"
            elif _value > 70:
                self._attr_icon = "mdi:battery-80"
            elif _value > 50:
                self._attr_icon = "mdi:battery-60"
            elif _value > 30:
                self._attr_icon = "mdi:battery-40"
            elif _value > 15:
                self._attr_icon = "mdi:battery-20"
            else:
                self._attr_icon = "mdi:battery-alert"
        return self._attr_icon
