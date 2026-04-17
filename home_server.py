#!/usr/bin/env python3
"""
家居控制服务端 (扩展版 v3.0)
监听 127.0.0.1:22222，处理家居设备控制请求

支持设备:
  智能灯光、空调、电视、音箱、智能门锁、扫地机器人、
  空气净化器、风扇、智能插座、智能开关、窗帘、加湿器
  以及设备管理和家庭任务

使用方法:
    python home_server.py

依赖:
    pip install flask
"""

from flask import Flask, request, jsonify
from typing import Optional, Dict, Any, List

app = Flask(__name__)

# ============================================================================
# 设备配置
# ============================================================================

DEVICE_ACTIONS = {
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
    "curtain": ["on", "off", "pause", "position", "schedule"],
    "humidifier": ["on", "off", "mode", "humidity", "filter_level"],
}

# 数值型动作（需要 value 参数）
VALUE_REQUIRED_ACTIONS = [
    "brightness", "temperature", "volume", "password", "mode",
    "speed", "oscillate", "oscillate_angle", "position",
    "humidity", "filter_level", "fanspeed", "ion", "uv",
]

# 全局数值范围
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
    "fanspeed": (1, 4, "空调风速"),
    "ion": (0, 1, "负离子"),
    "uv": (0, 1, "UV灯"),
}

# 按设备区分的数值范围（优先级高于 VALUE_RANGES）
DEVICE_VALUE_RANGES = {
    ("fan", "speed"): (1, 3, "风速"),
    ("purifier", "speed"): (1, 5, "风速"),
    ("ac", "fanspeed"): (1, 4, "空调风速"),
}

# 字符串型动作（value 为预定义选项）
STRING_VALUE_OPTIONS = {
    ("light", "color"): (["warm", "cool", "natural", "暖光", "白光", "自然光"],
                          {"warm": "暖光", "cool": "白光", "natural": "自然光"}),
    ("light", "scene"): (["cozy", "reading", "romantic", "温馨", "阅读", "浪漫"],
                         {"cozy": "温馨", "reading": "阅读", "romantic": "浪漫"}),
    ("ac", "mode"): (["cool", "heat", "dehumidify", "fan", "auto", "制冷", "制热", "除湿", "送风", "自动"],
                     {"cool": "制冷", "heat": "制热", "dehumidify": "除湿", "fan": "送风", "auto": "自动"}),
    ("ac", "preset"): (["sleep", "silent", "eco", "睡眠", "静音", "节能"],
                       {"sleep": "睡眠", "silent": "静音", "eco": "节能"}),
    ("fan", "fan_mode"): (["natural", "sleep", "smart", "normal", "自然风", "睡眠风", "智能风", "正常风"],
                          {"natural": "自然风", "sleep": "睡眠风", "smart": "智能风", "normal": "正常风"}),
    ("tv", "source"): (["HDMI1", "HDMI2", "AV", "TV", "USB"], None),
    ("humidifier", "mode"): (["strong", "sleep", "auto", "强劲", "睡眠", "自动"],
                             {"strong": "强劲", "sleep": "睡眠", "auto": "自动"}),
}

# 无需 value 的动作
NO_VALUE_ACTIONS = [
    "on", "off", "play", "unlock", "lock", "pause", "dock", "locate", "status",
]

# ============================================================================
# 模拟设备状态
# ============================================================================

device_states = {
    "light": {"power": False, "brightness": 50, "color": "warm", "scene": "cozy"},
    "ac": {"power": False, "temperature": 24, "mode": "cool", "preset": None, "fanspeed": 2},
    "tv": {"power": False, "volume": 30, "source": "HDMI1", "channel": "CCTV-1"},
    "speaker": {"power": False, "playing": False, "volume": 20},
    "lock": {"locked": True, "password": "123456"},
    "vacuum": {"power": False, "mode": 1, "battery": 80, "paused": False,
               "location": "充电座", "cleaning": False},
    "purifier": {"power": False, "speed": 1, "pm25": 35, "ion": False, "uv": False},
    "fan": {"power": False, "speed": 1, "oscillating": False,
            "oscillate_angle": 60, "fan_mode": "normal"},
    "plug": {"power": False},
    "switch": {"power": False},
    "curtain": {"power": False, "position": 100, "moving": False, "scheduled": False},
    "humidifier": {"power": False, "mode": "auto", "humidity": 50,
                   "filter_level": 3, "current_humidity": 45},
}

# ============================================================================
# 设备注册表（设备管理）
# ============================================================================

device_registry: List[Dict[str, str]] = [
    {"id": "light_001", "name": "客厅灯", "type": "light", "room": "客厅", "status": "online"},
    {"id": "ac_001", "name": "客厅空调", "type": "ac", "room": "客厅", "status": "online"},
    {"id": "tv_001", "name": "客厅电视", "type": "tv", "room": "客厅", "status": "online"},
    {"id": "speaker_001", "name": "客厅音箱", "type": "speaker", "room": "客厅", "status": "online"},
    {"id": "lock_001", "name": "大门门锁", "type": "lock", "room": "入户", "status": "online"},
    {"id": "vacuum_001", "name": "扫地机器人", "type": "vacuum", "room": "全屋", "status": "online"},
    {"id": "purifier_001", "name": "空气净化器", "type": "purifier", "room": "卧室", "status": "online"},
    {"id": "fan_001", "name": "卧室风扇", "type": "fan", "room": "卧室", "status": "online"},
    {"id": "plug_001", "name": "智能插座", "type": "plug", "room": "书房", "status": "online"},
    {"id": "switch_001", "name": "智能开关1", "type": "switch", "room": "客厅", "status": "online"},
    {"id": "switch_002", "name": "智能开关2", "type": "switch", "room": "卧室", "status": "online"},
    {"id": "curtain_001", "name": "客厅窗帘", "type": "curtain", "room": "客厅", "status": "online"},
    {"id": "curtain_002", "name": "卧室窗帘", "type": "curtain", "room": "卧室", "status": "online"},
    {"id": "humidifier_001", "name": "卧室加湿器", "type": "humidifier", "room": "卧室", "status": "online"},
]

_device_counter = len(device_registry)


# ============================================================================
# 工具函数
# ============================================================================

def create_error_response(error_code: str, message: str, status_code: int = 400):
    """创建错误响应"""
    return jsonify({
        "status": "error",
        "error_code": error_code,
        "message": message
    }), status_code


def validate_request(device: str, action: str, value) -> tuple:
    """
    验证请求参数
    返回: (是否有效, 错误代码, 错误消息)
    """
    # 验证动作是否支持
    if action not in DEVICE_ACTIONS.get(device, []):
        return False, "INVALID_ACTION", f"设备 '{device}' 不支持动作 '{action}'"

    # 密码修改特殊验证（字符串类型）
    if action == "password":
        if value is None:
            return False, "MISSING_VALUE", "修改密码需要提供新密码"
        pwd = str(value)
        if not pwd.isdigit() or len(pwd) < 4 or len(pwd) > 8:
            return False, "INVALID_VALUE", "密码必须为4-8位数字"
        return True, "", ""

    # 检查字符串选项型动作
    range_key = (device, action)
    if range_key in STRING_VALUE_OPTIONS:
        valid_options, _ = STRING_VALUE_OPTIONS[range_key]
        if value is None:
            return False, "MISSING_VALUE", f"动作 '{action}' 需要提供参数，有效值: {', '.join(valid_options)}"
        value_str = str(value).lower()
        if value_str not in [opt.lower() for opt in valid_options]:
            return False, "INVALID_VALUE", f"'{value}' 不是有效选项，有效值: {', '.join(valid_options)}"
        return True, "", ""

    # 无需 value 的动作
    if action in NO_VALUE_ACTIONS:
        return True, "", ""

    # 验证数值参数
    if action in VALUE_REQUIRED_ACTIONS:
        if value is None:
            return False, "MISSING_VALUE", f"动作 '{action}' 需要提供数值参数"

        # 尝试转换数值
        try:
            num_value = int(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            return False, "INVALID_VALUE", f"动作 '{action}' 的值必须为数字"

        # 优先使用按设备区分的范围
        if range_key in DEVICE_VALUE_RANGES:
            min_val, max_val, name = DEVICE_VALUE_RANGES[range_key]
        elif action in VALUE_RANGES:
            min_val, max_val, name = VALUE_RANGES[action]
        else:
            return True, "", ""

        if not (min_val <= num_value <= max_val):
            return False, "INVALID_VALUE", f"{name}值必须在 {min_val} 到 {max_val} 之间"

    return True, "", ""


def normalize_string_value(device: str, action: str, value) -> Any:
    """将中文字符串值标准化为英文名"""
    range_key = (device, action)
    if range_key in STRING_VALUE_OPTIONS:
        _, display_map = STRING_VALUE_OPTIONS[range_key]
        if display_map:
            value_str = str(value).lower()
            for k, v in display_map.items():
                if k.lower() == value_str or v == value:
                    return k
    return value


def execute_device_action(device: str, action: str, value) -> Dict[str, Any]:
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
        if device == "vacuum":
            state["cleaning"] = False
            state["paused"] = False
        if device == "curtain":
            state["moving"] = False

    # --- 灯光 ---
    elif action == "brightness":
        state["brightness"] = value
        print(f"  >>> [硬件] {device} 亮度设置为: {value}%")
    elif action == "color":
        value = normalize_string_value(device, action, value)
        state["color"] = value
        _, display_map = STRING_VALUE_OPTIONS.get(("light", "color"), (None, None))
        display_name = display_map.get(value, value) if display_map else value
        print(f"  >>> [硬件] {device} 色彩设置为: {display_name}")
    elif action == "scene":
        value = normalize_string_value(device, action, value)
        state["scene"] = value
        _, display_map = STRING_VALUE_OPTIONS.get(("light", "scene"), (None, None))
        display_name = display_map.get(value, value) if display_map else value
        print(f"  >>> [硬件] {device} 场景设置为: {display_name}")

    # --- 空调 ---
    elif action == "temperature":
        state["temperature"] = value
        print(f"  >>> [硬件] {device} 温度设置为: {value}°C")
    elif action == "mode":
        value = normalize_string_value(device, action, value)
        state["mode"] = value
        _, display_map = STRING_VALUE_OPTIONS.get(("ac", "mode"), (None, None))
        display_name = display_map.get(value, value) if display_map else value
        print(f"  >>> [硬件] {device} 模式设置为: {display_name}")
    elif action == "preset":
        value = normalize_string_value(device, action, value)
        state["preset"] = value
        _, display_map = STRING_VALUE_OPTIONS.get(("ac", "preset"), (None, None))
        display_name = display_map.get(value, value) if display_map else value
        print(f"  >>> [硬件] {device} 预设设置为: {display_name}")
    elif action == "fanspeed":
        state["fanspeed"] = value
        print(f"  >>> [硬件] {device} 风速设置为: {value}档")

    # --- 电视 ---
    elif action == "volume":
        state["volume"] = value
        print(f"  >>> [硬件] {device} 音量设置为: {value}")
    elif action == "source":
        state["source"] = value
        print(f"  >>> [硬件] {device} 信号源切换为: {value}")
    elif action == "status":
        print(f"  >>> [硬件] {device} 查询状态")

    # --- 音箱 ---
    elif action == "play":
        state["playing"] = True
        print(f"  >>> [硬件] {device} 开始播放")

    # --- 门锁 ---
    elif action == "unlock":
        state["locked"] = False
        print(f"  >>> [硬件] {device} 已开锁")
    elif action == "lock":
        state["locked"] = True
        print(f"  >>> [硬件] {device} 已关锁")
    elif action == "password":
        state["password"] = str(value)
        print(f"  >>> [硬件] {device} 密码已修改")

    # --- 扫地机器人 ---
    elif action == "mode":
        mode_names = {1: "扫地", 2: "拖地", 3: "扫拖一体"}
        state["mode"] = value
        print(f"  >>> [硬件] {device} 模式设置为: {mode_names.get(value, value)}")
    elif action == "pause":
        state["paused"] = True
        print(f"  >>> [硬件] {device} 已暂停清扫")
    elif action == "dock":
        state["power"] = False
        state["cleaning"] = False
        state["paused"] = False
        state["location"] = "充电座"
        print(f"  >>> [硬件] {device} 返回充电座")
    elif action == "locate":
        print(f"  >>> [硬件] {device} 当前位置: {state.get('location', '充电座')}")

    # --- 空气净化器 ---
    elif action == "speed":
        state["speed"] = value
        print(f"  >>> [硬件] {device} 风速设置为: {value}档")
    elif action == "ion":
        state["ion"] = bool(value)
        print(f"  >>> [硬件] {device} 负离子: {'ON' if value else 'OFF'}")
    elif action == "uv":
        state["uv"] = bool(value)
        print(f"  >>> [硬件] {device} UV灯: {'ON' if value else 'OFF'}")

    # --- 风扇 ---
    elif action == "oscillate":
        state["oscillating"] = bool(value)
        print(f"  >>> [硬件] {device} 摇头: {'ON' if value else 'OFF'}")
    elif action == "oscillate_angle":
        state["oscillate_angle"] = value
        print(f"  >>> [硬件] {device} 摇头角度设置为: {value}°")
    elif action == "fan_mode":
        value = normalize_string_value(device, action, value)
        state["fan_mode"] = value
        _, display_map = STRING_VALUE_OPTIONS.get(("fan", "fan_mode"), (None, None))
        display_name = display_map.get(value, value) if display_map else value
        print(f"  >>> [硬件] {device} 风扇模式设置为: {display_name}")

    # --- 窗帘 ---
    elif action == "pause":
        state["moving"] = False
        print(f"  >>> [硬件] {device} 已暂停")
    elif action == "position":
        state["position"] = value
        print(f"  >>> [硬件] {device} 位置设置为: {value}%")
    elif action == "schedule":
        state["scheduled"] = bool(value)
        print(f"  >>> [硬件] {device} 定时: {'开启' if value else '关闭'}")

    # --- 加湿器 ---
    elif action == "mode":
        value = normalize_string_value(device, action, value)
        state["mode"] = value
        _, display_map = STRING_VALUE_OPTIONS.get(("humidifier", "mode"), (None, None))
        display_name = display_map.get(value, value) if display_map else value
        print(f"  >>> [硬件] {device} 模式设置为: {display_name}")
    elif action == "humidity":
        state["humidity"] = value
        print(f"  >>> [硬件] {device} 目标湿度设置为: {value}%")
    elif action == "filter_level":
        state["filter_level"] = value
        print(f"  >>> [硬件] {device} 过滤等级设置为: {value}级")

    return state.copy()


def get_action_message(device: str, action: str, value) -> str:
    """生成操作成功消息"""
    DEVICE_NAMES = {
        "light": "灯光", "ac": "空调", "tv": "电视", "speaker": "音箱",
        "lock": "门锁", "vacuum": "扫地机器人", "purifier": "空气净化器",
        "fan": "风扇", "plug": "插座", "switch": "开关",
        "curtain": "窗帘", "humidifier": "加湿器",
    }
    name = DEVICE_NAMES.get(device, device)

    if action == "on":
        return f"{name}已开启"
    elif action == "off":
        return f"{name}已关闭"
    elif action == "brightness":
        return f"亮度已设置为 {value}%"
    elif action == "color":
        _, display_map = STRING_VALUE_OPTIONS.get(("light", "color"), (None, None))
        display = display_map.get(value, value) if display_map else value
        return f"灯光色彩已切换为{display}"
    elif action == "scene":
        _, display_map = STRING_VALUE_OPTIONS.get(("light", "scene"), (None, None))
        display = display_map.get(value, value) if display_map else value
        return f"灯光场景已切换为{display}模式"
    elif action == "temperature":
        return f"温度已设置为 {value}°C"
    elif action == "mode":
        if device == "ac":
            _, display_map = STRING_VALUE_OPTIONS.get(("ac", "mode"), (None, None))
            display = display_map.get(value, value) if display_map else value
            return f"空调已切换为{display}模式"
        elif device == "vacuum":
            mode_names = {1: "扫地", 2: "拖地", 3: "扫拖一体"}
            return f"扫地机器人模式已设置为{mode_names.get(value, value)}"
        elif device == "humidifier":
            _, display_map = STRING_VALUE_OPTIONS.get(("humidifier", "mode"), (None, None))
            display = display_map.get(value, value) if display_map else value
            return f"加湿器已切换为{display}模式"
        elif device == "fan":
            _, display_map = STRING_VALUE_OPTIONS.get(("fan", "fan_mode"), (None, None))
            display = display_map.get(value, value) if display_map else value
            return f"风扇已切换为{display}模式"
        return f"模式已设置"
    elif action == "preset":
        _, display_map = STRING_VALUE_OPTIONS.get(("ac", "preset"), (None, None))
        display = display_map.get(value, value) if display_map else value
        return f"空调已切换为{display}模式"
    elif action == "fanspeed":
        return f"空调风速已设置为 {value}档"
    elif action == "volume":
        return f"音量已设置为 {value}"
    elif action == "source":
        return f"信号源已切换为 {value}"
    elif action == "status":
        return f"电视当前状态"
    elif action == "play":
        return "开始播放"
    elif action == "unlock":
        return "门锁已打开"
    elif action == "lock":
        return "门锁已锁定"
    elif action == "password":
        return "门锁密码已修改"
    elif action == "pause":
        if device == "vacuum":
            return "扫地机器人已暂停清扫"
        elif device == "curtain":
            return "窗帘已暂停"
        return "已暂停"
    elif action == "dock":
        return "扫地机器人已返回充电座"
    elif action == "locate":
        return "扫地机器人定位查询完成"
    elif action == "speed":
        return f"风速已设置为 {value}档"
    elif action == "ion":
        return f"负离子已{'开启' if value else '关闭'}"
    elif action == "uv":
        return f"UV灯已{'开启' if value else '关闭'}"
    elif action == "oscillate":
        return f"风扇摇头已{'开启' if value else '关闭'}"
    elif action == "oscillate_angle":
        return f"风扇摇头角度已设置为 {value}°"
    elif action == "fan_mode":
        _, display_map = STRING_VALUE_OPTIONS.get(("fan", "fan_mode"), (None, None))
        display = display_map.get(value, value) if display_map else value
        return f"风扇已切换为{display}"
    elif action == "position":
        return f"窗帘位置已设置为 {value}%"
    elif action == "schedule":
        return f"窗帘定时已{'开启' if value else '关闭'}"
    elif action == "humidity":
        return f"目标湿度已设置为 {value}%"
    elif action == "filter_level":
        return f"过滤等级已设置为 {value}级"

    return "操作成功"


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

    # 标准化字符串值
    range_key = (device, action)
    if range_key in STRING_VALUE_OPTIONS and value is not None:
        value = normalize_string_value(device, action, value)

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
# 设备管理路由
# ============================================================================

@app.route('/device_list', methods=['GET', 'POST'])
def device_list():
    """查询设备列表"""
    print("\n[请求] 查询设备列表")
    return jsonify({
        "status": "ok",
        "devices": device_registry,
        "total": len(device_registry)
    }), 200


@app.route('/device_add', methods=['POST'])
def device_add():
    """添加新设备"""
    print("\n[请求] 添加设备")

    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)
    except Exception as e:
        return create_error_response("INVALID_REQUEST", f"无法解析JSON请求体: {e}", 400)

    device_type = data.get("type")
    device_name = data.get("name")
    room = data.get("room", "未分类")

    if not device_type:
        return create_error_response("MISSING_PARAM", "缺少 'type' 参数（设备类型）", 400)
    if not device_name:
        return create_error_response("MISSING_PARAM", "缺少 'name' 参数（设备名称）", 400)
    if device_type not in DEVICE_ACTIONS:
        return create_error_response("INVALID_DEVICE_TYPE",
                                     f"不支持的设备类型 '{device_type}'，"
                                     f"支持: {', '.join(DEVICE_ACTIONS.keys())}", 400)

    global _device_counter
    _device_counter += 1
    new_device = {
        "id": f"{device_type}_{_device_counter:03d}",
        "name": device_name,
        "type": device_type,
        "room": room,
        "status": "online"
    }
    device_registry.append(new_device)

    print(f"  >>> 添加设备: {new_device}")

    return jsonify({
        "status": "ok",
        "message": f"设备 '{device_name}' 添加成功",
        "device": new_device
    }), 200


# ============================================================================
# 家庭任务路由
# ============================================================================

# 模拟任务存储
home_tasks: List[Dict[str, Any]] = []


@app.route('/task/list', methods=['GET'])
def task_list():
    """查询家庭任务列表"""
    print("\n[请求] 查询家庭任务列表")
    return jsonify({
        "status": "ok",
        "tasks": home_tasks,
        "total": len(home_tasks)
    }), 200


@app.route('/task/add', methods=['POST'])
def task_add():
    """添加家庭任务（定时任务 / 条件触发任务）"""
    print("\n[请求] 添加家庭任务")

    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)
    except Exception as e:
        return create_error_response("INVALID_REQUEST", f"无法解析JSON请求体: {e}", 400)

    task_type = data.get("type")  # "schedule"（定时）或 "trigger"（条件触发）
    task_name = data.get("name", "")
    action_config = data.get("action", {})  # 要执行的动作配置

    if not task_type or task_type not in ["schedule", "trigger"]:
        return create_error_response("INVALID_PARAM",
                                     "缺少 'type' 参数，必须为 'schedule'（定时）或 'trigger'（条件触发）", 400)

    if not action_config:
        return create_error_response("MISSING_PARAM", "缺少 'action' 参数（任务执行的动作配置）", 400)

    if task_type == "schedule":
        # 定时任务: {"device": "curtain", "action": "on", "time": "08:00", "repeat": "daily"}
        if not action_config.get("time"):
            return create_error_response("MISSING_PARAM", "定时任务需要提供 'time' 参数", 400)
        task = {
            "id": f"task_{len(home_tasks) + 1:03d}",
            "name": task_name or f"定时任务",
            "type": "schedule",
            "device": action_config.get("device"),
            "action": action_config.get("action"),
            "value": action_config.get("value"),
            "time": action_config.get("time"),
            "repeat": action_config.get("repeat", "daily"),
            "enabled": True
        }
    else:
        # 条件触发任务: {"device": "humidifier", "action": "on", "condition": {"sensor": "humidity", "operator": "<", "threshold": 30}}
        condition = action_config.get("condition")
        if not condition:
            return create_error_response("MISSING_PARAM", "条件触发任务需要提供 'condition' 参数", 400)
        task = {
            "id": f"task_{len(home_tasks) + 1:03d}",
            "name": task_name or f"条件触发任务",
            "type": "trigger",
            "device": action_config.get("device"),
            "action": action_config.get("action"),
            "value": action_config.get("value"),
            "condition": condition,
            "check_interval": action_config.get("check_interval", "1h"),
            "enabled": True
        }

    home_tasks.append(task)
    print(f"  >>> 添加任务: {task}")

    return jsonify({
        "status": "ok",
        "message": f"任务 '{task['name']}' 添加成功",
        "task": task
    }), 200


@app.route('/task/enable', methods=['POST'])
def task_enable():
    """启用/禁用家庭任务"""
    print("\n[请求] 启用/禁用任务")

    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)
    except Exception as e:
        return create_error_response("INVALID_REQUEST", f"无法解析JSON请求体: {e}", 400)

    task_id = data.get("task_id")
    enabled = data.get("enabled")

    if not task_id:
        return create_error_response("MISSING_PARAM", "缺少 'task_id' 参数", 400)

    for task in home_tasks:
        if task["id"] == task_id:
            task["enabled"] = bool(enabled) if enabled is not None else True
            status_text = "启用" if task["enabled"] else "禁用"
            print(f"  >>> 任务 {task_id} 已{status_text}")
            return jsonify({
                "status": "ok",
                "message": f"任务 '{task['name']}' 已{status_text}",
                "task": task
            }), 200

    return create_error_response("NOT_FOUND", f"未找到任务 '{task_id}'", 404)


@app.route('/task/delete', methods=['POST'])
def task_delete():
    """删除家庭任务"""
    print("\n[请求] 删除任务")

    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)
    except Exception as e:
        return create_error_response("INVALID_REQUEST", f"无法解析JSON请求体: {e}", 400)

    task_id = data.get("task_id")
    if not task_id:
        return create_error_response("MISSING_PARAM", "缺少 'task_id' 参数", 400)

    for i, task in enumerate(home_tasks):
        if task["id"] == task_id:
            removed = home_tasks.pop(i)
            print(f"  >>> 删除任务: {task_id}")
            return jsonify({
                "status": "ok",
                "message": f"任务 '{removed['name']}' 已删除"
            }), 200

    return create_error_response("NOT_FOUND", f"未找到任务 '{task_id}'", 404)


# ============================================================================
# 设备控制路由
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


@app.route('/curtain', methods=['POST'])
def control_curtain():
    """窗帘控制"""
    return handle_device_request("curtain")


@app.route('/humidifier', methods=['POST'])
def control_humidifier():
    """加湿器控制"""
    return handle_device_request("humidifier")


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
        "devices": list(DEVICE_ACTIONS.keys()),
        "features": ["device_control", "device_management", "home_tasks"]
    }), 200


@app.route('/', methods=['GET'])
def index():
    """根路径信息"""
    return jsonify({
        "service": "Home Control Server",
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
            "/device_list": "查询设备列表 (GET/POST)",
            "/device_add": "添加新设备 (POST: type, name, room)",
            "/task/list": "查询家庭任务 (GET)",
            "/task/add": "添加家庭任务 (POST: type, action)",
            "/task/enable": "启用/禁用任务 (POST: task_id, enabled)",
            "/task/delete": "删除任务 (POST: task_id)",
            "/health": "健康检查",
        }
    }), 200


# ============================================================================
# 启动服务
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("        家居控制服务端 (扩展版 v3.0)")
    print("=" * 60)
    print(f"  监听地址: http://127.0.0.1:22222")
    print(f"  支持设备: {', '.join(DEVICE_ACTIONS.keys())}")
    print(f"  扩展功能: 设备管理, 家庭任务(定时/条件触发)")
    print("=" * 60)
    print("  测试命令示例:")
    print("    curl -X POST http://127.0.0.1:22222/light \\")
    print("      -H 'Content-Type: application/json' \\")
    print("      -d '{\"action\": \"color\", \"value\": \"warm\"}'")
    print("    curl -X POST http://127.0.0.1:22222/curtain \\")
    print("      -H 'Content-Type: application/json' \\")
    print("      -d '{\"action\": \"position\", \"value\": 50}'")
    print("    curl -X POST http://127.0.0.1:22222/task/add \\")
    print("      -H 'Content-Type: application/json' \\")
    print("      -d '{\"type\": \"schedule\", \"action\": {\"device\": \"curtain\", \"action\": \"on\", \"time\": \"08:00\"}}'")
    print("=" * 60)
    print()

    app.run(host='127.0.0.1', port=22222, debug=True)
