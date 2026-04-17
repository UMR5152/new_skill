#!/usr/bin/env python3
"""
家居控制服务端 - MQTT 版本
监听 HTTP 请求，转换为 MQTT 消息发送到设备
"""

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
from typing import Optional, Dict, Any
import os

app = Flask(__name__)

# MQTT 配置
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = "home-control-gateway"

# MQTT 话题映射配置
MQTT_TOPIC_PREFIX = "home"
DEVICE_TOPICS = {
    "light": "light",
    "ac": "ac",
    "tv": "tv",
    "speaker": "speaker",
    "lock": "lock",
    "vacuum": "vacuum",
    "purifier": "air_purifier",  # 注意：这里映射为 air_purifier
    "fan": "fan",
    "plug": "plug",
    "switch": "switch",
}

# 设备配置
DEVICE_ACTIONS = {
    "light": ["on", "off", "brightness"],
    "ac": ["on", "off", "temperature"],
    "tv": ["on", "off", "volume"],
    "speaker": ["on", "off", "play", "volume"],
    "lock": ["unlock", "lock", "password"],
    "vacuum": ["on", "off", "mode"],
    "purifier": ["on", "off", "speed"],
    "fan": ["on", "off", "speed", "oscillate"],
    "plug": ["on", "off"],
    "switch": ["on", "off"],
}

VALUE_REQUIRED_ACTIONS = ["brightness", "temperature", "volume", "password", "mode", "speed", "oscillate"]

VALUE_RANGES = {
    "brightness": (0, 100, "亮度"),
    "temperature": (16, 30, "温度"),
    "volume": (0, 100, "音量"),
    "mode": (1, 3, "模式"),
    "oscillate": (0, 1, "摇头"),
}

DEVICE_VALUE_RANGES = {
    ("fan", "speed"): (1, 3, "风速"),
    ("purifier", "speed"): (1, 5, "风速"),
}

# MQTT 客户端
mqtt_client = None


def on_connect(client, userdata, flags, rc):
    """MQTT 连接回调"""
    if rc == 0:
        print(f"✓ MQTT 已连接到 {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"✗ MQTT 连接失败，返回码: {rc}")


def on_publish(client, userdata, mid):
    """MQTT 发布回调"""
    print(f"✓ MQTT 消息已发布 (消息ID: {mid})")


def init_mqtt():
    """初始化 MQTT 客户端"""
    global mqtt_client

    mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish

    # 设置用户名密码（如果配置了）
    if MQTT_USERNAME and MQTT_PASSWORD:
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # 连接到 MQTT Broker
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        return True
    except Exception as e:
        print(f"✗ MQTT 连接失败: {e}")
        return False


def get_mqtt_topic(device: str, action: str) -> str:
    """
    获取 MQTT 话题名称

    格式: {MQTT_TOPIC_PREFIX}/{设备类型}/{动作}
    例如: home/air_purifier/set
    """
    device_topic = DEVICE_TOPICS.get(device, device)
    return f"{MQTT_TOPIC_PREFIX}/{device_topic}/set"


def build_mqtt_payload(device: str, action: str, value) -> Dict[str, Any]:
    """
    构建 MQTT 消息的 Payload

    示例:
    {
        "action": "on",
        "value": null,
        "device": "purifier",
        "timestamp": 1713456789
    }
    """
    import time

    payload = {
        "action": action,
        "device": device,
        "timestamp": int(time.time())
    }

    if value is not None:
        payload["value"] = value

    return payload


def publish_mqtt_message(topic: str, payload: Dict[str, Any]) -> bool:
    """发布 MQTT 消息"""
    global mqtt_client

    if mqtt_client is None:
        print("✗ MQTT 客户端未初始化")
        return False

    try:
        mqtt_client.publish(topic, json.dumps(payload), qos=1, retain=False)
        return True
    except Exception as e:
        print(f"✗ MQTT 发布失败: {e}")
        return False


def validate_request(device: str, action: str, value) -> tuple[bool, str, str]:
    """验证请求参数"""
    if action not in DEVICE_ACTIONS.get(device, []):
        return False, "INVALID_ACTION", f"设备 '{device}' 不支持动作 '{action}'"

    if action == "password":
        if value is None:
            return False, "MISSING_VALUE", "修改密码需要提供新密码"
        pwd = str(value)
        if not pwd.isdigit() or len(pwd) < 4 or len(pwd) > 8:
            return False, "INVALID_VALUE", "密码必须为4-8位数字"
        return True, "", ""

    if action in VALUE_REQUIRED_ACTIONS:
        if value is None:
            return False, "MISSING_VALUE", f"动作 '{action}' 需要提供数值参数"
        range_key = (device, action)
        if range_key in DEVICE_VALUE_RANGES:
            min_val, max_val, name = DEVICE_VALUE_RANGES[range_key]
        elif action in VALUE_RANGES:
            min_val, max_val, name = VALUE_RANGES[action]
        else:
            return True, "", ""
        if not (min_val <= value <= max_val):
            return False, "INVALID_VALUE", f"{name}值必须在 {min_val} 到 {max_val} 之间"

    return True, "", ""


def create_response(device: str, action: str, value: Optional[int],
                    status: str = "ok", message: str = "", mqtt_topic: str = None, mqtt_payload: str = None) -> Dict[str, Any]:
    """创建标准响应"""
    response = {
        "status": status,
        "device": device,
        "action": action,
        "value": value,
    }
    if message:
        response["message"] = message
    if mqtt_topic:
        response["mqtt_topic"] = mqtt_topic
        response["mqtt_payload"] = mqtt_payload
    return response


def create_error_response(error_code: str, message: str, status_code: int = 400) -> tuple:
    """创建错误响应"""
    return jsonify({
        "status": "error",
        "error_code": error_code,
        "message": message
    }), status_code


# 路由处理
@app.route('/light', methods=['POST'])
def control_light():
    return handle_device_request("light")

@app.route('/ac', methods=['POST'])
def control_ac():
    return handle_device_request("ac")

@app.route('/tv', methods=['POST'])
def control_tv():
    return handle_device_request("tv")

@app.route('/speaker', methods=['POST'])
def control_speaker():
    return handle_device_request("speaker")

@app.route('/lock', methods=['POST'])
def control_lock():
    return handle_device_request("lock")

@app.route('/vacuum', methods=['POST'])
def control_vacuum():
    return handle_device_request("vacuum")

@app.route('/purifier', methods=['POST'])
def control_purifier():
    return handle_device_request("purifier")

@app.route('/fan', methods=['POST'])
def control_fan():
    return handle_device_request("fan")

@app.route('/plug', methods=['POST'])
def control_plug():
    return handle_device_request("plug")

@app.route('/switch', methods=['POST'])
def control_switch():
    return handle_device_request("switch")


def handle_device_request(device: str):
    """通用设备请求处理"""
    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)
    except Exception:
        return create_error_response("INVALID_REQUEST", "无法解析JSON请求体", 400)

    action = data.get("action")
    value = data.get("value")

    if not action:
        return create_error_response("INVALID_ACTION", "缺少 'action' 参数", 400)

    is_valid, error_code, error_msg = validate_request(device, action, value)
    if not is_valid:
        status_code = 400 if error_code in ["INVALID_ACTION", "INVALID_VALUE", "MISSING_VALUE"] else 500
        return create_error_response(error_code, error_msg, status_code)

    try:
        # 构建 MQTT 话题和 Payload
        mqtt_topic = get_mqtt_topic(device, action)
        mqtt_payload_dict = build_mqtt_payload(device, action, value)
        mqtt_payload_str = json.dumps(mqtt_payload_dict, ensure_ascii=False)

        # 发布 MQTT 消息
        mqtt_published = publish_mqtt_message(mqtt_topic, mqtt_payload_dict)

        action_messages = {
            "on": f"{device} 已开启",
            "off": f"{device} 已关闭",
            "brightness": f"亮度已设置为 {value}%",
            "temperature": f"温度已设置为 {value}°C",
            "volume": f"音量已设置为 {value}",
            "play": "开始播放",
            "unlock": "门锁已打开",
            "lock": "门锁已锁定",
            "password": "门锁密码已修改",
            "mode": f"扫地机器人模式已设置",
            "speed": f"风速已设置为 {value}档",
            "oscillate": f"摇头已{'开启' if value else '关闭'}",
        }

        response = create_response(
            device=device,
            action=action,
            value=value,
            message=action_messages.get(action, "操作成功"),
            mqtt_topic=mqtt_topic,
            mqtt_payload=mqtt_payload_str
        )

        if not mqtt_published:
            response["warning"] = "MQTT 消息发布失败，但请求已处理"

        return jsonify(response), 200

    except Exception as e:
        return create_error_response("DEVICE_ERROR", f"设备控制失败: {str(e)}", 500)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "home-control-server-mqtt",
        "mqtt_connected": mqtt_client is not None and mqtt_client.is_connected(),
        "devices": list(DEVICE_ACTIONS.keys())
    }), 200


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Home Control Server (MQTT Version)",
        "version": "2.0.0-mqtt",
        "mqtt_broker": f"{MQTT_BROKER}:{MQTT_PORT}",
        "endpoints": {
            "/light": "灯光控制 (on/off/brightness)",
            "/ac": "空调控制 (on/off/temperature)",
            "/tv": "电视控制 (on/off/volume)",
            "/speaker": "音箱控制 (on/off/play/volume)",
            "/lock": "智能门锁控制 (unlock/lock/password)",
            "/vacuum": "扫地机器人控制 (on/off/mode)",
            "/purifier": "空气净化器控制 (on/off/speed)",
            "/fan": "风扇控制 (on/off/speed/oscillate)",
            "/plug": "智能插座控制 (on/off)",
            "/switch": "智能开关控制 (on/off)",
            "/health": "健康检查"
        }
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("家居控制服务端 (MQTT 版本) 启动中...")
    print(f"HTTP 监听: http://127.0.0.1:22222")
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print("=" * 60)

    # 初始化 MQTT
    if not init_mqtt():
        print("⚠️  警告: MQTT 连接失败，服务器将以 HTTP-only 模式运行")

    app.run(host='127.0.0.1', port=22222, debug=False)
