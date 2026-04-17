#!/usr/bin/env python3
"""
家居控制服务端
监听 127.0.0.1:22222，处理家居设备控制请求
"""

from flask import Flask, request, jsonify
from typing import Optional, Dict, Any
import sys
import logging
from datetime import datetime

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/home_control.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 设备配置
DEVICE_ACTIONS = {
    "light": ["on", "off", "brightness"],
    "ac": ["on", "off", "temperature", "cool", "heat", "dehumidify", "fan", "auto"],
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

# 模拟设备状态
device_states = {
    "light": {"power": False, "brightness": 50},
    "ac": {"power": False, "temperature": 24, "mode": "cool"},
    "tv": {"power": False, "volume": 30},
    "speaker": {"power": False, "playing": False, "volume": 20},
    "lock": {"locked": True, "password": "123456"},
    "vacuum": {"power": False, "mode": 1, "battery": 80},
    "purifier": {"power": False, "speed": 1, "pm25": 35},
    "fan": {"power": False, "speed": 1, "oscillating": False},
    "plug": {"power": False},
    "switch": {"power": False},
}


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


def execute_device_action(device: str, action: str, value) -> Dict[str, Any]:
    """执行设备控制动作"""
    state = device_states[device]

    if action == "on":
        state["power"] = True
    elif action == "off":
        state["power"] = False
        if device == "speaker":
            state["playing"] = False
    elif action == "brightness":
        state["brightness"] = value
    elif action == "temperature":
        state["temperature"] = value
    elif action == "volume":
        state["volume"] = value
    elif action == "play":
        state["playing"] = True
    elif action == "unlock":
        state["locked"] = False
    elif action == "lock":
        state["locked"] = True
    elif action == "password":
        old_password = state["password"]
        new_password = str(value)
        state["password"] = new_password
        # 记录密码修改日志（包含明文）
        logger.info(f"门锁密码修改: 旧密码='{old_password}' -> 新密码='{new_password}'")
    elif action == "mode":
        state["mode"] = value
    elif action == "speed":
        state["speed"] = value
    elif action == "oscillate":
        state["oscillating"] = bool(value)
    # AC mode actions
    elif action in ["cool", "heat", "dehumidify", "fan", "auto"]:
        if device == "ac":
            state["mode"] = action
            state["power"] = True  # 自动开启空调

    return state.copy()


def create_response(device: str, action: str, value: Optional[int],
                    status: str = "ok", message: str = "") -> Dict[str, Any]:
    """创建标准响应"""
    response = {
        "status": status,
        "device": device,
        "action": action,
        "value": value,
    }
    if message:
        response["message"] = message
    return response


def create_error_response(error_code: str, message: str,
                          status_code: int = 400) -> tuple:
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
        new_state = execute_device_action(device, action, value)

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
            # AC mode messages
            "cool": "空调已切换到制冷模式",
            "heat": "空调已切换到制热模式",
            "dehumidify": "空调已切换到除湿模式",
            "fan": "空调已切换到送风模式",
            "auto": "空调已切换到自动模式",
        }

        response = create_response(
            device=device,
            action=action,
            value=value,
            message=action_messages.get(action, "操作成功")
        )
        response["state"] = new_state

        return jsonify(response), 200

    except Exception as e:
        return create_error_response("DEVICE_ERROR", f"设备控制失败: {str(e)}", 500)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "home-control-server",
        "devices": list(DEVICE_ACTIONS.keys())
    }), 200


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Home Control Server",
        "version": "1.0.0",
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
    print("=" * 50)
    print("家居控制服务端启动中...")
    print(f"监听地址: http://127.0.0.1:22222")
    print("=" * 50)
    app.run(host='127.0.0.1', port=22222, debug=False)
