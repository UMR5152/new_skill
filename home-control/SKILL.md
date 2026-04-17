---
name: home-control
description: Control smart home devices including lights, air conditioner, TV, speakers, smart lock, robot vacuum, air purifier, fan, smart plug, smart switch, curtain, and humidifier. This skill provides a unified interface to manage all your home automation devices through HTTP requests. Use when the user asks to control smart home devices such as turning on/off lights, adjusting AC temperature, controlling TV/speaker volume, locking/unlocking doors, starting robot vacuum, controlling curtains, managing humidifiers, or any other home automation tasks.
---

# Home Control (home-control)

## Usage

```bash
python scripts/home_control.py <device> <action> [value] [--mock]
```

### Options

| Option | Description |
|--------|-------------|
| `--mock`, `-m` | 模拟模式，无需服务器即可测试 |
| `--save-request` | 保存原始HTTP请求到指定文件 |
| `--room` | 设备所在房间 (用于添加设备) |

### Devices

| Device | Alias | Description |
|--------|-------|-------------|
| `light` | `灯` / `灯光` / `智能灯光` | Control room lights |
| `ac` | `空调` | Control air conditioner |
| `tv` | `电视` / `电视机` | Control television |
| `speaker` | `音箱` | Control audio speaker |
| `lock` | `门锁` / `智能门锁` | Control smart door lock |
| `vacuum` | `扫地机器人` / `扫地机` | Control robot vacuum |
| `purifier` | `空气净化器` / `净化器` | Control air purifier |
| `fan` | `风扇` | Control fan |
| `plug` | `插座` / `智能插座` | Control smart plug |
| `switch` | `开关` / `智能开关` | Control smart switch |
| `curtain` | `窗帘` / `窗帘电机` | Control curtain motor |
| `humidifier` | `加湿器` | Control humidifier |
| `device_list` | `设备列表` / `查询设备` / `查看设备` | Get device list |
| `device_add` | `添加设备` | Add new device |

### Actions

#### Light (灯)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the light | - |
| `off` / `关` | Turn off the light | - |
| `brightness` / `亮度` | Set brightness level | 0-100 |
| `color` / `色彩` / `色调` | Set light color | warm/cool/natural (暖光/白光/自然光) |
| `scene` / `场景` | Switch light scene | cozy/reading/romantic (温馨/阅读/浪漫) |

#### Air Conditioner (空调)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the AC | - |
| `off` / `关` | Turn off the AC | - |
| `temperature` / `温度` | Set temperature | 16-30 (°C) |
| `mode` / `模式` | Set AC mode | cool/heat/dehumidify/fan/auto (制冷/制热/除湿/送风/自动) |
| `preset` / `预设` | Set preset mode | sleep/silent/eco (睡眠/静音/节能) |
| `fanspeed` / `空调风速` | Set fan speed | 1-4 (档位) |

#### TV (电视)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the TV | - |
| `off` / `关` | Turn off the TV | - |
| `volume` / `音量` | Set volume level | 0-100 |
| `source` / `信号源` | Switch input source | HDMI1/HDMI2/AV/TV/USB |
| `status` / `状态` / `查询状态` | Query TV status | - |

#### Speaker (音箱)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the speaker | - |
| `off` / `关` | Turn off the speaker | - |
| `play` / `播放` | Start playback | - |
| `volume` / `音量` | Set volume level | 0-100 |

#### Smart Lock (智能门锁)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `unlock` / `开锁` | Unlock the door | - |
| `lock` / `关锁` / `上锁` | Lock the door | - |
| `password` / `密码` | Change lock password | 4-8 digit number |

#### Robot Vacuum (扫地机器人)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` / `打扫` / `清扫` | Start cleaning | - |
| `off` / `关` / `停止` | Stop cleaning | - |
| `mode` / `模式` | Set cleaning mode | 1=sweep, 2=mop, 3=sweep+mop |
| `pause` / `暂停` | Pause cleaning | - |
| `dock` / `回充` / `充电` | Return to charging dock | - |
| `locate` / `定位` / `位置` | Query vacuum location | - |

#### Air Purifier (空气净化器)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the purifier | - |
| `off` / `关` | Turn off the purifier | - |
| `speed` / `风速` / `档位` | Set fan speed | 1-5 |
| `ion` / `负离子` | Control ionizer | 0=off, 1=on |
| `uv` / `uv灯` | Control UV light | 0=off, 1=on |

#### Fan (风扇)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the fan | - |
| `off` / `关` | Turn off the fan | - |
| `speed` / `风速` / `档位` | Set fan speed | 1-3 |
| `oscillate` / `摇头` | Set oscillation | 0=off, 1=on |
| `oscillate_angle` / `摇头角度` | Set oscillation angle | 30-90 (度) |
| `fan_mode` / `风扇模式` | Set fan mode | natural/sleep/smart/normal (自然风/睡眠风/智能风/正常风) |

#### Smart Plug (智能插座)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the plug | - |
| `off` / `关` | Turn off the plug | - |

#### Smart Switch (智能开关)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the switch | - |
| `off` / `关` | Turn off the switch | - |

#### Curtain (窗帘)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` / `打开` | Open curtain fully | - |
| `off` / `关` / `关闭` | Close curtain fully | - |
| `pause` / `暂停` | Pause curtain movement | - |
| `position` / `位置` / `打开多少` | Set curtain position | 0-100 (%) |
| `schedule` / `定时` | Set scheduled operation | 0=off, 1=on |

#### Humidifier (加湿器)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the humidifier | - |
| `off` / `关` | Turn off the humidifier | - |
| `mode` / `模式` | Set humidifier mode | strong/sleep/auto (强劲/睡眠/自动) |
| `humidity` / `湿度` | Set target humidity | 30-90 (%) |
| `filter_level` / `过滤等级` / `过滤` | Set filter level | 1-5 (级) |

#### Device Management
| Action | Description | Usage |
|--------|-------------|-------|
| `device_list` / `设备列表` / `查询设备` / `查看设备` | Get all registered devices | `python scripts/home_control.py device_list` |
| `device_add` / `添加设备` | Add new device | `python scripts/home_control.py device_add <设备类型> <设备名称> [--room 房间]` |

## Examples

### Basic Controls

```bash
# Light
python scripts/home_control.py light on
python scripts/home_control.py 灯 开
python scripts/home_control.py light brightness 80
python scripts/home_control.py 灯 亮度 80
python scripts/home_control.py light color warm
python scripts/home_control.py 灯 光色 暖光
python scripts/home_control.py light scene cozy
python scripts/home_control.py 灯 场景 温馨

# Air Conditioner
python scripts/home_control.py ac on
python scripts/home_control.py 空调 开
python scripts/home_control.py ac temperature 24
python scripts/home_control.py 空调 温度 24
python scripts/home_control.py ac mode cool
python scripts/home_control.py 空调 制冷
python scripts/home_control.py ac preset sleep
python scripts/home_control.py 空调 预设 睡眠
python scripts/home_control.py ac fanspeed 3
python scripts/home_control.py 空调 风速 3

# TV
python scripts/home_control.py tv on
python scripts/home_control.py 电视 开
python scripts/home_control.py tv volume 50
python scripts/home_control.py 电视 音量 50
python scripts/home_control.py tv source HDMI1
python scripts/home_control.py 电视 信号源 HDMI1
python scripts/home_control.py tv status
python scripts/home_control.py 电视 状态

# Speaker
python scripts/home_control.py speaker on
python scripts/home_control.py 音箱 开
python scripts/home_control.py speaker play
python scripts/home_control.py 音箱 播放
python scripts/home_control.py speaker volume 30
python scripts/home_control.py 音箱 音量 30

# Smart Lock
python scripts/home_control.py lock unlock
python scripts/home_control.py 门锁 开锁
python scripts/home_control.py lock lock
python scripts/home_control.py 门锁 关锁
python scripts/home_control.py lock password 654321
python scripts/home_control.py 门锁 密码 654321
```

### Robot Vacuum

```bash
# Start cleaning
python scripts/home_control.py vacuum on
python scripts/home_control.py 扫地机器人 开
python scripts/home_control.py vacuum mode 2
python scripts/home_control.py 扫地机器人 模式 2

# Pause and dock
python scripts/home_control.py vacuum pause
python scripts/home_control.py 扫地机器人 暂停
python scripts/home_control.py vacuum dock
python scripts/home_control.py 扫地机器人 回充

# Locate
python scripts/home_control.py vacuum locate
python scripts/home_control.py 扫地机器人 定位
```

### Air Purifier

```bash
# Basic controls
python scripts/home_control.py purifier on
python scripts/home_control.py 净化器 开
python scripts/home_control.py purifier speed 3
python scripts/home_control.py 净化器 风速 3

# Advanced features
python scripts/home_control.py purifier ion 1
python scripts/home_control.py 净化器 负离子 1
python scripts/home_control.py purifier uv 1
python scripts/home_control.py 净化器 uv 1
```

### Fan

```bash
# Basic controls
python scripts/home_control.py fan on
python scripts/home_control.py 风扇 开
python scripts/home_control.py fan speed 2
python scripts/home_control.py 风扇 风速 2

# Oscillation
python scripts/home_control.py fan oscillate 1
python scripts/home_control.py 风扇 摇头 1
python scripts/home_control.py fan oscillate_angle 60
python scripts/home_control.py 风扇 摇头角度 60

# Fan modes
python scripts/home_control.py fan fan_mode natural
python scripts/home_control.py 风扇 自然风
python scripts/home_control.py fan fan_mode sleep
python scripts/home_control.py 风扇 睡眠风
```

### Curtain

```bash
# Open/Close
python scripts/home_control.py curtain on
python scripts/home_control.py 窗帘 打开
python scripts/home_control.py curtain off
python scripts/home_control.py 窗帘 关闭

# Position control
python scripts/home_control.py curtain position 50
python scripts/home_control.py 窗帘 位置 50

# Pause
python scripts/home_control.py curtain pause
python scripts/home_control.py 窗帘 暂停
```

### Humidifier

```bash
# Basic controls
python scripts/home_control.py humidifier on
python scripts/home_control.py 加湿器 开
python scripts/home_control.py humidifier humidity 60
python scripts/home_control.py 加湿器 湿度 60

# Mode and filter
python scripts/home_control.py humidifier mode strong
python scripts/home_control.py 加湿器 模式 强劲
python scripts/home_control.py humidifier filter_level 4
python scripts/home_control.py 加湿器 过滤等级 4
```

### Smart Plug and Switch

```bash
# Smart Plug
python scripts/home_control.py plug on
python scripts/home_control.py 插座 开
python scripts/home_control.py plug off
python scripts/home_control.py 插座 关

# Smart Switch
python scripts/home_control.py switch on
python scripts/home_control.py 开关 开
python scripts/home_control.py switch off
python scripts/home_control.py 开关 关
```

### Device Management

```bash
# Get device list
python scripts/home_control.py device_list
python scripts/home_control.py 设备列表
python scripts/home_control.py 查询设备

# Add new device
python scripts/home_control.py device_add light 卧室灯
python scripts/home_control.py device_add light 书房灯 --room 书房
python scripts/home_control.py 添加设备 ac 客厅空调 客厅
```

### Mock Mode (Testing)

```bash
# Test without server
python scripts/home_control.py --mock light on
python scripts/home_control.py -m 灯 亮度 50
python scripts/home_control.py --mock device_list
```

### Save HTTP Request

```bash
# Save raw HTTP request to file
python scripts/home_control.py light on --save-request /tmp/light_on.txt
```

## API Endpoints

All requests are sent to `http://127.0.0.1:22222/` with the following endpoints:

| Device | Endpoint | Method | Parameters |
|--------|----------|--------|------------|
| Light | `/light` | POST | `action`: on/off/brightness/color/scene, `value`: varies |
| AC | `/ac` | POST | `action`: on/off/temperature/mode/preset/fanspeed, `value`: varies |
| TV | `/tv` | POST | `action`: on/off/volume/source/status, `value`: varies |
| Speaker | `/speaker` | POST | `action`: on/off/play/volume, `value`: varies |
| Smart Lock | `/lock` | POST | `action`: unlock/lock/password, `value`: varies |
| Robot Vacuum | `/vacuum` | POST | `action`: on/off/mode/pause/dock/locate, `value`: varies |
| Air Purifier | `/purifier` | POST | `action`: on/off/speed/ion/uv, `value`: varies |
| Fan | `/fan` | POST | `action`: on/off/speed/oscillate/oscillate_angle/fan_mode, `value`: varies |
| Smart Plug | `/plug` | POST | `action`: on/off |
| Smart Switch | `/switch` | POST | `action`: on/off |
| Curtain | `/curtain` | POST | `action`: on/off/pause/position/schedule, `value`: varies |
| Humidifier | `/humidifier` | POST | `action`: on/off/mode/humidity/filter_level, `value`: varies |
| Device List | `/device_list` | GET | - |
| Add Device | `/device_add` | POST | `type`, `name`, `room` (optional) |

## Request/Response Format

### Example Request

```json
{
  "action": "on",
  "value": 80
}
```

### Example Success Response

```json
{
  "status": "ok",
  "device": "light",
  "action": "brightness",
  "value": 80,
  "message": "亮度已设置为 80%",
  "state": {
    "power": true,
    "brightness": 80,
    "color": "warm",
    "scene": "cozy"
  }
}
```

### Example Error Response

```json
{
  "status": "error",
  "error_code": "INVALID_VALUE",
  "message": "亮度值必须在 0 到 100 之间"
}
```

## Requirements

- Python 3.8+
- `requests` library

## Installation

```bash
pip install requests
```

## Workflow

1. Parse device, action, and value from command line arguments
2. Map aliases to standard device/action names
3. Validate input parameters
4. Send HTTP POST request to the appropriate endpoint
5. Return the response status

## Server Deployment

To use this skill, you need to run a home control server at `http://127.0.0.1:22222/`.

### Quick Start

```bash
# Start the example server (requires flask)
pip install flask
python scripts/home_server.py
```

### Extended Server

For full feature support (curtains, humidifiers, device management, etc.), use the extended server:

```bash
python scripts/home_server_extended.py
```

### Detailed Documentation

See [docs/SERVER_DEPLOYMENT.md](docs/SERVER_DEPLOYMENT.md) for:
- Complete API specification
- Request/Response format
- Error handling
- Production deployment guide
- Flask and FastAPI example implementations

## Supported Features by Device

### Lighting (智能灯光)
- ✅ On/Off control
- ✅ Brightness adjustment (0-100%)
- ✅ Color temperature (warm/cool/natural)
- ✅ Scene modes (cozy/reading/romantic)

### Air Conditioner (空调)
- ✅ On/Off control
- ✅ Temperature control (16-30°C)
- ✅ Mode selection (cool/heat/dehumidify/fan/auto)
- ✅ Preset modes (sleep/silent/eco)
- ✅ Fan speed control (1-4)

### Television (电视)
- ✅ On/Off control
- ✅ Volume control (0-100)
- ✅ Input source switching (HDMI1/HDMI2/AV/TV/USB)
- ✅ Status query

### Speaker (音箱)
- ✅ On/Off control
- ✅ Play/Pause control
- ✅ Volume control (0-100)

### Smart Lock (智能门锁)
- ✅ Lock/Unlock control
- ✅ Password change (4-8 digits)

### Robot Vacuum (扫地机器人)
- ✅ Start/Stop cleaning
- ✅ Cleaning mode selection (sweep/mop/sweep+mop)
- ✅ Pause cleaning
- ✅ Return to dock
- ✅ Location query

### Air Purifier (空气净化器)
- ✅ On/Off control
- ✅ Fan speed control (1-5)
- ✅ Ionizer control
- ✅ UV light control

### Fan (风扇)
- ✅ On/Off control
- ✅ Fan speed control (1-3)
- ✅ Oscillation control
- ✅ Oscillation angle (30-90°)
- ✅ Fan mode (natural/sleep/smart/normal)

### Smart Plug (智能插座)
- ✅ On/Off control

### Smart Switch (智能开关)
- ✅ On/Off control

### Curtain (窗帘)
- ✅ Open/Close control
- ✅ Position control (0-100%)
- ✅ Pause movement
- ✅ Schedule control

### Humidifier (加湿器)
- ✅ On/Off control
- ✅ Mode selection (strong/sleep/auto)
- ✅ Humidity control (30-90%)
- ✅ Filter level control (1-5)

### Device Management (设备管理)
- ✅ List all devices
- ✅ Add new devices
