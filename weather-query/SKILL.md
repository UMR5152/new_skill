# Weather Query (weather-query)

## Description

Query weather information including current temperature, weather forecast, air quality, and clothing suggestions. This skill provides comprehensive weather data through various weather APIs.

## Usage

```bash
python scripts/weather_query.py <command> [location] [options]
```

### Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `now` | `当前` | Current weather conditions |
| `forecast` | `预报` | Multi-day weather forecast |
| `air` | `空气` | Air quality index (AQI) |
| `suggest` | `建议` | Clothing and activity suggestions |
| `all` | `全部` | Complete weather report |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--days`, `-d` | Number of forecast days (1-7) | 3 |
| `--mock`, `-m` | Mock mode for testing | false |
| `--format`, `-f` | Output format (text/json) | text |

### Location

Location can be specified as:
- City name in Chinese: `北京`, `上海`, `广州`
- City name in English: `beijing`, `shanghai`
- Coordinates: `39.9,116.4`

If no location specified, defaults to `北京`.

## Examples

```bash
# Current weather
python scripts/weather_query.py now
python scripts/weather_query.py 当前 上海
python scripts/weather_query.py now "New York"

# Weather forecast
python scripts/weather_query.py forecast
python scripts/weather_query.py 预报 广州 --days 5
python scripts/weather_query.py forecast shanghai -d 7

# Air quality
python scripts/weather_query.py air
python scripts/weather_query.py 空气 深圳

# Clothing suggestions
python scripts/weather_query.py suggest
python scripts/weather_query.py 建议 成都

# Complete report
python scripts/weather_query.py all
python scripts/weather_query.py 全部 杭州

# Mock mode (for testing without API)
python scripts/weather_query.py now 北京 --mock
python scripts/weather_query.py -m 预报 上海 -d 3

# JSON output
python scripts/weather_query.py now 北京 --format json
```

## Features

- **Current Weather**: Temperature, humidity, wind, visibility, pressure
- **Weather Forecast**: Up to 7 days forecast with daily details
- **Air Quality**: AQI, PM2.5, PM10, O3, NO2, SO2, CO levels
- **Clothing Suggestions**: Based on temperature and weather conditions
- **Activity Recommendations**: Indoor/outdoor activity suggestions
- **Multi-language Support**: Chinese and English city names

## Weather Data Sources

- Primary: wttr.in API (free, no API key required)
- Fallback: Mock data mode for offline testing

## API Endpoints

By default, the script uses `https://wttr.in` API:

| Endpoint | Description |
|----------|-------------|
| `/{location}?format=j1` | Full weather data in JSON |
| `/{location}?format=3` | Brief weather info |

## Requirements

- Python 3.8+
- `requests` library

## Installation

```bash
pip install requests
```

## Output Examples

### Current Weather (`now`)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           北京 当前天气
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  天气状况: 晴 ☀️
  当前温度: 22°C (体感 20°C)
  最高/最低: 25°C / 15°C

  湿度: 45%
  风速: 12 km/h 东北风
  能见度: 10 km
  气压: 1015 hPa

  紫外线指数: 5 (中等)
  日出/日落: 06:15 / 18:32
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Forecast (`forecast`)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           上海 天气预报 (3天)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 今天 (周三)
   ☀️ 晴
   25°C / 18°C
   湿度: 55%  风速: 10 km/h

📅 明天 (周四)
   ⛅ 多云
   23°C / 17°C
   湿度: 60%  风速: 15 km/h

📅 后天 (周五)
   🌧️ 小雨
   20°C / 15°C
   湿度: 75%  风速: 12 km/h

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Air Quality (`air`)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           深圳 空气质量
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AQI 指数: 68 (良)

  PM2.5: 45 μg/m³
  PM10: 62 μg/m³
  O3: 85 μg/m³
  NO2: 28 μg/m³
  SO2: 8 μg/m³
  CO: 0.8 mg/m³

  建议: 空气质量可接受，户外活动正常进行
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Clothing Suggestions (`suggest`)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         广州 穿衣建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  当前温度: 28°C

  👕 穿衣建议:
     建议穿着短袖、短裤等夏季服装
     可携带薄外套应对室内空调

  🏃 运动建议:
     天气适宜，适合户外运动
     注意防晒和补水

  ☂️ 出行提示:
     无需携带雨具
     紫外线较强，建议涂抹防晒霜
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Workflow

1. Parse command, location, and options from arguments
2. Validate input parameters
3. Fetch weather data from API (or use mock data)
4. Parse and format the response
5. Display weather information or suggestions
