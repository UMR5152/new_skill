#!/usr/bin/env python3
"""
家居控制服务端示例（扩展版）
监听 127.0.0.1:22222，处理家居设备控制请求

使用方法:
    python home_server_extended.py

依赖:
    pip install flask
"""

from flask import Flask, request, jsonify
from typing import Optional, Dict, Any, List
from datetime import datetime, time
import threading

app = Flask(__name__)

# ============================================================================
# 设备配置
# ============================================================================

# 所有支持的设备和动作
DEVICE_ACTIONS = {
    # 现有设备
    "light": ["on", "off", "brightness", "color", "scene"],
    "ac": ["on", "off", "temperature", "mode", "preset", "fanspeed"],
    "tv": ["on", "off", "volume", "source", "status"],
    "speaker": ["on", "off", "play", "volume"],
    "lock": ["unlock", "lock", "password"],
    "vacuum": ["on", "off", "mode", "pause", "dock", "locate"],
    "purifier": ["on", "off", "speed", "ion", "uv"],
    "fan": ["on", "off", "speed", "oscillate", "oscillate_angle", "fan_mode"],
    "plug": ["on", "off"],
    "switch": ["on", "off"],
    # 新增设备
    "curtain": ["on", "off", "pause", "position", "schedule"],
    "humidifier": ["on", "off", "mode", "humidity", "filter_level"],
    # 通用功能
    "device_list": ["get"],
    "device_add": ["add"],
}

# 需要数值参数的动作
VALUE_REQUIRED_ACTIONS = [
    "brightness", "temperature", "volume", "password", "mode", "speed", "oscillate",
    "oscillate_angle", "position", "humidity", "filter_level", "fanspeed"
]

# 数值范围定义
VALUE_RANGES = {
    "brightness": (0, 100, "亮度"),
    "temperature": (16, 30, "温度"),
    "volume": (0, 100, "音量"),
    "mode": (1, 3, "模式"),
    "oscillate": (0, 1, "摇头"),
    "oscillate_angle": (30, 90, "摇头角度"),
    "position": (0, 100, "位置"),
    "humidity": (30, 90, "湿度"),
    "filter_level": (1, 5, "过滤等级"),
}

# 按设备区分的数值范围（优先级高于 VALUE_RANGES）
DEVICE_VALUE_RANGES = {
    ("fan", "speed"): (1, 3, "风速"),
    ("purifier", "speed"): (1, 5, "风速"),
    ("ac", "fanspeed"): (1, 4, "空调风速"),
}

# 字符串值的有效选项
STRING_VALUE_OPTIONS = {
    # 灯光色彩
    ("light", "color"): ["warm", "cool", "natural", "暖光", "白光", "自然光"],
    # 灯光场景
    ("light", "scene"): ["cozy", "reading", "romantic", "温馨", "阅读", "浪漫"],
    # 空调模式
    ("ac", "mode"): ["cool", "heat", "dehumidify", "fan", "auto", "制冷", "制热", "除湿", "送风", "自动"],
    # 空调预设
    ("ac", "preset"): ["sleep", "silent", "eco", "睡眠", "静音", "节能"],
    # 风扇模式
    ("fan", "fan_mode"): ["natural", "sleep", "smart", "normal", "自然风", "睡眠风", "智能风", "正常风"],
    # 电视信号源
    ("tv", "source"): ["HDMI1", "HDMI2", "AV", "TV", "USB"],
    # 加湿器模式
    ("humidifier", "mode"): ["strong", "sleep", "auto", "强劲", "睡眠", "自动"],
}

# 模拟设备状态
device_states = {
    "light": {
        "power": False, "brightness": 50, "color": "warm", "scene": "cozy"
    },
    "ac": {
        "power": False, "temperature": 24, "mode": "cool", "preset": None, "fanspeed": 2
    },
    "tv": {
        "power": False, "volume": 30, "source": "HDMI1", "channel": 1
    },
    "speaker": {
        "power": False, "playing": False, "volume": 20, "current_track": None
    },
    "lock": {
        "locked": True, "password": "123456", "battery": 85
    },
    "vacuum": {
        "power": False, "mode": 1, "battery": 80, "location": "充电座",
        "cleaning": False, "paused": False
    },
    "purifier": {
        "power": False, "speed": 1, "ion": False, "uv": False, "pm25": 35
    },
    "fan": {
        "power": False, "speed": 1, "oscillating": False,
        "oscillate_angle": 90, "fan_mode": "normal"
    },
    "plug": {
        "power": False, "power_consumption": 0
    },
    "switch": {
        "power": False
    },
    "curtain": {
        "power": False, "position": 0, "moving": False, "scheduled": False
    },
    "humidifier": {
        "power": False, "mode": "auto", "humidity": 50, "filter_level": 3,
        "water_level": 80, "current_humidity": 45
    },
}

# 设备列表（模拟数据库）
registered_devices = [
    {"id": "light_001", "name": "客厅灯", "type": "light", "room": "客厅", "status": "online"},
    {"id": "light_002", "name": "卧室灯", "type": "light", "room": "卧室", "status": "online"},
    {"id": "ac_001", "name": "客厅空调", "type": "ac", "room": "客厅", "status": "online"},
    {"id": "tv_001", "name": "客厅电视", "type": "tv", "room": "客厅", "status": "online"},
    {"id": "speaker_001", "name": "客厅音箱", "type": "speaker", "room": "客厅", "status": "online"},
    {"id": "lock_001", "name": "大门门锁", "type": "lock", "room": "玄关", "status": "online"},
    {"id": "vacuum_001", "name": "扫地机器人", "type": "vacuum", "room": "全屋", "status": "online"},
    {"id": "purifier_001", "name": "空气净化器", "type": "purifier", "room": "客厅", "status": "online"},
    {"id": "fan_001", "name": "客厅风扇", "type": "fan", "room": "客厅", "status": "online"},
    {"id": "curtain_001", "name": "客厅窗帘", "type": "curtain", "room": "客厅", "status": "online"},
    {"id": "humidifier_001", "name": "卧室加湿器", "type": "humidifier", "room": "卧室", "status": "online"},
]

# 自动化任务列表（模拟）
automation_tasks = []


# ============================================================================
# 工具函数
# ============================================================================

def validate_request(device: str, action: str, value) -> tuple:
    """
    验证请求参数
    返回: (是否有效, 错误代码, 错误消息)
    """
    # 验证动作是否支持
    if action not in DEVICE_ACTIONS.get(device, []):
        return False, "INVALID_ACTION", f"设备 '{device}' 不支持动作 '{action}'"

    # 密码特殊验证（字符串类型）
    if action == "password":
        if value is None:
            return False, "MISSING_VALUE", "修改密码需要提供新密码"
        pwd = str(value)
        if not pwd.isdigit() or len(pwd) < 4 or len(pwd) > 8:
            return False, "INVALID_VALUE", "密码必须为4-8位数字"
        return True, "", ""

    # 验证字符串值选项
    range_key = (device, action)
    if range_key in STRING_VALUE_OPTIONS:
        valid_options = STRING_VALUE_OPTIONS[range_key]
        if value is None:
            return False, "MISSING_VALUE", f"动作 '{action}' 需要提供参数"
        value_str = str(value).lower()
        # 支持中英文
        for opt in valid_options:
            if opt.lower() == value_str:
                return True, "", ""
        return False, "INVALID_VALUE", f"'{value}' 不是有效的选项，有效值: {', '.join(valid_options)}"

    # 验证数值参数
    if action in VALUE_REQUIRED_ACTIONS:
        if value is None:
            return False, "MISSING_VALUE", f"动作 '{action}' 需要提供数值参数"
        # 优先使用按设备区分的范围
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
    """
    执行设备控制动作
    实际应用中，这里应该调用真实的硬件控制接口
    """
    state = device_states[device]

    # 灯光控制
    if device == "light":
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False
        elif action == "brightness":
            state["brightness"] = value
        elif action == "color":
            state["color"] = value
        elif action == "scene":
            state["scene"] = value

    # 空调控制
    elif device == "ac":
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False
        elif action == "temperature":
            state["temperature"] = value
        elif action == "mode":
            state["mode"] = value
        elif action == "preset":
            state["preset"] = value
        elif action == "fanspeed":
            state["fanspeed"] = value

    # 电视控制
    elif device == "tv":
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False
        elif action == "volume":
            state["volume"] = value
        elif action == "source":
            state["source"] = value
        elif action == "status":
            pass  # 只返回状态

    # 音箱控制
    elif device == "speaker":
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False
            state["playing"] = False
        elif action == "play":
            state["playing"] = True
        elif action == "volume":
            state["volume"] = value

    # 门锁控制
    elif device == "lock":
        if action == "unlock":
            state["locked"] = False
        elif action == "lock":
            state["locked"] = True
        elif action == "password":
            state["password"] = str(value)

    # 扫地机器人控制
    elif device == "vacuum":
        if action == "on":
            state["power"] = True
            state["cleaning"] = True
            state["paused"] = False
        elif action == "off":
            state["power"] = False
            state["cleaning"] = False
            state["paused"] = False
        elif action == "mode":
            state["mode"] = value
        elif action == "pause":
            state["paused"] = True
            state["cleaning"] = False
        elif action == "dock":
            state["cleaning"] = False
            state["paused"] = False
            state["location"] = "充电座"
        elif action == "locate":
            pass  # 只返回位置

    # 空气净化器控制
    elif device == "purifier":
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False
        elif action == "speed":
            state["speed"] = value
        elif action == "ion":
            state["ion"] = bool(value)
        elif action == "uv":
            state["uv"] = bool(value)

    # 风扇控制
    elif device == "fan":
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False
        elif action == "speed":
            state["speed"] = value
        elif action == "oscillate":
            state["oscillating"] = bool(value)
        elif action == "oscillate_angle":
            state["oscillate_angle"] = value
        elif action == "fan_mode":
            state["fan_mode"] = value

    # 智能插座/开关
    elif device in ["plug", "switch"]:
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False

    # 窗帘控制
    elif device == "curtain":
        if action == "on":
            state["power"] = True
            state["position"] = 100
        elif action == "off":
            state["power"] = True
            state["position"] = 0
        elif action == "pause":
            state["moving"] = False
        elif action == "position":
            state["position"] = value
            state["power"] = True
        elif action == "schedule":
            state["scheduled"] = bool(value)

    # 加湿器控制
    elif device == "humidifier":
        if action == "on":
            state["power"] = True
        elif action == "off":
            state["power"] = False
        elif action == "mode":
            state["mode"] = value
        elif action == "humidity":
            state["humidity"] = value
        elif action == "filter_level":
            state["filter_level"] = value

    # 打印硬件调用日志
    print(f"  >>> [硬件] {device} {action}: {value if value is not None else ''}")

    return state.copy()


def create_error_response(error_code: str, message: str, status_code: int = 400):
    """创建错误响应"""
    return jsonify({
        "status": "error",
        "error_code": error_code,
        "message": message
    }), status_code


def get_action_message(device: str, action: str, value) -> str:
    """生成操作成功消息"""
    messages = {
        "light": {
            "on": "灯光已开启", "off": "灯光已关闭",
            "brightness": f"亮度已设置为 {value}%",
            "color": f"色彩已切换为 {value}",
            "scene": f"场景已切换为 {value}",
        },
        "ac": {
            "on": "空调已开启", "off": "空调已关闭",
            "temperature": f"温度已设置为 {value}°C",
            "mode": f"空调模式已切换为 {value}",
            "preset": f"预设模式已切换为 {value}",
            "fanspeed": f"风速已设置为 {value}档",
        },
        "tv": {
            "on": "电视已开启", "off": "电视已关闭",
            "volume": f"音量已设置为 {value}",
            "source": f"信号源已切换为 {value}",
            "status": "电视状态查询成功",
        },
        "speaker": {
            "on": "音箱已开启", "off": "音箱已关闭",
            "play": "开始播放", "volume": f"音量已设置为 {value}",
        },
        "lock": {
            "unlock": "门锁已打开", "lock": "门锁已锁定",
            "password": "门锁密码已修改",
        },
        "vacuum": {
            "on": "扫地机器人开始清扫", "off": "扫地机器人已停止",
            "mode": f"清扫模式已设置",
            "pause": "清扫已暂停", "dock": "返回充电座",
            "locate": "位置查询成功",
        },
        "purifier": {
            "on": "空气净化器已开启", "off": "空气净化器已关闭",
            "speed": f"风速已设置为 {value}档",
            "ion": f"负离子功能已{'开启' if value else '关闭'}",
            "uv": f"UV灯已{'开启' if value else '关闭'}",
        },
        "fan": {
            "on": "风扇已开启", "off": "风扇已关闭",
            "speed": f"风速已设置为 {value}档",
            "oscillate": f"摇头已{'开启' if value else '关闭'}",
            "oscillate_angle": f"摇头角度已设置为 {value}°",
            "fan_mode": f"风扇模式已切换为 {value}",
        },
        "plug": {"on": "智能插座已开启", "off": "智能插座已关闭"},
        "switch": {"on": "智能开关已开启", "off": "智能开关已关闭"},
        "curtain": {
            "on": "窗帘已打开", "off": "窗帘已关闭",
            "pause": "窗帘运动已暂停",
            "position": f"窗帘位置已设置为 {value}%",
            "schedule": f"定时任务已{'开启' if value else '关闭'}",
        },
        "humidifier": {
            "on": "加湿器已开启", "off": "加湿器已关闭",
            "mode": f"模式已切换为 {value}",
            "humidity": f"目标湿度已设置为 {value}%",
            "filter_level": f"过滤等级已设置为 {value}级",
        },
    }
    return messages.get(device, {}).get(action, "操作成功")


# ============================================================================
# 路由处理 - 现有设备
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


@app.route('/lock', methods=['POST'])
def control_lock():
    """智能门锁控制"""
    return handle_device_request("lock")


@app.route('/vacuum', methods=['POST'])
def control_vacuum():
    """扫地机器人控制"""
    return handle_device_request("vacuum")


@app.route('/purifier', methods=['POST'])
def control_purifier():
    """空气净化器控制"""
    return handle_device_request("purifier")


@app.route('/fan', methods=['POST'])
def control_fan():
    """风扇控制"""
    return handle_device_request("fan")


@app.route('/plug', methods=['POST'])
def control_plug():
    """智能插座控制"""
    return handle_device_request("plug")


@app.route('/switch', methods=['POST'])
def control_switch():
    """智能开关控制"""
    return handle_device_request("switch")


# ============================================================================
# 路由处理 - 新增设备
# ============================================================================

@app.route('/curtain', methods=['POST'])
def control_curtain():
    """窗帘控制"""
    return handle_device_request("curtain")


@app.route('/humidifier', methods=['POST'])
def control_humidifier():
    """加湿器控制"""
    return handle_device_request("humidifier")


# ============================================================================
# 路由处理 - 通用功能
# ============================================================================

@app.route('/device_list', methods=['GET', 'POST'])
def get_device_list():
    """获取设备列表"""
    return jsonify({
        "status": "ok",
        "devices": registered_devices,
        "total": len(registered_devices)
    }), 200


@app.route('/device_add', methods=['POST'])
def add_device():
    """添加设备"""
    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)

        device_type = data.get("type")
        device_name = data.get("name")
        room = data.get("room", "未分类")

        if not device_type or not device_name:
            return create_error_response("MISSING_PARAMS", "缺少必要参数: type 和 name", 400)

        if device_type not in DEVICE_ACTIONS:
            return create_error_response("INVALID_DEVICE_TYPE", f"不支持的设备类型: {device_type}", 400)

        # 创建新设备
        new_device = {
            "id": f"{device_type}_{len(registered_devices) + 1:03d}",
            "name": device_name,
            "type": device_type,
            "room": room,
            "status": "online"
        }
        registered_devices.append(new_device)

        print(f"  >>> [系统] 新增设备: {new_device}")

        return jsonify({
            "status": "ok",
            "message": f"设备 '{device_name}' 添加成功",
            "device": new_device
        }), 200

    except Exception as e:
        return create_error_response("DEVICE_ERROR", f"添加设备失败: {str(e)}", 500)


# ============================================================================
# 通用设备请求处理
# ============================================================================

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

        response = {
            "status": "ok",
            "device": device,
            "action": action,
            "value": value,
            "message": get_action_message(device, action, value),
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
        "version": "3.0.0",
        "devices": list(DEVICE_ACTIONS.keys())
    }), 200


@app.route('/', methods=['GET'])
def index():
    """根路径信息"""
    return jsonify({
        "service": "Home Control Server (Extended)",
        "version": "3.0.0",
        "endpoints": {
            "/light": "灯光控制 (on/off/brightness/color/scene)",
            "/ac": "空调控制 (on/off/temperature/mode/preset/fanspeed)",
            "/tv": "电视控制 (on/off/volume/source/status)",
            "/speaker": "音箱控制 (on/off/play/volume)",
            "/lock": "智能门锁控制 (unlock/lock/password)",
            "/vacuum": "扫地机器人控制 (on/off/mode/pause/dock/locate)",
            "/purifier": "空气净化器控制 (on/off/speed/ion/uv)",
            "/fan": "风扇控制 (on/off/speed/oscillate/oscillate_angle/fan_mode)",
            "/plug": "智能插座控制 (on/off)",
            "/switch": "智能开关控制 (on/off)",
            "/curtain": "窗帘控制 (on/off/pause/position/schedule)",
            "/humidifier": "加湿器控制 (on/off/mode/humidity/filter_level)",
            "/device_list": "获取设备列表 (GET/POST)",
            "/device_add": "添加设备 (POST)",
            "/health": "健康检查"
        }
    }), 200


# ============================================================================
# 启动服务
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("        家居控制服务端 (扩展版 v3.0.0)")
    print("=" * 60)
    print(f"  监听地址: http://127.0.0.1:22222")
    print(f"  支持设备: {', '.join(DEVICE_ACTIONS.keys())}")
    print("=" * 60)
    print("  测试命令示例:")
    print("    # 灯光控制")
    print("    curl -X POST http://127.0.0.1:22222/light \\")
    print("      -H 'Content-Type: application/json' \\")
    print("      -d '{\"action\": \"color\", \"value\": \"warm\"}'")
    print()
    print("    # 空调控制")
    print("    curl -X POST http://127.0.0.1:22222/ac \\")
    print("      -H 'Content-Type: application/json' \\")
    print("      -d '{\"action\": \"preset\", \"value\": \"sleep\"}'")
    print()
    print("    # 获取设备列表")
    print("    curl http://127.0.0.1:22222/device_list")
    print("=" * 60)
    print()

    app.run(host='127.0.0.1', port=22222, debug=True)
