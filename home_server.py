#!/usr/bin/env python3
"""
家居控制服务端示例
监听 127.0.0.1:22222，处理家居设备控制请求

使用方法:
    python home_server.py

依赖:
    pip install flask
"""

from flask import Flask, request, jsonify
from typing import Optional, Dict, Any

app = Flask(__name__)

# ============================================================================
# 设备配置
# ============================================================================

DEVICE_ACTIONS = {
    "light": ["on", "off", "brightness"],
    "ac": ["on", "off", "temperature"],
    "tv": ["on", "off", "volume"],
    "speaker": ["on", "off", "play", "volume"],
}

VALUE_REQUIRED_ACTIONS = ["brightness", "temperature", "volume"]

VALUE_RANGES = {
    "brightness": (0, 100, "亮度"),
    "temperature": (16, 30, "温度"),
    "volume": (0, 100, "音量"),
}

# 模拟设备状态（实际应用中应从硬件读取）
device_states = {
    "light": {"power": False, "brightness": 50},
    "ac": {"power": False, "temperature": 24},
    "tv": {"power": False, "volume": 30},
    "speaker": {"power": False, "playing": False, "volume": 20},
}


# ============================================================================
# 工具函数
# ============================================================================

def validate_request(device: str, action: str, value: Optional[int]) -> tuple:
    """
    验证请求参数
    返回: (是否有效, 错误代码, 错误消息)
    """
    # 验证动作是否支持
    if action not in DEVICE_ACTIONS.get(device, []):
        return False, "INVALID_ACTION", f"设备 '{device}' 不支持动作 '{action}'"

    # 验证数值参数
    if action in VALUE_REQUIRED_ACTIONS:
        if value is None:
            return False, "MISSING_VALUE", f"动作 '{action}' 需要提供数值参数"
        min_val, max_val, name = VALUE_RANGES[action]
        if not (min_val <= value <= max_val):
            return False, "INVALID_VALUE", f"{name}值必须在 {min_val} 到 {max_val} 之间"

    return True, "", ""


def execute_device_action(device: str, action: str, value: Optional[int]) -> Dict[str, Any]:
    """
    执行设备控制动作
    实际应用中，这里应该调用真实的硬件控制接口
    """
    state = device_states[device]

    if action == "on":
        state["power"] = True
        print(f"  >>> [硬件] {device} 电源: ON")
    elif action == "off":
        state["power"] = False
        print(f"  >>> [硬件] {device} 电源: OFF")
        if device == "speaker":
            state["playing"] = False
    elif action == "brightness":
        state["brightness"] = value
        print(f"  >>> [硬件] {device} 亮度设置为: {value}%")
    elif action == "temperature":
        state["temperature"] = value
        print(f"  >>> [硬件] {device} 温度设置为: {value}°C")
    elif action == "volume":
        state["volume"] = value
        print(f"  >>> [硬件] {device} 音量设置为: {value}")
    elif action == "play":
        state["playing"] = True
        print(f"  >>> [硬件] {device} 开始播放")

    return state.copy()


def create_error_response(error_code: str, message: str, status_code: int = 400):
    """创建错误响应"""
    return jsonify({
        "status": "error",
        "error_code": error_code,
        "message": message
    }), status_code


# ============================================================================
# 路由处理
# ============================================================================

@app.route('/light', methods=['POST'])
def control_light():
    """灯光控制"""
    return handle_device_request("light")


@app.route('/ac', methods=['POST'])
def control_ac():
    """空调控制"""
    return handle_device_request("ac")


@app.route('/tv', methods=['POST'])
def control_tv():
    """电视控制"""
    return handle_device_request("tv")


@app.route('/speaker', methods=['POST'])
def control_speaker():
    """音箱控制"""
    return handle_device_request("speaker")


def handle_device_request(device: str):
    """通用设备请求处理"""
    print(f"\n[请求] 设备: {device}")

    # 解析请求
    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)
    except Exception as e:
        return create_error_response("INVALID_REQUEST", f"无法解析JSON请求体: {e}", 400)

    action = data.get("action")
    value = data.get("value")

    print(f"  >>> 动作: {action}, 值: {value}")

    # 验证action参数
    if not action:
        return create_error_response("INVALID_ACTION", "缺少 'action' 参数", 400)

    # 验证请求参数
    is_valid, error_code, error_msg = validate_request(device, action, value)
    if not is_valid:
        print(f"  >>> 验证失败: {error_msg}")
        status_code = 400 if error_code in ["INVALID_ACTION", "INVALID_VALUE", "MISSING_VALUE"] else 500
        return create_error_response(error_code, error_msg, status_code)

    # 执行设备控制
    try:
        new_state = execute_device_action(device, action, value)

        # 构建成功消息
        action_messages = {
            "on": f"{device} 已开启",
            "off": f"{device} 已关闭",
            "brightness": f"亮度已设置为 {value}%",
            "temperature": f"温度已设置为 {value}°C",
            "volume": f"音量已设置为 {value}",
            "play": "开始播放",
        }

        response = {
            "status": "ok",
            "device": device,
            "action": action,
            "value": value,
            "message": action_messages.get(action, "操作成功"),
            "state": new_state
        }

        print(f"  >>> 响应: {response}")
        return jsonify(response), 200

    except Exception as e:
        print(f"  >>> 执行失败: {e}")
        return create_error_response("DEVICE_ERROR", f"设备控制失败: {str(e)}", 500)


# ============================================================================
# 健康检查和服务信息
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "home-control-server",
        "devices": list(DEVICE_ACTIONS.keys())
    }), 200


@app.route('/', methods=['GET'])
def index():
    """根路径信息"""
    return jsonify({
        "service": "Home Control Server",
        "version": "1.0.0",
        "endpoints": {
            "/light": "灯光控制 (on/off/brightness)",
            "/ac": "空调控制 (on/off/temperature)",
            "/tv": "电视控制 (on/off/volume)",
            "/speaker": "音箱控制 (on/off/play/volume)",
            "/health": "健康检查"
        }
    }), 200


# ============================================================================
# 启动服务
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("        家居控制服务端")
    print("=" * 60)
    print(f"  监听地址: http://127.0.0.1:22222")
    print(f"  支持设备: light, ac, tv, speaker")
    print("=" * 60)
    print("  测试命令示例:")
    print("    curl -X POST http://127.0.0.1:22222/light \\")
    print("      -H 'Content-Type: application/json' \\")
    print("      -d '{\"action\": \"on\"}'")
    print("=" * 60)
    print()

    app.run(host='127.0.0.1', port=22222, debug=True)
