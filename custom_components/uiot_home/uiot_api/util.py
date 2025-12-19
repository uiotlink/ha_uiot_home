"""Uiot util api."""

import base64
import binascii
from collections import OrderedDict
from datetime import datetime
import hashlib
import json

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def parse_byte2hex_str(buf: bytes) -> str:
    """parse_byte2hex_str."""
    # 使用列表推导式优化性能
    # format(byte, '02x') 直接生成补零的小写十六进制
    return "".join(f"{byte:02x}" for byte in buf)


def compute_md5(params: dict, secret: str) -> str:
    """compute_md5."""
    temp_sorted = {key: params[key] for key in sorted(params)}
    # print(temp_sorted)
    md5_raw_str: str = ""
    for key, val in temp_sorted.items():
        if key == "sign" or val == "" or key == "Content-Type":
            continue
        if md5_raw_str != "":
            md5_raw_str += "&"
        md5_raw_str = md5_raw_str + key + "=" + val
    md5_raw_str += secret
    md5_hash = hashlib.md5()
    md5_hash.update(md5_raw_str.encode("utf-8"))
    return md5_hash.hexdigest()


def compute_md5_str(params: str) -> str:
    """compute_md5_str."""
    md5_hash = hashlib.md5()
    md5_hash.update(params.encode("utf-8"))
    return md5_hash.hexdigest()


def calculate_mqtt_sign(message: str, app_secret: str) -> str:
    """calculate_mqtt_sign."""
    # 使用 OrderedDict 保证字段顺序
    data = json.loads(message, object_pairs_hook=OrderedDict)

    # 转换为标准 dict 并提取 header 和 payload
    json_obj = dict(data)
    header = json_obj.get("header", {})
    payload = json_obj.get("payload", {})

    header_json = json.dumps(header, separators=(",", ":"))
    payload_json = json.dumps(payload, separators=(",", ":"))
    # 构建待签名字符串
    mds_str = (
        f"header={header_json}"  # 第一部分
        f"&payload={payload_json}"  # 第二部分
        f"{app_secret}"  # 第三部分
    )
    # 计算 MD5
    return hashlib.md5(mds_str.encode("utf-8")).hexdigest()


def encrypt1(plaintext: str, key: str) -> str:
    """encrypt1."""
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")

    # 创建AES加密器（ECB模式，PKCS7填充）
    cipher = AES.new(key_bytes, AES.MODE_ECB)

    # 明文处理：转为字节 + PKCS7填充
    plaintext_bytes = plaintext.encode("utf-8")
    padded_bytes = pad(plaintext_bytes, AES.block_size)

    # 执行加密
    encrypted_bytes = cipher.encrypt(padded_bytes)

    # 结果处理：字节 → 十六进制字符串 → Base64编码
    # hex_str = binascii.hexlify(encrypted_bytes).decode('utf-8')
    hex_str = binascii.hexlify(encrypted_bytes).decode("utf-8")
    return base64.b64encode(hex_str.encode("utf-8")).decode("utf-8")


def decrypt1(ciphertext: str, key: str) -> str:
    """decrypt1."""
    # 密钥处理（保持与加密逻辑一致）
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")

    # 创建解密器
    cipher = AES.new(key_bytes, AES.MODE_ECB)

    # Base64解码 → hex解码 → 原始加密字节
    hex_str = base64.b64decode(ciphertext).decode("utf-8")
    encrypted_bytes = binascii.unhexlify(hex_str)

    # 执行解密
    decrypted_bytes = cipher.decrypt(encrypted_bytes)

    # 去除填充并解码
    plaintext_bytes = unpad(decrypted_bytes, AES.block_size)
    return plaintext_bytes.decode("utf-8")


def get_timestamp_str() -> str:
    """get_timestamp_str."""
    return str(int(datetime.now().timestamp() * 1000))


def phase_dev_list(list_data: str) -> list:
    """Filter and classify devices based on their model."""
    # 定义模型与类型的映射关系
    MODEL_TYPE_MAP = {
        "l_dimmer_switch": "light",
        "l_smart_strip_controller": "light",
        "l_smart_color_temperature_spotlight": "light",
        "l_smart_dimming_controller": "light",
        "l_smart_tube_spotlight": "light",
        "l_magnetic_color_controller": "light",
        "l_smart_dimming_dali": "light",
        "l_smart_color_temperature_dali": "light",
        "l_smart_color_light": "light",
        "l_smart_dimming_spotlight": "light",
        "l_smart_color_temperature_light": "light",
        "l_zf_single_switch": "switch",
        "l_zf_double_switch": "switch",
        "l_zf_three_switch": "switch",
        "l_zf_four_switch": "switch",
        "l_m_single_switch_box": "switch",
        "l_m_double_switch_box": "switch",
        "l_m_three_switch_box": "switch",
        "l_m_four_switch_box": "switch",
        "l_f_single_switch": "switch",
        "l_f_double_switch": "switch",
        "l_f_three_switch": "switch",
        "l_zf_single_switch_ai_smart_screen_config_switch": "switch",
        "l_zf_single_switch_ai_smart_screen_e_series": "switch",
        "l_zf_double_switch_ai_smart_large_screen": "switch",
        "l_zf_single_switch_ai_smart_screen": "switch",
        "hvac_general_module_child_relay_switch": "switch",
        "hvac_general_module_child_relay_garagedoor": "switch",
        "ss_smart_door_sensor": "senser",
        "ss_ir_curtain_sensor": "senser",
        "ss_exist_human_detector": "senser",
        "ss_ir_radar_human_detector": "senser",
        "env_temp_hum_sensor": "senser",
        "env_4_1_air_genius_formaldehyde": "senser",
        "env_4_1_air_genius_co2": "senser",
        "env_4_1_air_genius_pm25": "senser",
        "env_4_1_air_box_pm25": "senser",
        "env_5_1_air_genius_co2": "senser",
        "env_6_1_air_genius": "senser",
        "env_7_1_air_genius_tvoc": "senser",
        "env_7_1_air_box_tvoc": "senser",
        "env_7_1_air_genius": "senser",
        "env_7_1_air_box": "senser",
        "env_8_1_air_genius": "senser",
        "env_8_1_air_box": "senser",
        "wc_smart_roller_motor": "cover",
        "wc_smart_curtain_motor": "cover",
        "wc_sliding_window_opener": "cover",
        "wc_panning_window_opener": "cover",
        "wc_single_motor_control_panel": "cover",
        "wc_double_motor_control_panel": "cover",
        "ai_smart_screen_config_motor": "cover",
        "wc_dream_curtain_motor": "cover",
        "wc_smart_curtain_motor_box": "cover",
        "wc_smart_curtain_motor_box": "cover",
        "hs_smoke_detector": "senser",
        "hs_water_leak_detector": "senser",
        "hs_flammable_gas_detector": "senser",
        "hs_gas_leak_detector": "senser",
        "hs_sos_button": "senser",
        "ss_human_area_exist_detector": "senser",
        "ss_exist_human_detector_pro": "senser",
        "ss_ir_human_detector": "senser",
        "ss_ir_curtain_detector": "senser",
        "ss_ir_curtain_detector_active": "senser",
        "ss_ir_curtain_sensor": "senser",
        "hvac_thermostat_3h1_e3_child_ac": "climate",
        "hvac_thermostat_3h1_e3_child_fair_power": "fan",
        "hvac_thermostat_3h1_e3_child_wfh": "water_heater",
        "hvac_smart_gateway_engineering_ac": "climate",
        "hvac_smart_gateway_general_ac": "climate",
        "hvac_smart_gateway_pro_ms_ac": "climate",
        "hvac_fresh_air_3h1_th": "fan",
        "hvac_ac_e3": "climate",
        "hvac_wfh_e3": "water_heater",
        "hvac_water_floor_heating_3h1_th": "water_heater",
        "hvac_water_floor_heating_th": "water_heater",
        "ha_smart_socket": "switch",
        "ha_ir_socket_kookong": "switch",
        "hvac_ir_air_conditioner_maku": "climate",
        "hvac_thermostat_3h1_c_child_ac": "climate",
        "hvac_thermostat_3h1_c_child_efh": "water_heater",
        "hvac_super_temp_panel_child_fan": "climate",
        "hvac_general_module_child_relay_fair": "fan",
        "hvac_general_module_child_relay_fair_lv2": "fan",
        "hvac_485_fair_chino": "fan",
        "hvac_485_fair_bole_cs2": "fan",
        "hvac_485_fair_aidishi_kf800rm": "fan",
        "hvac_485_ac_gree_fgr35d": "climate",
        "hvac_485_ac_hitachi_pcpihhq": "climate",
        "hvac_485_ac_haier_casarte_ycja001": "climate",
        "hvac_485_wfh_ya_te_lee6606": "water_heater",
        "hvac_485_efh_org": "water_heater",
        "hvac_485_wfh_org": "water_heater",
        "hvac_floor_heating_panel_2s1_child_efh": "water_heater",
        "hvac_floor_heating_panel_2s1_child_wfh": "water_heater",
        "hvac_water_floor_heating_3h1_child_wfh": "water_heater",
        "hvac_general_module_child_relay_wfh": "water_heater",
        "i_smart_cloud_speaker_X10": "media_player",
        "multi_series_panel_switch": "switch",
        "multi_series_panel_motor": "cover",
        "hvac_fan_coil_3h1_th": "climate",
        "smart_protocol_conversion_module_child_relay_fan": "climate",
        "hvac_general_module_child_relay_fan": "climate",
    }

    MODEL_ABILITY_MAP = {
        "wc_smart_roller_motor": 2,
        "wc_smart_curtain_motor": 2,
        "wc_sliding_window_opener": 2,
        "wc_panning_window_opener": 2,
        "wc_single_motor_control_panel": 1,
        "ai_smart_screen_config_motor": 1,
        "wc_double_motor_control_panel": 1,
        "wc_dream_curtain_motor": 3,
        "wc_smart_curtain_motor_box": 2,
        "multi_series_panel_motor": 1,
    }

    # 定义默认属性
    DEFAULT_PROPERTIES = {
        "ss_smart_door_sensor": {
            "contactState": "close",
            "batteryPercentage": "100",
            "batteryState": "normal",
            "sensorWorkMode": "sensor",
        },
        "ss_ir_curtain_sensor": {
            "curtainAlarmState": "normal",
            "batteryPercentage": "100",
            "batteryState": "normal",
            "sensorWorkMode": "sensor",
            "illumination": "500",
        },
        "ss_exist_human_detector": {
            "illumination": "500",
            "humanDetectedState": "havePerson",
            "humanDistanceState": "0.1",
            "humanDirectionState": "noMovement",
            "humanActiveState": "inactivity",
            "securityAlarm": "normal",
            "sensorWorkMode": "sensor",
        },
        "ss_human_area_exist_detector": {
            "illumination": "500",
            "humanDetectedState": "havePerson",
            "sensorWorkMode": "sensor",
        },
        "ss_exist_human_detector_pro": {
            "illumination": "500",
            "humanDetectedState": "havePerson",
            "humanDistanceState_1": "0.1",
            "securityAlarm": "normal",
            "sensorWorkMode": "sensor",
        },
        "ss_ir_human_detector": {
            "batteryPercentage": "100",
            "batteryState": "normal",
            "someonePass": "normal",
            "securityAlarm": "normal",
            "sensorWorkMode": "sensor",
        },
        "ss_ir_curtain_detector": {
            "batteryPercentage": "100",
            "batteryState": "normal",
            "curtainAlarmState": "normal",
            "securityAlarm": "normal",
            "sensorWorkMode": "sensor",
        },
        "ss_ir_curtain_detector_active": {
            "curtainAlarmState": "normal",
            "securityAlarm": "normal",
            "sensorWorkMode": "sensor",
        },
        "ss_ir_curtain_sensor": {
            "illumination": "500",
            "batteryPercentage": "100",
            "batteryState": "normal",
            "curtainAlarmState": "normal",
            "securityAlarm": "normal",
            "sensorWorkMode": "sensor",
        },
        "ss_ir_radar_human_detector": {
            "humanDetectedState": "havePerson",
            "humanActiveState": "inactivity",
            "batteryPercentage": "100",
            "sensorWorkMode": "sensor",
        },
        "env_temp_hum_sensor": {
            "batteryPercentage": "100",
            "temperature": "20.0",
            "humidity": "30.0",
        },
        "env_4_1_air_genius_formaldehyde": {
            "illumination": "500",
            "formaldehyde": "0.01",
            "humidity": "30.0",
            "temperature": "25.0",
        },
        "env_4_1_air_genius_co2": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
        },
        "env_4_1_air_genius_pm25": {
            "illumination": "500",
            "pm25": "10",
            "humidity": "30.0",
            "temperature": "25.0",
        },
        "env_4_1_air_box_pm25": {
            "illumination": "500",
            "pm25": "10",
            "humidity": "30.0",
            "temperature": "25.0",
        },
        "env_5_1_air_genius_co2": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "tvoc": "30",
        },
        "env_6_1_air_genius": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "pm25": "10",
            "noise": "30",
        },
        "env_7_1_air_genius_tvoc": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "pm25": "10",
            "noise": "30",
            "tvoc": "30",
        },
        "env_7_1_air_box_tvoc": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "pm25": "10",
            "noise": "30",
            "tvoc": "30",
        },
        "env_7_1_air_genius": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "pm25": "10",
            "noise": "30",
            "formaldehyde": "0.01",
        },
        "env_7_1_air_box": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "pm25": "10",
            "noise": "30",
            "formaldehyde": "0.01",
        },
        "env_8_1_air_genius": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "pm25": "10",
            "noise": "30",
            "formaldehyde": "0.01",
            "tvoc": "30",
        },
        "env_8_1_air_box": {
            "illumination": "500",
            "co2": "100",
            "humidity": "30.0",
            "temperature": "25.0",
            "pm25": "10",
            "noise": "30",
            "formaldehyde": "0.01",
            "tvoc": "30",
        },
        "wc_smart_roller_motor": {
            "curtainPosition": 0,
            "motorSwitch": "off",
        },
        "wc_smart_curtain_motor": {
            "curtainPosition": 0,
            "motorSwitch": "off",
        },
        "wc_sliding_window_opener": {
            "curtainPosition": 0,
            "motorSwitch": "off",
        },
        "wc_panning_window_opener": {
            "curtainPosition": 0,
            "motorSwitch": "off",
        },
        "wc_single_motor_control_panel": {
            "motorSwitch": "off",
        },
        "ai_smart_screen_config_motor": {
            "motorSwitch": "off",
        },
        "wc_double_motor_control_panel": {
            "motorSwitch": "off",
        },
        "wc_dream_curtain_motor": {
            "curtainPosition": 0,
            "motorSwitch": "off",
            "blindAngle": "shading135",
        },
        "wc_smart_curtain_motor_box": {
            "curtainPosition": 0,
            "motorSwitch": "off",
        },
        "hs_smoke_detector": {
            "batteryPercentage": "100",
            "alarmState": "normal",
        },
        "hs_water_leak_detector": {
            "batteryPercentage": "100",
            "alarmState": "normal",
        },
        "hs_flammable_gas_detector": {
            "alarmState": "normal",
        },
        "hs_gas_leak_detector": {
            "alarmState": "normal",
        },
        "hs_sos_button": {
            "batteryPercentage": "100",
            "alarmState": "normal",
        },
        "hvac_thermostat_3h1_e3_child_ac": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_thermostat_3h1_e3_child_fair_power": {
            "powerSwitch": "off",
            "windSpeed": "low",
            "fan_modes": ["low", "mid", "high"],
        },
        "hvac_thermostat_3h1_e3_child_wfh": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "waterValveSwitch",
        },
        "hvac_smart_gateway_engineering_ac": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_smart_gateway_general_ac": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_smart_gateway_pro_ms_ac": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 30,
            "temperature_min": 19,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_fresh_air_3h1_th": {
            "powerSwitch": "off",
            "windSpeed": "low",
            "fan_modes": ["low", "mid", "high"],
        },
        "hvac_ac_e3": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_wfh_e3": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "waterValveSwitch",
        },
        "hvac_water_floor_heating_3h1_th": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "waterValveSwitch",
        },
        "hvac_water_floor_heating_th": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "waterValveSwitch",
        },
        "hvac_ir_air_conditioner_maku": {
            "targetTemperature": "26",
            "workMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 30,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "auto", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_thermostat_3h1_c_child_ac": {
            "targetTemperature": "26",
            "workMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high"],
        },
        "hvac_thermostat_3h1_c_child_efh": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "heatingSwitch",
        },
        "hvac_super_temp_panel_child_fan": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_general_module_child_relay_fair": {
            "powerSwitch": "off",
            "windSpeed": "low",
            "fan_modes": ["off", "low", "mid", "high"],
        },
        "hvac_general_module_child_relay_fair_lv2": {
            "powerSwitch": "off",
            "windSpeed": "low",
            "fan_modes": ["off", "low", "high"],
        },
        "hvac_485_fair_chino": {
            "powerSwitch": "off",
            "windSpeed": "low",
            "fan_modes": ["low", "mid", "high"],
        },
        "hvac_485_fair_aidishi_kf800rm": {
            "powerSwitch": "off",
            "windSpeed": "low",
            "fan_modes": ["low", "mid", "high"],
        },
        "hvac_485_fair_bole_cs2": {
            "powerSwitch": "off",
            "windSpeed": "low",
            "fan_modes": ["low", "mid", "high"],
        },
        "hvac_485_ac_gree_fgr35d": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 30,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only", "auto"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_485_ac_hitachi_pcpihhq": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 30,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only", "auto"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_485_ac_haier_casarte_ycja001": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 30,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "dry", "fan_only", "auto"],
            "fan_modes": ["low", "medium", "high", "auto"],
        },
        "hvac_485_wfh_ya_te_lee6606": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 45,
            "temperature_min": 5,
            "value_switch_type": "",
        },
        "hvac_485_efh_org": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 35,
            "temperature_min": 5,
            "value_switch_type": "",
        },
        "hvac_485_wfh_org": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 35,
            "temperature_min": 5,
            "value_switch_type": "",
        },
        "hvac_floor_heating_panel_2s1_child_wfh": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "waterValveSwitch",
        },
        "hvac_water_floor_heating_3h1_child_wfh": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "waterValveSwitch",
        },
        "hvac_floor_heating_panel_2s1_child_efh": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "heatingSwitch",
        },
        "hvac_general_module_child_relay_wfh": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "powerSwitch": "off",
            "temperature_max": 32,
            "temperature_min": 16,
            "value_switch_type": "heatingSwitch",
        },
        "multi_series_panel_motor": {
            "curtainPosition": 0,
            "motorSwitch": "off",
        },
        "hvac_fan_coil_3h1_th": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "fan_only"],
            "fan_modes": ["low", "medium", "high"],
        },
        "smart_protocol_conversion_module_child_relay_fan": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "fan_only"],
            "fan_modes": ["low", "medium", "high", "off"],
        },
        "hvac_general_module_child_relay_fan": {
            "currentTemperature": "0",
            "targetTemperature": "26",
            "thermostatMode": "cool",
            "powerSwitch": "off",
            "windSpeed": "low",
            "temperature_max": 32,
            "temperature_min": 16,
            "hvac_modes": ["off", "cool", "heat", "fan_only"],
            "fan_modes": ["low", "medium", "high", "off"],
        },
    }

    # 辅助函数：初始化 properties
    def initialize_properties(device, default_properties):
        has_properties = "properties" in device
        is_valid_dict = isinstance(device.get("properties"), dict)
        if not (has_properties and is_valid_dict):
            device["properties"] = {}
        for key, value in default_properties.items():
            if key not in device["properties"]:
                device["properties"][key] = value
        if (
            "humanActiveState" in device["properties"]
            and "humanDetectedState" in device["properties"]
        ):
            if device["properties"]["humanDetectedState"] == "noPerson":
                device["properties"]["humanActiveState"] = "noFeatures"

    # 主逻辑
    filtered_devices = []
    data = json.loads(list_data)
    for device in data.get("deviceList", []):
        model = device.get("model", "")
        if model not in MODEL_TYPE_MAP:
            continue

        # 设置设备类型
        device["type"] = MODEL_TYPE_MAP[model]

        if model in MODEL_ABILITY_MAP:
            if ("channel" in device and device.get("channel", 0) == 0) or (
                "channelNum" in device and device.get("channelNum", 0) == 0
            ):
                continue

            device["ability_type"] = MODEL_ABILITY_MAP[model]

        # 初始化 properties（如果需要）
        if model in DEFAULT_PROPERTIES:
            initialize_properties(device, DEFAULT_PROPERTIES[model])

        # 添加到结果列表
        filtered_devices.append(device)
    # print(filtered_devices)
    return filtered_devices


def phase_smart_list(list_data, devices_list: list) -> list:
    """Phase smart list."""
    filtered_devices = devices_list
    data = list_data.get("data", "")
    smartList = json.loads(data)
    for device in smartList.get("smartList", []):
        # 设置设备类型
        device["type"] = "scene"
        filtered_devices.append(device)
    # print(filtered_devices)
    return filtered_devices
