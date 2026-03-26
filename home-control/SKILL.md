# Home Control (home-control)

## Description

Control smart home devices including lights, air conditioner, TV, and speakers. This skill provides a unified interface to manage all your home automation devices through HTTP requests.

## Usage

```bash
python scripts/home_control.py <device> <action> [value] [--mock]
```

### Options

| Option | Description |
|--------|-------------|
| `--mock`, `-m` | 模拟模式，无需服务器即可测试 |

### Devices

| Device | Alias | Description |
|--------|-------|-------------|
| `light` | `灯` | Control room lights |
| `ac` | `空调` | Control air conditioner |
| `tv` | `电视` | Control television |
| `speaker` | `音箱` | Control audio speaker |

### Actions

#### Light (灯)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the light | - |
| `off` / `关` | Turn off the light | - |
| `brightness` / `亮度` | Set brightness level | 0-100 |

#### Air Conditioner (空调)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the AC | - |
| `off` / `关` | Turn off the AC | - |
| `temperature` / `温度` | Set temperature | 16-30 (°C) |

#### TV (电视)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the TV | - |
| `off` / `关` | Turn off the TV | - |
| `volume` / `音量` | Set volume level | 0-100 |

#### Speaker (音箱)
| Action | Description | Value Range |
|--------|-------------|-------------|
| `on` / `开` | Turn on the speaker | - |
| `off` / `关` | Turn off the speaker | - |
| `play` / `播放` | Start playback | - |
| `volume` / `音量` | Set volume level | 0-100 |

## Examples

```bash
# Turn on the light
python scripts/home_control.py light on
python scripts/home_control.py 灯 开

# Set light brightness to 80%
python scripts/home_control.py light brightness 80
python scripts/home_control.py 灯 亮度 80

# Turn off the light
python scripts/home_control.py light off
python scripts/home_control.py 灯 关

# Turn on air conditioner
python scripts/home_control.py ac on
python scripts/home_control.py 空调 开

# Set AC temperature to 24°C
python scripts/home_control.py ac temperature 24
python scripts/home_control.py 空调 温度 24

# Turn on TV
python scripts/home_control.py tv on
python scripts/home_control.py 电视 开

# Set TV volume to 50
python scripts/home_control.py tv volume 50
python scripts/home_control.py 电视 音量 50

# Turn on speaker
python scripts/home_control.py speaker on
python scripts/home_control.py 音箱 开

# Start playback on speaker
python scripts/home_control.py speaker play
python scripts/home_control.py 音箱 播放

# Set speaker volume to 30
python scripts/home_control.py speaker volume 30
python scripts/home_control.py 音箱 音量 30

# Mock mode (for testing without server)
python scripts/home_control.py --mock light on
python scripts/home_control.py -m 灯 亮度 50
```

## API Endpoints

All requests are sent to `http://127.0.0.1:22222/` with the following endpoints:

| Device | Endpoint | Method | Parameters |
|--------|----------|--------|------------|
| Light | `/light` | POST | `action`: on/off/brightness, `value`: 0-100 (for brightness) |
| AC | `/ac` | POST | `action`: on/off/temperature, `value`: 16-30 (for temperature) |
| TV | `/tv` | POST | `action`: on/off/volume, `value`: 0-100 (for volume) |
| Speaker | `/speaker` | POST | `action`: on/off/play/volume, `value`: 0-100 (for volume) |

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

### Detailed Documentation

See [docs/SERVER_DEPLOYMENT.md](docs/SERVER_DEPLOYMENT.md) for:
- Complete API specification
- Request/Response format
- Error handling
- Production deployment guide
- Flask and FastAPI example implementations
