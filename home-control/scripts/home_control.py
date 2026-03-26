#!/usr/bin/env python3
"""
Home Control Script
Control smart home devices via HTTP requests to http://127.0.0.1:22222/
"""

import argparse
import sys
import json
from typing import Optional, Dict, Any

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
    "light": "light",
    "灯": "light",
    "ac": "ac",
    "空调": "ac",
    "tv": "tv",
    "电视": "tv",
    "speaker": "speaker",
    "音箱": "speaker",
}

# Action aliases (support both English and Chinese)
ACTION_ALIASES = {
    "on": "on",
    "开": "on",
    "off": "off",
    "关": "off",
    "brightness": "brightness",
    "亮度": "brightness",
    "temperature": "temperature",
    "温度": "temperature",
    "volume": "volume",
    "音量": "volume",
    "play": "play",
    "播放": "play",
}

# Valid actions for each device
DEVICE_ACTIONS = {
    "light": ["on", "off", "brightness"],
    "ac": ["on", "off", "temperature"],
    "tv": ["on", "off", "volume"],
    "speaker": ["on", "off", "play", "volume"],
}

# Value ranges for actions that require a value
VALUE_RANGES = {
    "brightness": (0, 100, "亮度"),
    "temperature": (16, 30, "温度"),
    "volume": (0, 100, "音量"),
}


def validate_value(action: str, value: Optional[int]) -> tuple[bool, str]:
    """Validate the value for a given action."""
    if action not in VALUE_RANGES:
        return True, ""

    if value is None:
        return False, f"动作 '{action}' 需要提供一个数值参数"

    min_val, max_val, name = VALUE_RANGES[action]
    if not (min_val <= value <= max_val):
        return False, f"{name}值必须在 {min_val} 到 {max_val} 之间"

    return True, ""


def send_control_request(device: str, action: str, value: Optional[int] = None) -> Dict[str, Any]:
    """Send control request to the home automation server."""
    url = f"{BASE_URL}/{device}"
    payload = {"action": action}

    if value is not None:
        payload["value"] = value

    # Mock mode - simulate successful response
    if MOCK_MODE:
        return {
            "success": True,
            "data": {
                "device": device,
                "action": action,
                "value": value,
                "status": "ok",
                "mode": "mock"
            },
            "status_code": 200
        }

    if not REQUESTS_AVAILABLE:
        return {"success": False, "error": "requests库未安装，请运行: pip install requests"}

    try:
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


def get_device_display_name(device: str) -> str:
    """Get display name for device."""
    names = {"light": "灯光", "ac": "空调", "tv": "电视", "speaker": "音箱"}
    return names.get(device, device)


def get_action_display_name(action: str) -> str:
    """Get display name for action."""
    names = {
        "on": "开启",
        "off": "关闭",
        "brightness": "设置亮度",
        "temperature": "设置温度",
        "volume": "设置音量",
        "play": "开始播放",
    }
    return names.get(action, action)


def main():
    global MOCK_MODE

    parser = argparse.ArgumentParser(
        description="家居控制 - 控制智能家居设备",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s light on          # 打开灯
  %(prog)s 灯 开             # 打开灯 (中文)
  %(prog)s light brightness 80    # 设置灯亮度为80
  %(prog)s ac temperature 24       # 设置空调温度为24度
  %(prog)s tv volume 50            # 设置电视音量为50
  %(prog)s speaker play            # 音箱开始播放
  %(prog)s --mock light on         # 模拟模式测试
        """,
    )

    parser.add_argument(
        "device",
        help="设备名称: light/灯, ac/空调, tv/电视, speaker/音箱",
    )

    parser.add_argument(
        "action",
        help="操作: on/开, off/关, brightness/亮度, temperature/温度, volume/音量, play/播放",
    )

    parser.add_argument(
        "value",
        type=int,
        nargs="?",
        help="数值 (亮度: 0-100, 温度: 16-30, 音量: 0-100)",
    )

    parser.add_argument(
        "--mock", "-m",
        action="store_true",
        help="模拟模式 (无需服务器，用于测试)",
    )

    args = parser.parse_args()

    # Set mock mode
    MOCK_MODE = args.mock

    # Map device alias
    device = DEVICE_ALIASES.get(args.device.lower())
    if not device:
        print(f"错误: 未知的设备 '{args.device}'")
        print(f"支持的设备: {', '.join(set(DEVICE_ALIASES.keys()))}")
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

    # Validate value
    is_valid, error_msg = validate_value(action, args.value)
    if not is_valid:
        print(f"错误: {error_msg}")
        sys.exit(1)

    # Send request
    result = send_control_request(device, action, args.value)

    if result["success"]:
        device_name = get_device_display_name(device)
        action_name = get_action_display_name(action)

        mock_indicator = " [模拟模式]" if MOCK_MODE else ""

        if action in VALUE_RANGES:
            print(f"✓ {device_name}{action_name}为 {args.value}{mock_indicator}")
        else:
            print(f"✓ {device_name}已{action_name}{mock_indicator}")

        if "data" in result and result["data"]:
            print(f"  响应: {json.dumps(result['data'], ensure_ascii=False)}")
    else:
        print(f"✗ 操作失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
