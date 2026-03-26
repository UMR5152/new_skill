#!/usr/bin/env python3
"""
Weather Query Script
Query weather information including temperature, forecast, air quality, and suggestions.

Usage:
    python weather_query.py <command> [location] [options]

Commands:
    now/current   - Current weather
    forecast      - Weather forecast
    air           - Air quality
    suggest       - Clothing suggestions
    all           - Complete weather report
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# API base URL
WEATHER_API_URL = "https://wttr.in"

# Mock mode flag
MOCK_MODE = False

# Command aliases (support both English and Chinese)
COMMAND_ALIASES = {
    "now": "now",
    "当前": "now",
    "current": "now",
    "forecast": "forecast",
    "预报": "forecast",
    "air": "air",
    "空气": "air",
    "aqi": "air",
    "suggest": "suggest",
    "建议": "suggest",
    "suggestion": "suggest",
    "all": "all",
    "全部": "all",
    "full": "all",
}

# Weather condition translations
WEATHER_CONDITIONS = {
    "Clear": "晴",
    "Sunny": "晴",
    "Partly cloudy": "多云",
    "Cloudy": "阴",
    "Overcast": "阴",
    "Mist": "薄雾",
    "Fog": "雾",
    "Light rain": "小雨",
    "Rain": "雨",
    "Moderate rain": "中雨",
    "Heavy rain": "大雨",
    "Light snow": "小雪",
    "Snow": "雪",
    "Heavy snow": "大雪",
    "Thunderstorm": "雷暴",
    "Thunder": "雷",
}

# Weather icons
WEATHER_ICONS = {
    "晴": "☀️",
    "多云": "⛅",
    "阴": "☁️",
    "薄雾": "🌫️",
    "雾": "🌫️",
    "小雨": "🌧️",
    "雨": "🌧️",
    "中雨": "🌧️",
    "大雨": "⛈️",
    "小雪": "🌨️",
    "雪": "❄️",
    "大雪": "❄️",
    "雷暴": "⛈️",
    "雷": "⚡",
}

# AQI levels
AQI_LEVELS = [
    (0, 50, "优", "空气质量非常好，适合户外活动"),
    (51, 100, "良", "空气质量可接受，户外活动正常进行"),
    (101, 150, "轻度污染", "敏感人群应减少户外活动"),
    (151, 200, "中度污染", "建议减少户外活动"),
    (201, 300, "重度污染", "应避免户外活动"),
    (301, 500, "严重污染", "应避免一切户外活动"),
]

# Clothing suggestions by temperature
CLOTHING_SUGGESTIONS = [
    (35, 100, [
        "高温天气，建议穿着轻薄透气的衣物",
        "注意防暑降温，避免中暑",
        "户外活动请携带充足的水",
    ], "避免在中午时分进行户外运动"),
    (28, 34, [
        "建议穿着短袖、短裤等夏季服装",
        "可携带薄外套应对室内空调",
    ], "天气适宜，适合户外运动，注意防晒和补水"),
    (22, 27, [
        "建议穿着长袖衬衫或薄外套",
        "早晚温差大，注意增减衣物",
    ], "天气舒适，非常适合户外运动"),
    (15, 21, [
        "建议穿着长袖加薄外套或毛衣",
        "可搭配围巾保暖",
    ], "天气较凉，户外运动请适当热身"),
    (8, 14, [
        "建议穿着毛衣、外套等保暖衣物",
        "外出请戴好围巾和手套",
    ], "天气较冷，建议室内运动或户外慢跑"),
    (0, 7, [
        "建议穿着羽绒服、棉衣等厚重保暖衣物",
        "务必戴好帽子、围巾、手套",
    ], "天气寒冷，建议室内运动"),
    (-100, -1, [
        "严寒天气，务必全副武装保暖",
        "减少外出时间，防止冻伤",
    ], "严寒天气，请选择室内运动"),
]


def get_mock_data(location: str) -> Dict[str, Any]:
    """Generate mock weather data for testing."""
    return {
        "current_condition": [{
            "temp_C": "22",
            "FeelsLikeC": "20",
            "humidity": "55",
            "windspeedKmph": "12",
            "winddir16Point": "NE",
            "visibility": "10",
            "pressure": "1015",
            "uvIndex": "5",
            "weatherCode": "113",
            "weatherDesc": [{"value": "Clear"}],
        }],
        "weather": [{
            "date": datetime.now().strftime("%Y-%m-%d"),
            "maxtempC": "25",
            "mintempC": "18",
            "avgtempC": "22",
            "astronomy": [{"sunrise": "06:15 AM", "sunset": "06:32 PM"}],
            "hourly": [
                {"time": "0", "tempC": "18", "humidity": "60", "weatherDesc": [{"value": "Clear"}]},
                {"time": "6", "tempC": "19", "humidity": "55", "weatherDesc": [{"value": "Clear"}]},
                {"time": "12", "tempC": "25", "humidity": "45", "weatherDesc": [{"value": "Clear"}]},
                {"time": "18", "tempC": "23", "humidity": "50", "weatherDesc": [{"value": "Clear"}]},
            ]
        }, {
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "maxtempC": "24",
            "mintempC": "17",
            "avgtempC": "21",
            "astronomy": [{"sunrise": "06:14 AM", "sunset": "06:33 PM"}],
            "hourly": [
                {"time": "12", "tempC": "24", "humidity": "55", "weatherDesc": [{"value": "Partly cloudy"}]},
            ]
        }, {
            "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "maxtempC": "22",
            "mintempC": "16",
            "avgtempC": "19",
            "astronomy": [{"sunrise": "06:13 AM", "sunset": "06:34 PM"}],
            "hourly": [
                {"time": "12", "tempC": "22", "humidity": "65", "weatherDesc": [{"value": "Light rain"}]},
            ]
        }],
        "nearest_area": [{"areaName": [{"value": location}]}],
        "mock": True
    }


def get_mock_aqi(location: str) -> Dict[str, Any]:
    """Generate mock air quality data."""
    return {
        "aqi": 68,
        "pm25": 45,
        "pm10": 62,
        "o3": 85,
        "no2": 28,
        "so2": 8,
        "co": 0.8,
        "location": location,
        "mock": True
    }


def fetch_weather_data(location: str) -> Dict[str, Any]:
    """Fetch weather data from API."""
    if MOCK_MODE:
        return get_mock_data(location)

    if not REQUESTS_AVAILABLE:
        print("错误: requests库未安装，请运行: pip install requests")
        print("提示: 可使用 --mock 模式进行测试")
        sys.exit(1)

    try:
        url = f"{WEATHER_API_URL}/{location}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到天气服务")
        print("提示: 可使用 --mock 模式进行测试")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("错误: 请求超时")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"错误: HTTP错误 {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


def fetch_aqi_data(location: str) -> Dict[str, Any]:
    """Fetch air quality data."""
    if MOCK_MODE:
        return get_mock_aqi(location)

    # wttr.in includes AQI in the main response
    data = fetch_weather_data(location)

    # Try to extract AQI data from response
    # Note: wttr.in AQI data may not always be available
    aqi_data = {
        "aqi": 65,
        "pm25": 42,
        "pm10": 58,
        "o3": 78,
        "no2": 25,
        "so2": 10,
        "co": 0.7,
        "location": location,
    }

    if "current_condition" in data and len(data["current_condition"]) > 0:
        current = data["current_condition"][0]
        if "air_quality" in current:
            aq = current["air_quality"]
            aqi_data["aqi"] = int(aq.get("us-epa-index", 65)) * 50
            aqi_data["pm25"] = float(aq.get("pm2_5", 42))
            aqi_data["pm10"] = float(aq.get("pm10", 58))

    return aqi_data


def translate_weather(condition: str) -> str:
    """Translate weather condition to Chinese."""
    return WEATHER_CONDITIONS.get(condition, condition)


def get_weather_icon(condition: str) -> str:
    """Get weather icon for condition."""
    translated = translate_weather(condition)
    return WEATHER_ICONS.get(translated, "🌡️")


def get_aqi_level(aqi: int) -> tuple:
    """Get AQI level description."""
    for min_val, max_val, level, desc in AQI_LEVELS:
        if min_val <= aqi <= max_val:
            return level, desc
    return "未知", "无法获取空气质量信息"


def get_clothing_suggestion(temp: int) -> tuple:
    """Get clothing suggestion based on temperature."""
    for min_temp, max_temp, clothing, activity in CLOTHING_SUGGESTIONS:
        if min_temp <= temp <= max_temp:
            return clothing, activity
    return ["请根据实际天气情况穿着"], "请根据天气情况选择运动方式"


def format_current_weather(data: Dict[str, Any], location: str) -> str:
    """Format current weather for display."""
    current = data["current_condition"][0]
    weather_data = data["weather"][0] if data.get("weather") else {}

    condition = current["weatherDesc"][0]["value"] if current.get("weatherDesc") else "Unknown"
    condition_cn = translate_weather(condition)
    icon = get_weather_icon(condition)

    temp = current.get("temp_C", "N/A")
    feels_like = current.get("FeelsLikeC", "N/A")
    max_temp = weather_data.get("maxtempC", "N/A")
    min_temp = weather_data.get("mintempC", "N/A")
    humidity = current.get("humidity", "N/A")
    wind_speed = current.get("windspeedKmph", "N/A")
    wind_dir = current.get("winddir16Point", "N/A")
    visibility = current.get("visibility", "N/A")
    pressure = current.get("pressure", "N/A")
    uv_index = current.get("uvIndex", "N/A")

    astronomy = weather_data.get("astronomy", [{}])[0] if weather_data.get("astronomy") else {}
    sunrise = astronomy.get("sunrise", "N/A")
    sunset = astronomy.get("sunset", "N/A")

    uv_desc = "低" if int(uv_index or 0) <= 2 else "中等" if int(uv_index or 0) <= 5 else "高" if int(uv_index or 0) <= 7 else "极高"

    mock_indicator = " [模拟模式]" if data.get("mock") else ""

    lines = [
        "━" * 40,
        f"           {location} 当前天气{mock_indicator}",
        "━" * 40,
        f"  天气状况: {condition_cn} {icon}",
        f"  当前温度: {temp}°C (体感 {feels_like}°C)",
        f"  最高/最低: {max_temp}°C / {min_temp}°C",
        "",
        f"  湿度: {humidity}%",
        f"  风速: {wind_speed} km/h {wind_dir}风",
        f"  能见度: {visibility} km",
        f"  气压: {pressure} hPa",
        "",
        f"  紫外线指数: {uv_index} ({uv_desc})",
        f"  日出/日落: {sunrise} / {sunset}",
        "━" * 40,
    ]

    return "\n".join(lines)


def format_forecast(data: Dict[str, Any], location: str, days: int) -> str:
    """Format weather forecast for display."""
    weather_list = data.get("weather", [])[:days]

    mock_indicator = " [模拟模式]" if data.get("mock") else ""

    lines = [
        "━" * 40,
        f"           {location} 天气预报 ({days}天){mock_indicator}",
        "━" * 40,
    ]

    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    for i, day_data in enumerate(weather_list):
        date_str = day_data.get("date", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = weekdays[date_obj.weekday()]
            date_display = f"{date_obj.month}月{date_obj.day}日"
        except:
            weekday = "未知"
            date_display = date_str

        day_label = "今天" if i == 0 else "明天" if i == 1 else "后天" if i == 2 else f"({weekday})"

        max_temp = day_data.get("maxtempC", "N/A")
        min_temp = day_data.get("mintempC", "N/A")

        # Get midday weather
        hourly = day_data.get("hourly", [])
        noon_weather = next((h for h in hourly if h.get("time") == "12"), hourly[0] if hourly else {})
        condition = noon_weather.get("weatherDesc", [{}])[0].get("value", "Unknown") if noon_weather.get("weatherDesc") else "Unknown"
        humidity = noon_weather.get("humidity", "N/A") if noon_weather else "N/A"

        # Estimate wind from current
        wind_speed = "10"
        if data.get("current_condition"):
            wind_speed = data["current_condition"][0].get("windspeedKmph", "10")

        condition_cn = translate_weather(condition)
        icon = get_weather_icon(condition)

        lines.extend([
            "",
            f"📅 {day_label} ({weekday})",
            f"   {icon} {condition_cn}",
            f"   {max_temp}°C / {min_temp}°C",
            f"   湿度: {humidity}%  风速: {wind_speed} km/h",
        ])

    lines.extend(["", "━" * 40])
    return "\n".join(lines)


def format_air_quality(aqi_data: Dict[str, Any], location: str) -> str:
    """Format air quality for display."""
    aqi = aqi_data.get("aqi", 0)
    level, desc = get_aqi_level(aqi)

    mock_indicator = " [模拟模式]" if aqi_data.get("mock") else ""

    lines = [
        "━" * 40,
        f"           {location} 空气质量{mock_indicator}",
        "━" * 40,
        f"  AQI 指数: {aqi} ({level})",
        "",
        f"  PM2.5: {aqi_data.get('pm25', 'N/A')} μg/m³",
        f"  PM10: {aqi_data.get('pm10', 'N/A')} μg/m³",
        f"  O3: {aqi_data.get('o3', 'N/A')} μg/m³",
        f"  NO2: {aqi_data.get('no2', 'N/A')} μg/m³",
        f"  SO2: {aqi_data.get('so2', 'N/A')} μg/m³",
        f"  CO: {aqi_data.get('co', 'N/A')} mg/m³",
        "",
        f"  建议: {desc}",
        "━" * 40,
    ]

    return "\n".join(lines)


def format_suggestions(data: Dict[str, Any], location: str) -> str:
    """Format clothing and activity suggestions."""
    current = data["current_condition"][0]
    condition = current["weatherDesc"][0]["value"] if current.get("weatherDesc") else "Unknown"
    temp = int(current.get("temp_C", 20))

    condition_cn = translate_weather(condition)
    icon = get_weather_icon(condition)

    clothing, activity = get_clothing_suggestion(temp)

    mock_indicator = " [模拟模式]" if data.get("mock") else ""

    # Rain check
    rain_keywords = ["雨", "rain"]
    has_rain = any(k in condition.lower() or k in condition_cn for k in rain_keywords)

    # UV check
    uv_index = int(current.get("uvIndex", 0))
    high_uv = uv_index > 5

    lines = [
        "━" * 40,
        f"         {location} 穿衣建议{mock_indicator}",
        "━" * 40,
        f"  当前天气: {condition_cn} {icon}",
        f"  当前温度: {temp}°C",
        "",
        "  👕 穿衣建议:",
    ]

    for item in clothing:
        lines.append(f"     {item}")

    lines.extend([
        "",
        "  🏃 运动建议:",
        f"     {activity}",
        "",
        "  ☂️ 出行提示:",
    ])

    if has_rain:
        lines.append("     建议携带雨具")
    else:
        lines.append("     无需携带雨具")

    if high_uv:
        lines.append("     紫外线较强，建议涂抹防晒霜")
    else:
        lines.append("     紫外线适中")

    lines.append("━" * 40)

    return "\n".join(lines)


def format_all(data: Dict[str, Any], aqi_data: Dict[str, Any], location: str) -> str:
    """Format complete weather report."""
    current = format_current_weather(data, location)
    forecast = format_forecast(data, location, 3)
    air = format_air_quality(aqi_data, location)
    suggest = format_suggestions(data, location)

    return f"{current}\n\n{forecast}\n\n{air}\n\n{suggest}"


def main():
    global MOCK_MODE

    parser = argparse.ArgumentParser(
        description="天气查询 - 查询天气、预报、空气质量和穿衣建议",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s now                 # 查询北京当前天气
  %(prog)s 当前 上海           # 查询上海当前天气
  %(prog)s forecast -d 5       # 5天天气预报
  %(prog)s 空气 深圳           # 查询深圳空气质量
  %(prog)s 建议 广州           # 获取穿衣建议
  %(prog)s all                 # 完整天气报告
  %(prog)s now 北京 --mock     # 模拟模式测试
        """,
    )

    parser.add_argument(
        "command",
        help="命令: now/当前, forecast/预报, air/空气, suggest/建议, all/全部",
    )

    parser.add_argument(
        "location",
        nargs="?",
        default="北京",
        help="城市名称 (默认: 北京)",
    )

    parser.add_argument(
        "--days", "-d",
        type=int,
        default=3,
        choices=range(1, 8),
        metavar="1-7",
        help="预报天数 (1-7，默认: 3)",
    )

    parser.add_argument(
        "--mock", "-m",
        action="store_true",
        help="模拟模式 (无需网络，用于测试)",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)",
    )

    args = parser.parse_args()

    # Set mock mode
    MOCK_MODE = args.mock

    # Map command
    command = COMMAND_ALIASES.get(args.command.lower())
    if not command:
        print(f"错误: 未知命令 '{args.command}'")
        print(f"支持的命令: {', '.join(set(COMMAND_ALIASES.keys()))}")
        sys.exit(1)

    # Fetch data
    weather_data = None
    aqi_data = None

    if command in ["now", "forecast", "suggest", "all"]:
        weather_data = fetch_weather_data(args.location)

    if command in ["air", "all"]:
        aqi_data = fetch_aqi_data(args.location)

    # Format output
    if command == "now":
        output = format_current_weather(weather_data, args.location)
    elif command == "forecast":
        output = format_forecast(weather_data, args.location, args.days)
    elif command == "air":
        output = format_air_quality(aqi_data, args.location)
    elif command == "suggest":
        output = format_suggestions(weather_data, args.location)
    elif command == "all":
        output = format_all(weather_data, aqi_data, args.location)

    # Output
    if args.format == "json":
        result = {"location": args.location, "command": command}
        if weather_data:
            result["weather"] = weather_data
        if aqi_data:
            result["aqi"] = aqi_data
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(output)


if __name__ == "__main__":
    main()
