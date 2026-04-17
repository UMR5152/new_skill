#!/usr/bin/env python3
"""
Home Control Script (Extended)
Control smart home devices via HTTP requests to http://127.0.0.1:22222/

Supports all devices from the extended server including:
- Light, AC, TV, Speaker, Lock, Vacuum, Purifier, Fan, Plug, Switch
- Curtain (窗帘)
- Humidifier (加湿器)
- Device list management
"""

import argparse
import sys
import json
from typing import Optional, Dict, Any, List

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# API base URL
BASE_URL = "http://127.0.0.1:22222"

# Mock mode flag (will be set by argparse)
MOCK_MODE = False

# Device aliases (support both English and Chinese)
DEVICE_ALIASES = {
    # 现有设备
    "light": "light",
    "灯": "light",
    "灯光": "light",
    "智能灯光": "light",
    "ac": "ac",
    "空调": "ac",
    "tv": "tv",
    "电视": "tv",
    "电视机": "tv",
    "speaker": "speaker",
    "音箱": "speaker",
    "lock": "lock",
    "门锁": "lock",
    "智能门锁": "lock",
    "vacuum": "vacuum",
    "扫地机器人": "vacuum",
    "扫地机": "vacuum",
    "purifier": "purifier",
    "空气净化器": "purifier",
    "净化器": "purifier",
    "fan": "fan",
    "风扇": "fan",
    "plug": "plug",
    "插座": "plug",
    "智能插座": "plug",
    "switch": "switch",
    "开关": "switch",
    "智能开关": "switch",
    # 新增设备
    "curtain": "curtain",
    "窗帘": "curtain",
    "窗帘电机": "curtain",
    "humidifier": "humidifier",
    "加湿器": "humidifier",
    # 通用功能
    "device_list": "device_list",
    "设备列表": "device_list",
    "查询设备": "device_list",
    "查看设备": "device_list",
    "device_add": "device_add",
    "添加设备": "device_add",
}

# Action aliases (support both English and Chinese)
ACTION_ALIASES = {
    # 通用动作
    "on": "on",
    "开": "on",
    "开启": "on",
    "打开": "on",
    "off": "off",
    "关": "off",
    "关闭": "off",
    "pause": "pause",
    "暂停": "pause",
    "stop": "off",
    "停止": "off",

    # 灯光
    "brightness": "brightness",
    "亮度": "brightness",
    "color": "color",
    "光色": "color",
    "色彩": "color",
    "色调": "color",
    "scene": "scene",
    "场景": "scene",
    "模式": "mode",

    # 空调
    "temperature": "temperature",
    "温度": "temperature",
    "mode": "mode",
    "制冷": "cool",
    "制热": "heat",
    "除湿": "dehumidify",
    "送风": "fan",
    "自动": "auto",
    "preset": "preset",
    "预设": "preset",
    "睡眠": "sleep",
    "静音": "silent",
    "节能": "eco",
    "fanspeed": "fanspeed",
    "空调风速": "fanspeed",
    "调大": "up",
    "调小": "down",

    # 电视
    "volume": "volume",
    "音量": "volume",
    "source": "source",
    "信号源": "source",
    "切换信号": "source",
    "status": "status",
    "状态": "status",
    "查询状态": "status",
    "同步状态": "status",

    # 音箱
    "play": "play",
    "播放": "play",

    # 门锁
    "unlock": "unlock",
    "开锁": "unlock",
    "lock": "lock",
    "关锁": "lock",
    "上锁": "lock",
    "password": "password",
    "密码": "password",
    "修改密码": "password",

    # 扫地机器人
    "打扫": "on",
    "清扫": "on",
    "充电": "dock",
    "回充": "dock",
    "定位": "locate",
    "位置": "locate",
    "在哪里": "locate",

    # 风扇
    "speed": "speed",
    "风速": "speed",
    "档位": "speed",
    "oscillate": "oscillate",
    "摇头": "oscillate",
    "oscillate_angle": "oscillate_angle",
    "摇头角度": "oscillate_angle",
    "fan_mode": "fan_mode",
    "自然风": "natural",
    "睡眠风": "sleep",
    "智能风": "smart",
    "正常风": "normal",

    # 空气净化器
    "ion": "ion",
    "负离子": "ion",
    "uv": "uv",
    "uv灯": "uv",

    # 窗帘
    "position": "position",
    "位置": "position",
    "打开多少": "position",
    "schedule": "schedule",
    "定时": "schedule",

    # 加湿器
    "humidity": "humidity",
    "湿度": "humidity",
    "filter_level": "filter_level",
    "过滤等级": "filter_level",
    "过滤": "filter_level",
    "强劲": "strong",
    "自动": "auto",

    # 设备管理
    "get": "get",
    "获取": "get",
    "add": "add",
    "新增": "add",
}

# Valid actions for each device
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
    "device_list": ["get"],
    "device_add": ["add"],
}

# Value ranges for actions that require a value
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

# Per-device value ranges (takes priority over VALUE_RANGES)
DEVICE_VALUE_RANGES = {
    ("fan", "speed"): (1, 3, "风速"),
    ("purifier", "speed"): (1, 5, "风速"),
    ("ac", "fanspeed"): (1, 4, "空调风速"),
}

# String value options (map device+action to valid string values)
STRING_VALUE_OPTIONS = {
    ("light", "color"): ["warm", "cool", "natural", "暖光", "白光", "自然光"],
    ("light", "scene"): ["cozy", "reading", "romantic", "温馨", "阅读", "浪漫"],
    ("ac", "mode"): ["cool", "heat", "dehumidify", "fan", "auto", "制冷", "制热", "除湿", "送风", "自动"],
    ("ac", "preset"): ["sleep", "silent", "eco", "睡眠", "静音", "节能"],
    ("fan", "fan_mode"): ["natural", "sleep", "smart", "normal", "自然风", "睡眠风", "智能风", "正常风"],
    ("tv", "source"): ["HDMI1", "HDMI2", "AV", "TV", "USB"],
    ("humidifier", "mode"): ["strong", "sleep", "auto", "强劲", "睡眠", "自动"],
}


def validate_value(device: str, action: str, value) -> tuple[bool, str]:
    """Validate the value for a given action."""
    # Password special validation
    if action == "password":
        if value is None:
            return False, "修改密码需要提供新密码"
        pwd = str(value)
        if not pwd.isdigit() or len(pwd) < 4 or len(pwd) > 8:
            return False, "密码必须为4-8位数字"
        return True, ""

    # Check if this device+action combination has string options
    range_key = (device, action)
    if range_key in STRING_VALUE_OPTIONS:
        valid_options = STRING_VALUE_OPTIONS[range_key]
        if value is None:
            return False, f"动作 '{action}' 需要提供参数"
        value_str = str(value).lower()
        for opt in valid_options:
            if opt.lower() == value_str:
                return True, ""
        return False, f"'{value}' 不是有效的选项，有效值: {', '.join(valid_options)}"

    # Check per-device numeric range first, then global range
    if range_key in DEVICE_VALUE_RANGES:
        min_val, max_val, name = DEVICE_VALUE_RANGES[range_key]
    elif action in VALUE_RANGES:
        min_val, max_val, name = VALUE_RANGES[action]
    else:
        # No value validation needed for this action
        return True, ""

    if value is None:
        return False, f"动作 '{action}' 需要提供一个数值参数"

    if not (min_val <= value <= max_val):
        return False, f"{name}值必须在 {min_val} 到 {max_val} 之间"

    return True, ""


def send_control_request(device: str, action: str, value: Optional[Any] = None, save_request_path: Optional[str] = None) -> Dict[str, Any]:
    """Send control request to the home automation server."""
    # Special handling for device_list and device_add
    if device == "device_list":
        url = f"{BASE_URL}/{device}"
        payload = {"action": "get"} if action == "get" else {}
    elif device == "device_add":
        url = f"{BASE_URL}/{device}"
        payload = value if isinstance(value, dict) else {}
    else:
        url = f"{BASE_URL}/{device}"
        payload = {"action": action}
        if value is not None:
            payload["value"] = value

    # Save raw HTTP request if path is provided
    if save_request_path:
        request_text = format_raw_http_request(url, payload)
        try:
            with open(save_request_path, 'w', encoding='utf-8') as f:
                f.write(request_text)
        except Exception as e:
            print(f"警告: 无法保存请求到文件 {save_request_path}: {e}")

    # Mock mode - simulate successful response
    if MOCK_MODE:
        if device == "device_list":
            mock_data = {
                "devices": [
                    {"id": "light_001", "name": "客厅灯", "type": "light", "room": "客厅", "status": "online"},
                    {"id": "ac_001", "name": "客厅空调", "type": "ac", "room": "客厅", "status": "online"},
                ],
                "total": 2
            }
        elif device == "device_add":
            mock_data = {"device": value, "message": "设备添加成功"}
        else:
            mock_data = {
                "device": device,
                "action": action,
                "value": value,
                "status": "ok"
            }
        return {
            "success": True,
            "data": mock_data,
            "status_code": 200
        }

    if not REQUESTS_AVAILABLE:
        return {"success": False, "error": "requests库未安装，请运行: pip install requests"}

    try:
        # Use GET for device_list, POST for others
        if device == "device_list":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return {"success": True, "data": response.json(), "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "无法连接到家居控制服务器 (127.0.0.1:22222)，可使用 --mock 模式测试"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP错误: {e}", "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"请求失败: {e}"}


def format_raw_http_request(url: str, payload: Dict[str, Any]) -> str:
    """Format the raw HTTP request for saving."""
    import urllib.parse

    parsed = urllib.parse.urlparse(url)
    path = parsed.path if parsed.path else "/"
    body = json.dumps(payload, ensure_ascii=False, indent=2)

    request_lines = [
        f"POST {path} HTTP/1.1",
        f"Host: {parsed.netloc}",
        "Content-Type: application/json",
        f"Content-Length: {len(body.encode('utf-8'))}",
        "Accept: application/json",
        "User-Agent: home-control/3.0",
        "",
        body
    ]

    return "\n".join(request_lines)


def get_device_display_name(device: str) -> str:
    """Get display name for device."""
    names = {
        "light": "智能灯光", "ac": "空调", "tv": "电视", "speaker": "音箱",
        "lock": "智能门锁", "vacuum": "扫地机器人",
        "purifier": "空气净化器", "fan": "风扇",
        "plug": "智能插座", "switch": "智能开关",
        "curtain": "窗帘", "humidifier": "加湿器",
        "device_list": "设备列表", "device_add": "添加设备",
    }
    return names.get(device, device)


def get_action_display_name(action: str) -> str:
    """Get display name for action."""
    names = {
        "on": "开启", "off": "关闭", "pause": "暂停",
        "brightness": "设置亮度", "temperature": "设置温度",
        "volume": "设置音量", "play": "开始播放",
        "unlock": "开锁", "lock": "关锁", "password": "修改密码",
        "mode": "设置模式", "speed": "设置风速",
        "oscillate": "设置摇头", "oscillate_angle": "设置摇头角度",
        "color": "设置色彩", "scene": "切换场景",
        "preset": "切换预设", "fanspeed": "设置空调风速",
        "source": "切换信号源", "status": "查询状态",
        "dock": "返回充电", "locate": "定位",
        "ion": "控制负离子", "uv": "控制UV灯",
        "position": "设置位置", "schedule": "设置定时",
        "humidity": "设置湿度", "filter_level": "设置过滤等级",
        "cool": "切换到制冷", "heat": "切换到制热",
        "dehumidify": "切换到除湿", "fan": "切换到送风",
        "auto": "切换到自动", "natural": "切换到自然风",
        "sleep": "切换到睡眠模式", "silent": "切换到静音模式",
        "smart": "切换到智能模式", "normal": "切换到正常模式",
        "strong": "切换到强劲模式", "eco": "切换到节能模式",
        "get": "获取", "add": "添加",
    }
    return names.get(action, action)


def parse_value(action: str, raw_value: str) -> Any:
    """Parse value based on action type."""
    if raw_value is None:
        return None

    # Password and string actions keep as string
    if action == "password":
        return raw_value

    # Check if this device+action combination expects string options
    # We'll check during validation, but try to parse as int first
    try:
        return int(raw_value)
    except ValueError:
        # Not a number, return as string
        return raw_value


def display_device_list(devices: List[Dict[str, Any]]):
    """Display device list in a formatted way."""
    if not devices:
        print("没有找到设备")
        return

    print("\n" + "=" * 60)
    print(f"设备列表 (共 {len(devices)} 个设备)")
    print("=" * 60)

    for i, device in enumerate(devices, 1):
        print(f"{i}. [{device['id']}] {device['name']}")
        print(f"   类型: {device['type']}, 位置: {device['room']}, 状态: {device['status']}")

    print("=" * 60)


def main():
    global MOCK_MODE

    parser = argparse.ArgumentParser(
        description="家居控制 - 控制智能家居设备 (扩展版)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 灯光控制
  %(prog)s light on                       # 打开灯
  %(prog)s 灯 亮度 80                      # 设置亮度为80
  %(prog)s 灯 光色 暖光                    # 切换为暖光
  %(prog)s 灯 场景 温馨                    # 切换到温馨模式

  # 空调控制
  %(prog)s ac temperature 24               # 设置温度为24度
  %(prog)s 空调 制冷                       # 切换到制冷模式
  %(prog)s 空调 预设 睡眠                   # 切换到睡眠模式
  %(prog)s 空调 风速 3                      # 设置空调风速为3档

  # 电视控制
  %(prog)s tv source HDMI1                 # 切换信号源为HDMI1
  %(prog)s 电视 状态                        # 查询电视状态

  # 扫地机器人
  %(prog)s vacuum pause                    # 暂停清扫
  %(prog)s 扫地机器人 回充                  # 返回充电座
  %(prog)s 扫地机器人 定位                  # 查询位置

  # 空气净化器
  %(prog)s purifier ion 1                  # 开启负离子
  %(prog)s 净化器 uv 1                     # 开启UV灯

  # 风扇
  %(prog)s fan oscillate_angle 60          # 设置摇头角度为60度
  %(prog)s 风扇 自然风                      # 切换到自然风模式

  # 窗帘
  %(prog)s curtain position 50             # 窗帘打开到50%%
  %(prog)s 窗帘 打开                        # 完全打开窗帘

  # 加湿器
  %(prog)s humidifier humidity 60          # 设置湿度为60%%
  %(prog)s 加湿器 模式 强劲                 # 切换到强劲模式

  # 设备管理
  %(prog)s device_list                     # 查看设备列表
  %(prog)s 添加设备 灯 卧室灯 卧室          # 添加新设备
  %(prog)s 查询设备                         # 查看设备列表

  # 模拟模式
  %(prog)s --mock light on                 # 模拟模式测试
        """,
    )

    parser.add_argument(
        "device",
        nargs="?",
        help="设备名称: light/灯, ac/空调, tv/电视, speaker/音箱, "
             "lock/门锁, vacuum/扫地机器人, purifier/净化器, "
             "fan/风扇, plug/插座, switch/开关, "
             "curtain/窗帘, humidifier/加湿器, "
             "device_list/设备列表, device_add/添加设备",
    )

    parser.add_argument(
        "action",
        nargs="?",
        help="操作: on/开, off/关, brightness/亮度, temperature/温度, "
             "volume/音量, play/播放, unlock/开锁, lock/关锁, "
             "password/密码, mode/模式, speed/风速, oscillate/摇头, "
             "color/光色, scene/场景, source/信号源, status/状态, "
             "preset/预设, fanspeed/空调风速, pause/暂停, dock/回充, "
             "locate/定位, ion/负离子, uv/uv灯, position/位置, "
             "schedule/定时, humidity/湿度, filter_level/过滤等级",
    )

    parser.add_argument(
        "value",
        nargs="?",
        help="数值或选项 (亮度: 0-100, 温度: 16-30, 音量: 0-100, "
             "密码: 4-8位数字, 模式: 1-3, 风速: 1-5, 摇头: 0/1, "
             "光色: warm/cool/natural, 场景: cozy/reading/romantic, "
             "空调模式: cool/heat/dehumidify/fan/auto, "
             "预设: sleep/silent/eco, 风扇模式: natural/sleep/smart/normal, "
             "信号源: HDMI1/HDMI2/AV/TV/USB, "
             "位置: 0-100, 湿度: 30-90, 过滤等级: 1-5)",
    )

    # For device_add, we need additional parameters
    parser.add_argument(
        "--room",
        help="设备所在房间 (用于添加设备)",
    )

    parser.add_argument(
        "--mock", "-m",
        action="store_true",
        help="模拟模式 (无需服务器，用于测试)",
    )

    parser.add_argument(
        "--save-request",
        help="保存原始HTTP请求到指定文件",
    )

    args = parser.parse_args()

    # Set mock mode
    MOCK_MODE = args.mock

    # Handle device_list as a simple command
    if args.device is None:
        parser.print_help()
        sys.exit(0)

    # Map device alias
    device = DEVICE_ALIASES.get(args.device.lower())
    if not device:
        print(f"错误: 未知的设备 '{args.device}'")
        print(f"支持的设备: {', '.join(set(DEVICE_ALIASES.keys()))}")
        sys.exit(1)

    # Special handling for device_add
    if device == "device_add":
        if not args.action:
            print("错误: 添加设备需要指定设备类型和名称")
            print("用法: python home_control_extended.py device_add <设备类型> <设备名称> [--room 房间]")
            sys.exit(1)

        device_type = args.action
        device_name = args.value
        if not device_name:
            print("错误: 需要提供设备名称")
            sys.exit(1)

        value = {
            "type": device_type,
            "name": device_name,
            "room": args.room or "未分类"
        }

        result = send_control_request(device, "add", value, args.save_request)

        if result["success"]:
            print(f"✓ {result['data'].get('message', '设备添加成功')}")
            if "device" in result["data"]:
                print(f"  设备信息: {json.dumps(result['data']['device'], ensure_ascii=False)}")
        else:
            print(f"✗ 操作失败: {result['error']}")
            sys.exit(1)

        return

    # For device_list, no action needed
    if device == "device_list":
        result = send_control_request(device, "get", None, args.save_request)

        if result["success"]:
            display_device_list(result["data"].get("devices", []))
        else:
            print(f"✗ 操作失败: {result['error']}")
            sys.exit(1)

        return

    # For regular devices, action is required
    if not args.action:
        print(f"错误: 设备 '{get_device_display_name(device)}' 需要指定操作")
        valid_actions = [a for a in ACTION_ALIASES.keys() if ACTION_ALIASES[a] in DEVICE_ACTIONS.get(device, [])]
        print(f"支持的操作: {', '.join(valid_actions)}")
        sys.exit(1)

    # Map action alias
    action = ACTION_ALIASES.get(args.action.lower())
    if not action:
        print(f"错误: 未知的操作 '{args.action}'")
        print(f"支持的操作: {', '.join(set(ACTION_ALIASES.keys()))}")
        sys.exit(1)

    # Validate action for device
    if action not in DEVICE_ACTIONS[device]:
        print(f"错误: 设备 '{get_device_display_name(device)}' 不支持操作 '{get_action_display_name(action)}'")
        valid_actions = [a for a in ACTION_ALIASES.keys() if ACTION_ALIASES[a] in DEVICE_ACTIONS[device]]
        print(f"支持的操作: {', '.join(valid_actions)}")
        sys.exit(1)

    # Parse value
    raw_value = parse_value(action, args.value)

    # Validate value
    is_valid, error_msg = validate_value(device, action, raw_value)
    if not is_valid:
        print(f"错误: {error_msg}")
        sys.exit(1)

    # Send request
    result = send_control_request(device, action, raw_value, args.save_request)

    if result["success"]:
        device_name = get_device_display_name(device)
        action_name = get_action_display_name(action)

        mock_indicator = " [模拟模式]" if MOCK_MODE else ""

        # Format output based on action type
        if action in ["status", "locate"]:
            print(f"✓ {device_name}{action_name}成功{mock_indicator}")
            if "state" in result["data"]:
                print(f"  状态: {json.dumps(result['data']['state'], ensure_ascii=False)}")
        elif raw_value is not None and not isinstance(raw_value, bool):
            print(f"✓ {device_name}{action_name}为 {raw_value}{mock_indicator}")
        else:
            print(f"✓ {device_name}已{action_name}{mock_indicator}")

        if "data" in result and result["data"]:
            print(f"  响应: {json.dumps(result['data'], ensure_ascii=False)}")
    else:
        print(f"✗ 操作失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
