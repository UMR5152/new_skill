# 家居控制服务端部署指南

本文档详细说明如何部署家居控制服务端，使其能够与 `home-control` 技能配合工作。

## 目录

- [服务概述](#服务概述)
- [API 规范](#api-规范)
- [请求格式](#请求格式)
- [响应格式](#响应格式)
- [错误处理](#错误处理)
- [示例服务端实现](#示例服务端实现)
- [部署说明](#部署说明)

---

## 服务概述

家居控制服务端需要：

- 监听地址：`127.0.0.1`
- 监听端口：`22222`
- 协议：HTTP
- 数据格式：JSON

服务端接收来自 `home_control.py` 脚本的 POST 请求，解析设备控制指令，执行相应的家居设备控制操作，并返回执行结果。

---

## API 规范

### 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `http://127.0.0.1:22222` |
| Content-Type | `application/json` |
| 请求方法 | `POST` |

### 端点列表

| 端点 | 描述 | 支持的动作 |
|------|------|-----------|
| `/light` | 灯光控制 | `on`, `off`, `brightness` |
| `/ac` | 空调控制 | `on`, `off`, `temperature` |
| `/tv` | 电视控制 | `on`, `off`, `volume` |
| `/speaker` | 音箱控制 | `on`, `off`, `play`, `volume` |
| `/lock` | 智能门锁控制 | `unlock`, `lock`, `password` |
| `/vacuum` | 扫地机器人控制 | `on`, `off`, `mode` |
| `/purifier` | 空气净化器控制 | `on`, `off`, `speed` |
| `/fan` | 风扇控制 | `on`, `off`, `speed`, `oscillate` |
| `/plug` | 智能插座控制 | `on`, `off` |
| `/switch` | 智能开关控制 | `on`, `off` |

---

## 请求格式

### 通用请求结构

所有请求均为 POST 方法，请求体为 JSON 格式：

```json
{
    "action": "<动作名称>",
    "value": <可选数值>
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | 是 | 要执行的动作 |
| `value` | integer | 否 | 动作参数值（某些动作需要） |

### 各设备请求详情

#### 1. 灯光控制 (`/light`)

**开启灯光**
```json
{
    "action": "on"
}
```

**关闭灯光**
```json
{
    "action": "off"
}
```

**设置亮度**
```json
{
    "action": "brightness",
    "value": 80
}
```
- `value` 范围：0-100（百分比）

#### 2. 空调控制 (`/ac`)

**开启空调**
```json
{
    "action": "on"
}
```

**关闭空调**
```json
{
    "action": "off"
}
```

**设置温度**
```json
{
    "action": "temperature",
    "value": 24
}
```
- `value` 范围：16-30（摄氏度）

#### 3. 电视控制 (`/tv`)

**开启电视**
```json
{
    "action": "on"
}
```

**关闭电视**
```json
{
    "action": "off"
}
```

**设置音量**
```json
{
    "action": "volume",
    "value": 50
}
```
- `value` 范围：0-100

#### 4. 音箱控制 (`/speaker`)

**开启音箱**
```json
{
    "action": "on"
}
```

**关闭音箱**
```json
{
    "action": "off"
}
```

**开始播放**
```json
{
    "action": "play"
}
```

**设置音量**
```json
{
    "action": "volume",
    "value": 30
}
```
- `value` 范围：0-100

#### 5. 智能门锁控制 (`/lock`)

**开锁**
```json
{
    "action": "unlock"
}
```

**关锁**
```json
{
    "action": "lock"
}
```

**修改密码**
```json
{
    "action": "password",
    "value": "654321"
}
```
- `value` 范围：4-8位数字

#### 6. 扫地机器人控制 (`/vacuum`)

**启动清扫**
```json
{
    "action": "on"
}
```

**停止清扫/回充**
```json
{
    "action": "off"
}
```

**设置清扫模式**
```json
{
    "action": "mode",
    "value": 1
}
```
- `value` 范围：1-3（1=扫地, 2=拖地, 3=扫拖一体）

#### 7. 空气净化器控制 (`/purifier`)

**开启净化器**
```json
{
    "action": "on"
}
```

**关闭净化器**
```json
{
    "action": "off"
}
```

**设置风速**
```json
{
    "action": "speed",
    "value": 3
}
```
- `value` 范围：1-5

#### 8. 风扇控制 (`/fan`)

**开启风扇**
```json
{
    "action": "on"
}
```

**关闭风扇**
```json
{
    "action": "off"
}
```

**设置风速**
```json
{
    "action": "speed",
    "value": 2
}
```
- `value` 范围：1-3

**设置摇头**
```json
{
    "action": "oscillate",
    "value": 1
}
```
- `value` 范围：0=关闭, 1=开启

#### 9. 智能插座控制 (`/plug`)

**开启插座**
```json
{
    "action": "on"
}
```

**关闭插座**
```json
{
    "action": "off"
}
```

#### 10. 智能开关控制 (`/switch`)

**开启开关**
```json
{
    "action": "on"
}
```

**关闭开关**
```json
{
    "action": "off"
}
```

---

## 响应格式

### 成功响应

HTTP 状态码：`200 OK`

```json
{
    "status": "ok",
    "device": "<设备名称>",
    "action": "<执行的动作>",
    "value": <设置的值，若无则为 null>,
    "message": "<可选的描述信息>"
}
```

**示例响应**

```json
{
    "status": "ok",
    "device": "light",
    "action": "brightness",
    "value": 80,
    "message": "灯光亮度已设置为 80%"
}
```

### 错误响应

HTTP 状态码：`4xx` 或 `5xx`

```json
{
    "status": "error",
    "error_code": "<错误代码>",
    "message": "<错误描述>"
}
```

**错误代码定义**

| 错误代码 | HTTP状态码 | 描述 |
|----------|-----------|------|
| `INVALID_ACTION` | 400 | 不支持的动作 |
| `INVALID_VALUE` | 400 | 无效的数值参数 |
| `MISSING_VALUE` | 400 | 缺少必要的数值参数 |
| `DEVICE_OFFLINE` | 503 | 设备离线 |
| `DEVICE_ERROR` | 500 | 设备控制失败 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

---

## 错误处理

服务端应实现以下验证和错误处理：

### 1. 请求验证

```python
def validate_request(device: str, action: str, value: Optional[int]) -> tuple[bool, str]:
    """验证请求参数"""

    # 设备支持的动作
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

    # 需要数值的动作
    VALUE_REQUIRED_ACTIONS = ["brightness", "temperature", "volume", "password", "mode", "speed", "oscillate"]

    # 数值范围
    VALUE_RANGES = {
        "brightness": (0, 100),
        "temperature": (16, 30),
        "volume": (0, 100),
        "mode": (1, 3),
        "oscillate": (0, 1),
    }

    # 按设备区分的数值范围
    DEVICE_VALUE_RANGES = {
        ("fan", "speed"): (1, 3),
        ("purifier", "speed"): (1, 5),
    }

    # 验证动作是否支持
    if action not in DEVICE_ACTIONS.get(device, []):
        return False, f"设备 '{device}' 不支持动作 '{action}'"

    # 验证数值参数
    if action in VALUE_REQUIRED_ACTIONS:
        if value is None:
            return False, f"动作 '{action}' 需要提供数值参数"
        # 优先使用按设备区分的范围
        range_key = (device, action)
        if range_key in DEVICE_VALUE_RANGES:
            min_val, max_val = DEVICE_VALUE_RANGES[range_key]
        elif action in VALUE_RANGES:
            min_val, max_val = VALUE_RANGES[action]
        else:
            return True, ""
        if not (min_val <= value <= max_val):
            return False, f"数值必须在 {min_val} 到 {max_val} 之间"

    return True, ""
```

### 2. 错误响应示例

**无效动作**
```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "status": "error",
    "error_code": "INVALID_ACTION",
    "message": "设备 'light' 不支持动作 'play'"
}
```

**数值超出范围**
```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "status": "error",
    "error_code": "INVALID_VALUE",
    "message": "温度值必须在 16 到 30 之间"
}
```

**设备离线**
```json
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{
    "status": "error",
    "error_code": "DEVICE_OFFLINE",
    "message": "空调设备当前离线"
}
```

---

## 示例服务端实现

### Python Flask 实现

```python
#!/usr/bin/env python3
"""
家居控制服务端示例
监听 127.0.0.1:22222，处理家居设备控制请求
"""

from flask import Flask, request, jsonify
from typing import Optional, Dict, Any

app = Flask(__name__)

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

# 模拟设备状态（实际应用中应从硬件读取）
device_states = {
    "light": {"power": False, "brightness": 50},
    "ac": {"power": False, "temperature": 24},
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
    """
    验证请求参数
    返回: (是否有效, 错误代码, 错误消息)
    """
    # 验证动作是否支持
    if action not in DEVICE_ACTIONS.get(device, []):
        return False, "INVALID_ACTION", f"设备 '{device}' 不支持动作 '{action}'"

    # 密码修改特殊验证
    if action == "password":
        if value is None:
            return False, "MISSING_VALUE", "修改密码需要提供新密码"
        pwd = str(value)
        if not pwd.isdigit() or len(pwd) < 4 or len(pwd) > 8:
            return False, "INVALID_VALUE", "密码必须为4-8位数字"
        return True, "", ""

    # 验证数值参数
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
    """
    执行设备控制动作
    实际应用中，这里应该调用真实的硬件控制接口
    """
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
        state["password"] = str(value)
    elif action == "mode":
        state["mode"] = value
    elif action == "speed":
        state["speed"] = value
    elif action == "oscillate":
        state["oscillating"] = bool(value)

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


# === 路由处理 ===

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


def handle_device_request(device: str):
    """通用设备请求处理"""
    # 解析请求
    try:
        data = request.get_json()
        if not data:
            return create_error_response("INVALID_REQUEST", "请求体必须是JSON格式", 400)
    except Exception:
        return create_error_response("INVALID_REQUEST", "无法解析JSON请求体", 400)

    action = data.get("action")
    value = data.get("value")

    # 验证action参数
    if not action:
        return create_error_response("INVALID_ACTION", "缺少 'action' 参数", 400)

    # 验证请求参数
    is_valid, error_code, error_msg = validate_request(device, action, value)
    if not is_valid:
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
            message=action_messages.get(action, "操作成功")
        )
        response["state"] = new_state

        return jsonify(response), 200

    except Exception as e:
        return create_error_response("DEVICE_ERROR", f"设备控制失败: {str(e)}", 500)


# === 健康检查 ===

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
        "version": "2.0.0",
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
    app.run(host='127.0.0.1', port=22222, debug=True)
```

### Python FastAPI 实现（推荐）

```python
#!/usr/bin/env python3
"""
家居控制服务端 - FastAPI 实现
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Home Control Server", version="2.0.0")


# === 请求模型 ===

class ControlRequest(BaseModel):
    action: str
    value: Optional[int | str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str


# === 设备配置 ===

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

device_states = {
    "light": {"power": False, "brightness": 50},
    "ac": {"power": False, "temperature": 24},
    "tv": {"power": False, "volume": 30},
    "speaker": {"power": False, "playing": False, "volume": 20},
    "lock": {"locked": True, "password": "123456"},
    "vacuum": {"power": False, "mode": 1, "battery": 80},
    "purifier": {"power": False, "speed": 1, "pm25": 35},
    "fan": {"power": False, "speed": 1, "oscillating": False},
    "plug": {"power": False},
    "switch": {"power": False},
}


# === 工具函数 ===

def validate_action(device: str, action: str, value):
    """验证动作和参数"""
    if action not in DEVICE_ACTIONS.get(device, []):
        raise HTTPException(
            status_code=400,
            detail={"error_code": "INVALID_ACTION", "message": f"不支持的动作: {action}"}
        )

    if action in VALUE_REQUIRED_ACTIONS and value is None:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "MISSING_VALUE", "message": f"动作 '{action}' 需要数值参数"}
        )

    # 密码特殊验证
    if action == "password" and value is not None:
        pwd = str(value)
        if not pwd.isdigit() or len(pwd) < 4 or len(pwd) > 8:
            raise HTTPException(
                status_code=400,
                detail={"error_code": "INVALID_VALUE", "message": "密码必须为4-8位数字"}
            )
        return

    # 数值范围验证
    if value is not None:
        range_key = (device, action)
        if range_key in DEVICE_VALUE_RANGES:
            min_val, max_val, name = DEVICE_VALUE_RANGES[range_key]
        elif action in VALUE_RANGES:
            min_val, max_val, name = VALUE_RANGES[action]
        else:
            return
        if not (min_val <= value <= max_val):
            raise HTTPException(
                status_code=400,
                detail={"error_code": "INVALID_VALUE", "message": f"{name}值必须在 {min_val}-{max_val} 之间"}
            )


def execute_action(device: str, action: str, value) -> dict:
    """执行设备动作"""
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
        state["password"] = str(value)
    elif action == "mode":
        state["mode"] = value
    elif action == "speed":
        state["speed"] = value
    elif action == "oscillate":
        state["oscillating"] = bool(value)

    return state.copy()


# === 路由 ===

@app.post("/{device}")
async def control_device(device: str, req: ControlRequest):
    """设备控制通用端点"""
    if device not in DEVICE_ACTIONS:
        raise HTTPException(status_code=404, detail=f"未知设备: {device}")

    validate_action(device, req.action, req.value)
    new_state = execute_action(device, req.action, req.value)

    return {
        "status": "ok",
        "device": device,
        "action": req.action,
        "value": req.value,
        "state": new_state
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "devices": list(DEVICE_ACTIONS.keys())}


@app.get("/")
async def root():
    """服务信息"""
    return {
        "service": "Home Control Server",
        "endpoints": {f"/{d}": DEVICE_ACTIONS[d] for d in DEVICE_ACTIONS}
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=22222)
```

---

## 部署说明

### 环境要求

- Python 3.8+
- Flask 或 FastAPI

### 安装依赖

**Flask 版本：**
```bash
pip install flask
```

**FastAPI 版本：**
```bash
pip install fastapi uvicorn
```

### 启动服务

**Flask：**
```bash
python home_server_flask.py
```

**FastAPI：**
```bash
python home_server_fastapi.py
```

### 验证服务

```bash
# 健康检查
curl http://127.0.0.1:22222/health

# 开灯测试
curl -X POST http://127.0.0.1:22222/light \
  -H "Content-Type: application/json" \
  -d '{"action": "on"}'

# 设置亮度测试
curl -X POST http://127.0.0.1:22222/light \
  -H "Content-Type: application/json" \
  -d '{"action": "brightness", "value": 80}'
```

### 与 Skill 配合测试

```bash
# 使用 home-control 技能测试
cd /root/new_skill/home-control
python scripts/home_control.py light on
python scripts/home_control.py 空调 温度 24
python scripts/home_control.py speaker play
python scripts/home_control.py 门锁 开锁
python scripts/home_control.py lock password 654321
python scripts/home_control.py 扫地机器人 模式 2
python scripts/home_control.py purifier speed 3
python scripts/home_control.py 风扇 风速 2
python scripts/home_control.py 插座 开
python scripts/home_control.py switch off
```

---

## 生产环境建议

1. **添加认证**：实现 API Key 或 JWT 认证
2. **日志记录**：记录所有控制操作
3. **设备发现**：支持动态设备注册
4. **状态持久化**：将设备状态保存到数据库
5. **WebSocket**：支持设备状态实时推送
6. **HTTPS**：生产环境建议启用 TLS
